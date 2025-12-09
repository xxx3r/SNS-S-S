"""World model for an asteroid with simple day/night illumination."""

from __future__ import annotations

import math


class AsteroidWorld:
    """Represent a rotating asteroid and provide illumination queries.

    Parameters
    ----------
    rotation_rate: float
        Angular rotation rate of the asteroid body in radians per second.
    solar_flux: float
        Solar flux on the day side in W/m^2.
    sun_direction: float
        Reference angle (radians) that defines where the sun-facing
        meridian sits at ``t = 0``.
    """

    def __init__(self, rotation_rate: float, solar_flux: float = 1360.0, sun_direction: float = 0.0) -> None:
        self.rotation_rate = rotation_rate
        self.solar_flux = solar_flux
        self.sun_direction = sun_direction

    def surface_angle(self, theta: float, t: float) -> float:
        """Compute the local surface angle relative to the sun direction."""

        return (theta + self.rotation_rate * t - self.sun_direction) % (2 * math.pi)

    def is_sunlit(self, theta: float, t: float) -> bool:
        """Return True if a position at ``theta`` is illuminated at time ``t``."""

        local_angle = self.surface_angle(theta, t)
        return math.cos(local_angle) > 0.0

    def flux(self, theta: float, t: float) -> float:
        """Return the solar flux experienced at ``theta`` and time ``t``."""

        if self.is_sunlit(theta, t):
            incidence = max(0.0, math.cos(self.surface_angle(theta, t)))
            return self.solar_flux * incidence
        return 0.0

    def daylight_fraction(self, theta_samples: int = 360) -> float:
        """Approximate the daylight fraction around the body."""

        lit_count = 0
        for i in range(theta_samples):
            theta = 2 * math.pi * i / theta_samples
            if self.is_sunlit(theta, 0.0):
                lit_count += 1
        return lit_count / theta_samples
