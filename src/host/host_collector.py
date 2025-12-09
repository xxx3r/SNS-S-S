"""Host collector for energy delivered by the SNS swarm."""

from __future__ import annotations

from typing import Callable, Optional


class HostCollector:
    """Track energy received by a host and optional demand."""

    def __init__(self, demand_function: Optional[Callable[[float], float]] = None) -> None:
        self.energy = 0.0
        self.demand_function = demand_function

    def receive_energy(self, delta_energy: float) -> None:
        """Increase stored energy by ``delta_energy`` in Wh."""

        if delta_energy > 0:
            self.energy += delta_energy

    def get_deficit(self, t: float) -> float:
        """Return demand minus current energy for time ``t`` (non-negative)."""

        if self.demand_function is None:
            return 0.0
        demand = self.demand_function(t)
        return max(0.0, demand - self.energy)
