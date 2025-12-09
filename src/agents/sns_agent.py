"""SNS agent model with simple HARVEST and IDLE behaviors."""

from __future__ import annotations

import enum
from dataclasses import dataclass

from src.utils.math_utils import clamp


class AgentMode(str, enum.Enum):
    """Operating modes for an SNS agent."""

    HARVEST = "HARVEST"
    IDLE = "IDLE"


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


class SNSAgent:
    """Simple SNS agent that can harvest and idle."""

    def __init__(self, agent_id: int, theta: float, params: AgentParameters) -> None:
        self.id = agent_id
        self.theta = theta
        self.params = params
        self.energy = params.initial_energy
        self.mode = AgentMode.HARVEST

    def decide_mode(self, sunlit: bool) -> None:
        """Choose mode based on illumination and stored energy."""

        if sunlit:
            self.mode = AgentMode.HARVEST
        else:
            self.mode = AgentMode.IDLE

    def harvest_power(self, flux: float) -> float:
        """Compute instantaneous harvest power in watts."""

        return flux * self.params.pv_area * self.params.pv_efficiency

    def load_power(self) -> float:
        """Power draw in watts for the current mode."""

        if self.mode is AgentMode.HARVEST:
            return self.params.power_idle
        return self.params.power_idle_low

    def beam_to_host(self, host, dt: float) -> float:
        """Optionally beam energy to the host for coordinated policies."""

        available = max(0.0, self.energy - self.params.low_threshold)
        transfer = min(available, self.params.beam_rate * dt / 3600.0)
        if transfer <= 0:
            return 0.0
        delivered = transfer * self.params.beam_efficiency
        self.energy -= transfer
        host.receive_energy(delivered)
        return delivered

    def step(self, world, host, t: float, dt: float, coordinated: bool = False) -> None:
        """Advance the agent by one timestep."""

        sunlit = world.is_sunlit(self.theta, t)
        self.decide_mode(sunlit)

        flux = world.flux(self.theta, t) if self.mode is AgentMode.HARVEST else 0.0
        harvest_power = self.harvest_power(flux)
        load_power = self.load_power()

        delta_energy = (harvest_power - load_power) * dt / 3600.0
        self.energy = clamp(self.energy + delta_energy, 0.0, self.params.energy_max)

        if coordinated and self.energy > self.params.high_threshold:
            self.beam_to_host(host, dt)

    def __repr__(self) -> str:  # pragma: no cover - convenience
        return f"SNSAgent(id={self.id}, theta={self.theta:.2f}, energy={self.energy:.2f}, mode={self.mode})"
