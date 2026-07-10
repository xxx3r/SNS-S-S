"""Metrics for energy flow, survival, coverage, roles, and health."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass, field
from typing import Iterable, List, Sequence

from src.agents.sns_agent import AgentStepResult


def _mean(values: Iterable[float]) -> float:
    values_list = list(values)
    return sum(values_list) / len(values_list) if values_list else 0.0


def _count_below(values: Iterable[float], threshold: float) -> int:
    return sum(1 for value in values if value <= threshold)


@dataclass
class MetricsRecorder:
    """Record timestep and cumulative mission metrics."""

    t_values: List[float] = field(default_factory=list)
    E_host_values: List[float] = field(default_factory=list)
    E_mean_values: List[float] = field(default_factory=list)
    E_min_values: List[float] = field(default_factory=list)
    E_max_values: List[float] = field(default_factory=list)
    dead_agent_count: List[int] = field(default_factory=list)
    harvested_total_Wh: List[float] = field(default_factory=list)
    delivered_total_Wh: List[float] = field(default_factory=list)
    curtailed_total_Wh: List[float] = field(default_factory=list)
    load_total_Wh: List[float] = field(default_factory=list)
    coverage_fraction: List[float] = field(default_factory=list)
    mean_temperature_K: List[float] = field(default_factory=list)
    mode_counts: List[dict[str, int]] = field(default_factory=list)
    role_counts: List[dict[str, int]] = field(default_factory=list)
    health_counts: List[dict[str, int]] = field(default_factory=list)
    _harvested_cumulative: float = 0.0
    _delivered_cumulative: float = 0.0
    _curtailed_cumulative: float = 0.0
    _load_cumulative: float = 0.0

    def record(
        self,
        t: float,
        host_energy: float,
        agent_energies: List[float],
        dead_threshold: float = 1e-6,
        *,
        step_results: Sequence[AgentStepResult] | None = None,
        coverage_fraction: float = 0.0,
        roles: Sequence[str] | None = None,
    ) -> None:
        """Append one auditable timestep.

        ``step_results`` is optional for compatibility with Q1 callers.
        """
        if not agent_energies:
            raise ValueError("agent_energies must not be empty")
        results = list(step_results or [])
        self.t_values.append(t)
        self.E_host_values.append(host_energy)
        self.E_mean_values.append(_mean(agent_energies))
        self.E_min_values.append(min(agent_energies))
        self.E_max_values.append(max(agent_energies))
        self.dead_agent_count.append(_count_below(agent_energies, dead_threshold))
        self._harvested_cumulative += sum(result.harvested_Wh for result in results)
        self._delivered_cumulative += sum(result.delivered_Wh for result in results)
        self._curtailed_cumulative += sum(result.curtailed_Wh for result in results)
        self._load_cumulative += sum(result.load_Wh for result in results)
        self.harvested_total_Wh.append(self._harvested_cumulative)
        self.delivered_total_Wh.append(self._delivered_cumulative)
        self.curtailed_total_Wh.append(self._curtailed_cumulative)
        self.load_total_Wh.append(self._load_cumulative)
        self.coverage_fraction.append(max(0.0, min(1.0, coverage_fraction)))
        self.mean_temperature_K.append(_mean(result.core_temperature_K for result in results))
        self.mode_counts.append(dict(Counter(result.mode for result in results)))
        self.health_counts.append(dict(Counter(result.health for result in results)))
        self.role_counts.append(dict(Counter(roles or [result.role for result in results])))

    def summary(self) -> dict:
        """Return final scalar metrics for comparisons and reports."""
        if not self.t_values:
            return {
                "steps": 0,
                "E_host": 0.0,
                "E_mean": 0.0,
                "dead_agent_count": 0,
                "harvested_total_Wh": 0.0,
                "delivered_total_Wh": 0.0,
                "curtailed_total_Wh": 0.0,
                "coverage_fraction": 0.0,
            }
        return {
            "steps": len(self.t_values),
            "E_host": self.E_host_values[-1],
            "E_mean": self.E_mean_values[-1],
            "E_min": self.E_min_values[-1],
            "E_max": self.E_max_values[-1],
            "dead_agent_count": self.dead_agent_count[-1],
            "harvested_total_Wh": self.harvested_total_Wh[-1],
            "delivered_total_Wh": self.delivered_total_Wh[-1],
            "curtailed_total_Wh": self.curtailed_total_Wh[-1],
            "load_total_Wh": self.load_total_Wh[-1],
            "coverage_fraction": self.coverage_fraction[-1],
            "mean_temperature_K": self.mean_temperature_K[-1],
            "mode_counts": self.mode_counts[-1],
            "role_counts": self.role_counts[-1],
            "health_counts": self.health_counts[-1],
        }

    def to_rows(self) -> list[dict]:
        """Return flat timestep rows suitable for CSV output."""
        rows = []
        for index, t in enumerate(self.t_values):
            rows.append(
                {
                    "t": t,
                    "E_host": self.E_host_values[index],
                    "E_mean": self.E_mean_values[index],
                    "E_min": self.E_min_values[index],
                    "E_max": self.E_max_values[index],
                    "dead_agent_count": self.dead_agent_count[index],
                    "harvested_total_Wh": self.harvested_total_Wh[index],
                    "delivered_total_Wh": self.delivered_total_Wh[index],
                    "curtailed_total_Wh": self.curtailed_total_Wh[index],
                    "load_total_Wh": self.load_total_Wh[index],
                    "coverage_fraction": self.coverage_fraction[index],
                    "mean_temperature_K": self.mean_temperature_K[index],
                }
            )
        return rows

    def to_dict(self) -> dict:
        """Return serializable time series and final summary."""
        payload = asdict(self)
        for private_key in [key for key in payload if key.startswith("_")]:
            payload.pop(private_key)
        payload["summary"] = self.summary()
        return payload
