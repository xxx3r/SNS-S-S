"""Host collector for energy delivered by an SNS swarm."""

from __future__ import annotations

from typing import Callable, Optional


class HostCollector:
    """Track cumulative energy received and mission demand."""

    def __init__(self, demand_function: Optional[Callable[[float], float]] = None, demand_rate: float = 0.0) -> None:
        self.energy = 0.0
        self.energy_received_Wh = 0.0
        if demand_function is None and demand_rate > 0:
            self.demand_function = lambda t: demand_rate * t / 3600.0
        else:
            self.demand_function = demand_function

    def receive_energy(self, delta_energy: float) -> None:
        """Record positive delivered energy in Wh."""
        if delta_energy > 0:
            self.energy += delta_energy
            self.energy_received_Wh += delta_energy

    def cumulative_demand(self, t: float) -> float:
        """Return cumulative host demand at ``t`` in Wh."""
        return 0.0 if self.demand_function is None else max(0.0, float(self.demand_function(t)))

    def get_deficit(self, t: float) -> float:
        """Return cumulative demand minus received energy."""
        return max(0.0, self.cumulative_demand(t) - self.energy)
