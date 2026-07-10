"""Shared environment interface for SNS mission scenarios."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class EnvironmentSample:
    """Local environmental state sampled by one SNS node."""

    sunlit: bool
    flux_W_m2: float
    equilibrium_temperature_K: float
    region_id: int
    line_of_sight_to_host: bool = True


class WorldModel(Protocol):
    """Protocol implemented by every Summer 2026 environment model."""

    coverage_bin_count: int

    def sample(self, theta: float, t: float) -> EnvironmentSample:
        """Return the local environment at angular position ``theta`` and time ``t``."""

    def is_sunlit(self, theta: float, t: float) -> bool:
        """Return whether the node is illuminated."""

    def flux(self, theta: float, t: float) -> float:
        """Return incident solar flux in W/m²."""
