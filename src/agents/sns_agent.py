"""SNS agent model with baseline and coordinated behaviors."""

from __future__ import annotations

import enum
import math
from dataclasses import dataclass

from src.utils.math_utils import clamp


class AgentMode(str, enum.Enum):
    """Operating modes for an SNS agent."""

    HARVEST = "HARVEST"
    IDLE = "IDLE"
    COMM_BEAM = "COMM_BEAM"
    MOVE = "MOVE"


@dataclass
class AgentParameters:
    """Parameter bundle for a single SNS agent."""

    pv_area: float = 0.5
    pv_efficiency: float = 0.25
    energy_max: float = 5.0
    initial_energy: float = 1.0
    power_idle: float = 0.2
    power_idle_low: float = 0.05
    low_threshold: float = 0.5
    high_threshold: float = 4.0
    beam_efficiency: float = 0.6
    beam_rate: float = 0.5
    power_comm: float = 0.1
    power_move: float = 0.2
    move_rate: float = 0.0005


class SNSAgent:
    """Simple SNS agent supporting configurable policies."""

    def __init__(self, agent_id: int, theta: float, params: AgentParameters) -> None:
        self.id = agent_id
        self.theta = theta
        self.params = params
        self.energy = params.initial_energy
        self.mode = AgentMode.HARVEST

    def harvest_power(self, flux: float) -> float:
        """Compute instantaneous harvest power in watts."""

        return flux * self.params.pv_area * self.params.pv_efficiency

    def load_power(self, mode: AgentMode) -> float:
        """Power draw in watts for the requested mode."""

        if mode is AgentMode.HARVEST:
            return self.params.power_idle
        if mode is AgentMode.IDLE:
            return self.params.power_idle_low
        if mode is AgentMode.COMM_BEAM:
            return self.params.power_comm
        if mode is AgentMode.MOVE:
            return self.params.power_move
        return self.params.power_idle

    def beam_to_host(self, host, dt: float, host_deficit: float) -> float:
        """Beam energy to the host when available and requested."""

        available = max(0.0, self.energy - self.params.low_threshold)
        transfer_limit = self.params.beam_rate * dt / 3600.0
        requested = host_deficit / self.params.beam_efficiency if self.params.beam_efficiency > 0 else 0.0
        transfer = min(available, transfer_limit, requested if requested > 0 else available)
        if transfer <= 0:
            return 0.0
        delivered = transfer * self.params.beam_efficiency
        self.energy -= transfer
        host.receive_energy(delivered)
        return delivered

    def move_toward(self, target_theta: float, dt: float) -> None:
        """Rotate the agent toward a target angular position."""

        if target_theta is None:
            return
        delta = (target_theta - self.theta + math.pi) % (2 * math.pi) - math.pi
        step = math.copysign(self.params.move_rate * dt, delta)
        if abs(step) > abs(delta):
            step = delta
        self.theta = (self.theta + step) % (2 * math.pi)

    def step(self, world, host, t: float, dt: float, policy, context) -> None:
        """Advance the agent by one timestep using the provided policy."""

        self.mode = policy.decide(self, context)

        flux = world.flux(self.theta, t) if context.sunlit else 0.0
        harvest_power = self.harvest_power(flux)
        load_power = self.load_power(self.mode)

        delta_energy = (harvest_power - load_power) * dt / 3600.0
        self.energy = clamp(self.energy + delta_energy, 0.0, self.params.energy_max)

        if self.mode is AgentMode.COMM_BEAM and self.energy > self.params.low_threshold:
            self.beam_to_host(host, dt, context.host_deficit)
        elif self.mode is AgentMode.MOVE and context.target_theta is not None:
            self.move_toward(context.target_theta, dt)

    def __repr__(self) -> str:  # pragma: no cover - convenience
        return f"SNSAgent(id={self.id}, theta={self.theta:.2f}, energy={self.energy:.2f}, mode={self.mode})"
