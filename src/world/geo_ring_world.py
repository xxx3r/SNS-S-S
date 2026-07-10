"""Idealized GEO-ring environment with eclipse windows."""

from __future__ import annotations

import math

from src.world.base import EnvironmentSample


class GEORingWorld:
    """Model nodes on a circular GEO-like ring with a configurable eclipse fraction."""

    def __init__(
        self,
        solar_flux: float = 1360.0,
        orbital_period_s: float = 86164.0,
        eclipse_fraction: float = 0.05,
        coverage_bin_count: int = 72,
        sun_temperature_K: float = 315.0,
        eclipse_temperature_K: float = 230.0,
    ) -> None:
        if orbital_period_s <= 0:
            raise ValueError("orbital_period_s must be positive")
        if not 0.0 <= eclipse_fraction < 1.0:
            raise ValueError("eclipse_fraction must be in [0, 1)")
        if coverage_bin_count <= 0:
            raise ValueError("coverage_bin_count must be positive")
        self.solar_flux = solar_flux
        self.orbital_period_s = orbital_period_s
        self.eclipse_fraction = eclipse_fraction
        self.coverage_bin_count = coverage_bin_count
        self.sun_temperature_K = sun_temperature_K
        self.eclipse_temperature_K = eclipse_temperature_K

    def orbital_phase(self, theta: float, t: float) -> float:
        """Return node phase in the ring frame."""
        return (theta + 2 * math.pi * t / self.orbital_period_s) % (2 * math.pi)

    def is_sunlit(self, theta: float, t: float) -> bool:
        """Return false inside a centered anti-solar eclipse window."""
        if self.eclipse_fraction == 0.0:
            return True
        phase = self.orbital_phase(theta, t)
        angular_distance_from_eclipse = abs((phase - math.pi + math.pi) % (2 * math.pi) - math.pi)
        return angular_distance_from_eclipse > math.pi * self.eclipse_fraction

    def flux(self, theta: float, t: float) -> float:
        """Return full nominal flux outside eclipse and zero inside it."""
        return self.solar_flux if self.is_sunlit(theta, t) else 0.0

    def region_id(self, theta: float, t: float) -> int:
        """Map orbital phase to a coverage bin."""
        phase = self.orbital_phase(theta, t)
        return min(self.coverage_bin_count - 1, int(phase / (2 * math.pi) * self.coverage_bin_count))

    def sample(self, theta: float, t: float) -> EnvironmentSample:
        """Return eclipse state, thermal proxy, and orbital region."""
        sunlit = self.is_sunlit(theta, t)
        return EnvironmentSample(
            sunlit=sunlit,
            flux_W_m2=self.solar_flux if sunlit else 0.0,
            equilibrium_temperature_K=self.sun_temperature_K if sunlit else self.eclipse_temperature_K,
            region_id=self.region_id(theta, t),
            line_of_sight_to_host=True,
        )
