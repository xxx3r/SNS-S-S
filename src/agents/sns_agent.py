"""Role-aware SNS node with explicit electrical and thermal bookkeeping."""

from __future__ import annotations

import enum
import math
from dataclasses import dataclass

from src.utils.math_utils import clamp


class AgentMode(str, enum.Enum):
    """Operating modes available to an SNS node."""

    HARVEST = "HARVEST"
    IDLE = "IDLE"
    COMM_BEAM = "COMM_BEAM"
    MOVE = "MOVE"
    SCOUT = "SCOUT"
    SLEEP = "SLEEP"
    REFLECT = "REFLECT"


class AgentRole(str, enum.Enum):
    """Mission specialization of a node."""

    SCOUT = "scout"
    RELAY = "relay"
    STORAGE = "storage"
    SENSOR = "sensor"


class HealthState(str, enum.Enum):
    """Coarse node health state for swarm metrics."""

    NOMINAL = "nominal"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    FAILED = "failed"


@dataclass
class AgentParameters:
    """Transparent parameters for one SNS node.

    Legacy names such as ``energy_max`` remain supported so the Q1 experiments
    still run. In the Summer 2026 model, that reservoir is interpreted as the
    survival battery rather than a warehouse for all kite output.
    """

    pv_area: float = 0.5
    pv_efficiency: float = 0.25
    energy_max: float = 0.10
    initial_energy: float = 0.05
    capacitor_max: float = 0.003
    initial_capacitor: float = 0.0
    max_battery_charge_power: float = 0.10
    max_capacitor_charge_power: float = 1.0
    charge_efficiency: float = 0.90
    discharge_efficiency: float = 0.90
    power_idle: float = 0.002
    power_idle_low: float = 0.0001
    power_scout: float = 0.005
    power_comm: float = 0.050
    power_move: float = 0.020
    low_threshold: float = 0.02
    high_threshold: float = 0.08
    beam_efficiency: float = 0.60
    beam_rate: float = 0.050
    move_rate: float = 0.0005
    role: str = AgentRole.RELAY.value
    orientation_factor: float = 1.0
    thermal_time_constant_s: float = 1800.0
    initial_temperature_K: float = 290.0
    min_operating_temperature_K: float = 240.0
    max_operating_temperature_K: float = 350.0

    def validate(self) -> None:
        """Raise ``ValueError`` for impossible or internally inconsistent inputs."""
        if self.pv_area < 0 or not 0 <= self.pv_efficiency <= 1:
            raise ValueError("PV area must be non-negative and efficiency must be in [0, 1]")
        if self.energy_max <= 0 or not 0 <= self.initial_energy <= self.energy_max:
            raise ValueError("initial_energy must lie within [0, energy_max]")
        if self.capacitor_max < 0 or not 0 <= self.initial_capacitor <= self.capacitor_max:
            raise ValueError("initial_capacitor must lie within [0, capacitor_max]")
        for name in ("charge_efficiency", "discharge_efficiency", "beam_efficiency", "orientation_factor"):
            if not 0 <= getattr(self, name) <= 1:
                raise ValueError(f"{name} must be in [0, 1]")
        if self.low_threshold < 0 or self.high_threshold < self.low_threshold:
            raise ValueError("thresholds must satisfy 0 <= low_threshold <= high_threshold")
        AgentRole(self.role)


@dataclass(frozen=True)
class AgentStepResult:
    """Energy-flow and state telemetry emitted by one node timestep."""

    agent_id: int
    role: str
    mode: str
    health: str
    harvested_Wh: float
    direct_use_Wh: float
    battery_charge_Wh: float
    capacitor_charge_Wh: float
    load_Wh: float
    beam_input_Wh: float
    delivered_Wh: float
    curtailed_Wh: float
    battery_Wh: float
    capacitor_Wh: float
    core_temperature_K: float
    region_id: int


class SNSAgent:
    """Autonomous SNS node with role, battery, pulse buffer, and health state."""

    def __init__(self, agent_id: int, theta: float, params: AgentParameters, role: AgentRole | str | None = None) -> None:
        params.validate()
        self.id = agent_id
        self.theta = theta
        self.params = params
        self.role = AgentRole(role or params.role)
        self.energy = params.initial_energy
        self.capacitor_energy = params.initial_capacitor
        self.mode = AgentMode.HARVEST
        self.health = HealthState.NOMINAL
        self.core_temperature_K = params.initial_temperature_K

    @property
    def state_of_charge(self) -> float:
        """Return battery state of charge in ``[0, 1]``."""
        return self.energy / self.params.energy_max if self.params.energy_max else 0.0

    def harvest_power(self, flux: float) -> float:
        """Compute gross electrical PV power in watts."""
        return max(0.0, flux) * self.params.pv_area * self.params.pv_efficiency * self.params.orientation_factor

    def load_power(self, mode: AgentMode) -> float:
        """Return electrical load in watts for the requested mode."""
        return {
            AgentMode.HARVEST: self.params.power_idle,
            AgentMode.IDLE: self.params.power_idle_low,
            AgentMode.SLEEP: self.params.power_idle_low,
            AgentMode.SCOUT: self.params.power_scout,
            AgentMode.COMM_BEAM: self.params.power_comm,
            AgentMode.MOVE: self.params.power_move,
            AgentMode.REFLECT: self.params.power_idle,
        }.get(mode, self.params.power_idle)

    def _draw_stored_energy(self, requested_output_Wh: float, preserve_reserve: bool = False) -> float:
        """Supply load or beam energy from capacitor then battery."""
        if requested_output_Wh <= 0:
            return 0.0
        supplied = 0.0
        from_cap = min(self.capacitor_energy, requested_output_Wh)
        self.capacitor_energy -= from_cap
        supplied += from_cap
        remaining = requested_output_Wh - from_cap
        if remaining <= 0:
            return supplied
        reserve = self.params.low_threshold if preserve_reserve else 0.0
        battery_available_Wh = max(0.0, self.energy - reserve)
        battery_output_available = battery_available_Wh * self.params.discharge_efficiency
        battery_output = min(remaining, battery_output_available)
        self.energy -= battery_output / self.params.discharge_efficiency if self.params.discharge_efficiency else 0.0
        return supplied + battery_output

    def _charge_from_surplus(self, surplus_power_W: float, dt: float) -> tuple[float, float, float]:
        """Charge pulse buffer then battery and return stored and curtailed Wh."""
        if surplus_power_W <= 0 or dt <= 0:
            return 0.0, 0.0, 0.0
        available_Wh = surplus_power_W * dt / 3600.0
        cap_room = self.params.capacitor_max - self.capacitor_energy
        cap_input_limit = self.params.max_capacitor_charge_power * dt / 3600.0
        cap_input = min(available_Wh, cap_input_limit, cap_room)
        self.capacitor_energy += cap_input
        available_Wh -= cap_input
        battery_room = self.params.energy_max - self.energy
        battery_input_limit = self.params.max_battery_charge_power * dt / 3600.0
        battery_input = min(available_Wh, battery_input_limit)
        battery_stored = min(battery_room, battery_input * self.params.charge_efficiency)
        self.energy += battery_stored
        actual_battery_input = battery_stored / self.params.charge_efficiency if self.params.charge_efficiency else 0.0
        available_Wh -= actual_battery_input
        return battery_stored, cap_input, max(0.0, available_Wh)

    def beam_to_host(self, host, dt: float, host_deficit: float) -> tuple[float, float]:
        """Transfer energy to the host, returning input and delivered energy in Wh."""
        if host_deficit <= 0 or self.params.beam_efficiency <= 0:
            return 0.0, 0.0
        transfer_limit_Wh = self.params.beam_rate * dt / 3600.0
        required_input_Wh = host_deficit / self.params.beam_efficiency
        requested_input_Wh = min(transfer_limit_Wh, required_input_Wh)
        beam_input_Wh = self._draw_stored_energy(requested_input_Wh, preserve_reserve=True)
        delivered_Wh = beam_input_Wh * self.params.beam_efficiency
        host.receive_energy(delivered_Wh)
        return beam_input_Wh, delivered_Wh

    def move_toward(self, target_theta: float | None, dt: float) -> None:
        """Move angularly toward a coverage target."""
        if target_theta is None:
            return
        delta = (target_theta - self.theta + math.pi) % (2 * math.pi) - math.pi
        step = math.copysign(self.params.move_rate * dt, delta)
        if abs(step) > abs(delta):
            step = delta
        self.theta = (self.theta + step) % (2 * math.pi)

    def _update_temperature(self, equilibrium_temperature_K: float, dt: float) -> None:
        tau = max(1.0, self.params.thermal_time_constant_s)
        fraction = clamp(dt / tau, 0.0, 1.0)
        self.core_temperature_K += (equilibrium_temperature_K - self.core_temperature_K) * fraction

    def _update_health(self) -> None:
        if self.energy <= 1e-12 and self.capacitor_energy <= 1e-12:
            self.health = HealthState.FAILED
        elif self.state_of_charge <= 0.10:
            self.health = HealthState.CRITICAL
        elif not self.params.min_operating_temperature_K <= self.core_temperature_K <= self.params.max_operating_temperature_K:
            self.health = HealthState.DEGRADED
        else:
            self.health = HealthState.NOMINAL

    def step(self, world, host, t: float, dt: float, policy, context) -> AgentStepResult:
        """Advance one node and return auditable energy-flow telemetry."""
        self.mode = policy.decide(self, context)
        sample = getattr(context, "sample", None) or world.sample(self.theta, t)
        gross_power_W = self.harvest_power(sample.flux_W_m2) if sample.sunlit else 0.0
        load_power_W = self.load_power(self.mode)
        direct_power_W = min(gross_power_W, load_power_W)
        load_energy_Wh = load_power_W * dt / 3600.0
        direct_use_Wh = direct_power_W * dt / 3600.0
        unmet_load_Wh = max(0.0, load_energy_Wh - direct_use_Wh)
        supplied_load_Wh = self._draw_stored_energy(unmet_load_Wh)
        if supplied_load_Wh + 1e-12 < unmet_load_Wh:
            self.mode = AgentMode.SLEEP
        surplus_power_W = max(0.0, gross_power_W - direct_power_W)
        battery_charge_Wh, capacitor_charge_Wh, curtailed_Wh = self._charge_from_surplus(surplus_power_W, dt)
        beam_input_Wh = 0.0
        delivered_Wh = 0.0
        if self.mode is AgentMode.COMM_BEAM:
            beam_input_Wh, delivered_Wh = self.beam_to_host(host, dt, context.host_deficit)
        elif self.mode is AgentMode.MOVE:
            self.move_toward(context.target_theta, dt)
        self.energy = clamp(self.energy, 0.0, self.params.energy_max)
        self.capacitor_energy = clamp(self.capacitor_energy, 0.0, self.params.capacitor_max)
        self._update_temperature(sample.equilibrium_temperature_K, dt)
        self._update_health()
        return AgentStepResult(
            agent_id=self.id,
            role=self.role.value,
            mode=self.mode.value,
            health=self.health.value,
            harvested_Wh=gross_power_W * dt / 3600.0,
            direct_use_Wh=direct_use_Wh,
            battery_charge_Wh=battery_charge_Wh,
            capacitor_charge_Wh=capacitor_charge_Wh,
            load_Wh=load_energy_Wh,
            beam_input_Wh=beam_input_Wh,
            delivered_Wh=delivered_Wh,
            curtailed_Wh=curtailed_Wh,
            battery_Wh=self.energy,
            capacitor_Wh=self.capacitor_energy,
            core_temperature_K=self.core_temperature_K,
            region_id=sample.region_id,
        )

    def __repr__(self) -> str:
        return (
            f"SNSAgent(id={self.id}, role={self.role.value}, theta={self.theta:.2f}, "
            f"battery={self.energy:.4f}, capacitor={self.capacitor_energy:.4f}, mode={self.mode.value})"
        )
