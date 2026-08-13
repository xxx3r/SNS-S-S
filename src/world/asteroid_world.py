"""Rotating asteroid environment with illumination and coverage bins."""

from __future__ import annotations

import math
from collections.abc import Iterable

from src.world.base import EnvironmentSample


class AsteroidWorld:
    """Represent a rotating asteroid with a transparent day/night model."""

    def __init__(
        self,
        rotation_rate: float,
        solar_flux: float = 1360.0,
        sun_direction: float = 0.0,
        coverage_bin_count: int = 36,
        day_temperature_K: float = 330.0,
        night_temperature_K: float = 190.0,
    ) -> None:
        if coverage_bin_count <= 0:
            raise ValueError("coverage_bin_count must be positive")
        self.rotation_rate = rotation_rate
        self.solar_flux = solar_flux
        self.sun_direction = sun_direction
        self.coverage_bin_count = coverage_bin_count
        self.day_temperature_K = day_temperature_K
        self.night_temperature_K = night_temperature_K

    def surface_angle(self, theta: float, t: float) -> float:
        """Compute local surface angle relative to the Sun."""
        return (theta + self.rotation_rate * t - self.sun_direction) % (2 * math.pi)

    def is_sunlit(self, theta: float, t: float) -> bool:
        """Return whether ``theta`` lies on the illuminated hemisphere."""
        return math.cos(self.surface_angle(theta, t)) > 0.0

    def flux(self, theta: float, t: float) -> float:
        """Return cosine-weighted incident solar flux."""
        incidence = max(0.0, math.cos(self.surface_angle(theta, t)))
        return self.solar_flux * incidence

    def region_id(self, theta: float) -> int:
        """Map angular position to a stable coverage bin."""
        normalized = theta % (2 * math.pi)
        return min(self.coverage_bin_count - 1, int(normalized / (2 * math.pi) * self.coverage_bin_count))

    def stale_coverage_fraction(
        self,
        observations: Iterable[tuple[int, float]],
        t: float,
        stale_after_s: float,
    ) -> float:
        """Return the fraction of coverage bins stale at ``t``.

        A bin is fresh when its most recent observation is no more than
        ``stale_after_s`` seconds old. Bins with no observation are stale.
        The metric is policy-agnostic: callers provide only region/time
        observations, so this method does not choose or compare survey policy.
        """
        if not math.isfinite(t):
            raise ValueError("t must be finite")
        if not math.isfinite(stale_after_s):
            raise ValueError("stale_after_s must be finite")
        if stale_after_s < 0.0:
            raise ValueError("stale_after_s must be non-negative")

        latest_observation_s: dict[int, float] = {}
        for region_id, observed_at_s in observations:
            if not 0 <= region_id < self.coverage_bin_count:
                raise ValueError("observation region_id is outside coverage bins")
            if not math.isfinite(observed_at_s):
                raise ValueError("observation time must be finite")
            if observed_at_s > t:
                raise ValueError("observation time cannot be in the future")
            latest_observation_s[region_id] = max(
                observed_at_s,
                latest_observation_s.get(region_id, -math.inf),
            )

        stale_bins = sum(
            1
            for region_id in range(self.coverage_bin_count)
            if region_id not in latest_observation_s
            or t - latest_observation_s[region_id] > stale_after_s
        )
        return stale_bins / self.coverage_bin_count

    def sample(self, theta: float, t: float) -> EnvironmentSample:
        """Return illumination, temperature proxy, and coverage region."""
        local_flux = self.flux(theta, t)
        sunlit = local_flux > 0.0
        incidence = local_flux / self.solar_flux if self.solar_flux > 0 else 0.0
        temperature = self.night_temperature_K + (self.day_temperature_K - self.night_temperature_K) * incidence
        return EnvironmentSample(
            sunlit=sunlit,
            flux_W_m2=local_flux,
            equilibrium_temperature_K=temperature,
            region_id=self.region_id(theta),
            line_of_sight_to_host=True,
        )

    def daylight_fraction(self, theta_samples: int = 360) -> float:
        """Approximate the fraction of the surface illuminated at one instant."""
        if theta_samples <= 0:
            raise ValueError("theta_samples must be positive")
        return sum(self.is_sunlit(2 * math.pi * i / theta_samples, 0.0) for i in range(theta_samples)) / theta_samples
