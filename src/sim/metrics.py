"""Metrics collection for SNS-S-S simulations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List


def _mean(values: Iterable[float]) -> float:
    values_list = list(values)
    return sum(values_list) / len(values_list) if values_list else 0.0


def _count_below(values: Iterable[float], threshold: float) -> int:
    return sum(1 for v in values if v <= threshold)


@dataclass
class MetricsRecorder:
    """Record time-series metrics for a simulation run."""

    t_values: List[float] = field(default_factory=list)
    E_host_values: List[float] = field(default_factory=list)
    E_mean_values: List[float] = field(default_factory=list)
    E_min_values: List[float] = field(default_factory=list)
    E_max_values: List[float] = field(default_factory=list)
    dead_agent_count: List[int] = field(default_factory=list)

    def record(self, t: float, host_energy: float, agent_energies: List[float], dead_threshold: float = 1e-6) -> None:
        """Append a new set of measurements."""

        self.t_values.append(t)
        self.E_host_values.append(host_energy)
        self.E_mean_values.append(_mean(agent_energies))
        self.E_min_values.append(min(agent_energies))
        self.E_max_values.append(max(agent_energies))
        self.dead_agent_count.append(_count_below(agent_energies, dead_threshold))

    def to_dict(self) -> dict:
        """Return recorded metrics as a dictionary of lists."""

        return {
            "t": self.t_values,
            "E_host": self.E_host_values,
            "E_mean": self.E_mean_values,
            "E_min": self.E_min_values,
            "E_max": self.E_max_values,
            "dead_agent_count": self.dead_agent_count,
        }
