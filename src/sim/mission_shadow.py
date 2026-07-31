"""Bounded mission-shadow geometry for QST-STOR-0002.

The helpers in this module answer one narrow screening question: can a declared
asteroid-scout or hosted geometry keep continuous shadow at or below a thermal
acceptance limit? They do not model irregular bodies, perturbed orbits,
station-keeping cost, penumbra, seasonal Sun geometry, or surface topography.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

GRAVITATIONAL_CONSTANT_M3_KG_S2 = 6.67430e-11


@dataclass(frozen=True)
class ShadowResult:
    """One mission-shadow screening result with explicit units and status."""

    name: str
    architecture: str
    maximum_shadow_h: float
    acceptance_limit_h: float
    status: str
    guarantee_class: str
    assumptions: tuple[str, ...]

    def to_dict(self) -> dict:
        """Serialize the result for JSON artifacts."""
        return {
            "name": self.name,
            "architecture": self.architecture,
            "maximum_shadow_h": self.maximum_shadow_h,
            "maximum_shadow_min": self.maximum_shadow_h * 60.0,
            "acceptance_limit_h": self.acceptance_limit_h,
            "status": self.status,
            "guarantee_class": self.guarantee_class,
            "assumptions": list(self.assumptions),
        }


def _status(duration_h: float, acceptance_limit_h: float) -> str:
    return "PASS" if duration_h <= acceptance_limit_h + 1e-12 else "FAIL"


def surface_fixed_shadow(
    *,
    name: str,
    rotation_period_h: float,
    acceptance_limit_h: float,
) -> ShadowResult:
    """Return the maximum night interval for an equatorial surface-fixed node.

    A spherical body with a fixed Sun direction gives one half-rotation of
    darkness. This is an upper-level geometry proxy, not a topographic model.
    """
    if rotation_period_h <= 0.0:
        raise ValueError("rotation_period_h must be positive")
    if acceptance_limit_h < 0.0:
        raise ValueError("acceptance_limit_h must be non-negative")
    duration_h = rotation_period_h / 2.0
    return ShadowResult(
        name=name,
        architecture="surface_fixed_equator",
        maximum_shadow_h=duration_h,
        acceptance_limit_h=acceptance_limit_h,
        status=_status(duration_h, acceptance_limit_h),
        guarantee_class="conditional_on_target_rotation_and_spherical_geometry",
        assumptions=(
            "spherical body",
            "equatorial fixed node",
            "constant rotation period",
            "no terrain self-shadow extension",
        ),
    )


def circular_orbit_shadow(
    *,
    name: str,
    asteroid_density_kg_m3: float,
    orbital_radius_ratio: float,
    acceptance_limit_h: float,
) -> ShadowResult:
    """Return central umbra duration for a circular equatorial asteroid orbit.

    ``orbital_radius_ratio`` is orbital radius divided by asteroid radius. For a
    uniform-density spherical body, asteroid radius cancels from the two-body
    angular rate, so this screening duration depends on density and radius ratio.
    """
    if asteroid_density_kg_m3 <= 0.0:
        raise ValueError("asteroid_density_kg_m3 must be positive")
    if orbital_radius_ratio <= 1.0:
        raise ValueError("orbital_radius_ratio must exceed 1")
    if acceptance_limit_h < 0.0:
        raise ValueError("acceptance_limit_h must be non-negative")

    mean_motion_rad_s = math.sqrt(
        (4.0 / 3.0)
        * math.pi
        * GRAVITATIONAL_CONSTANT_M3_KG_S2
        * asteroid_density_kg_m3
        / orbital_radius_ratio**3
    )
    eclipse_half_angle_rad = math.asin(1.0 / orbital_radius_ratio)
    duration_h = 2.0 * eclipse_half_angle_rad / mean_motion_rad_s / 3600.0
    return ShadowResult(
        name=name,
        architecture="passive_circular_equatorial_orbit",
        maximum_shadow_h=duration_h,
        acceptance_limit_h=acceptance_limit_h,
        status=_status(duration_h, acceptance_limit_h),
        guarantee_class="worst_case_central_umbra_screening",
        assumptions=(
            "uniform-density spherical asteroid",
            "two-body circular equatorial orbit",
            "central umbra crossing",
            "point Sun and no penumbra",
        ),
    )


def hosted_sunward_standoff_shadow(
    *,
    name: str,
    sunward_constraint_maintained: bool,
    acceptance_limit_h: float,
) -> ShadowResult:
    """Return a conditional zero-shadow result for active sunward standoff.

    This is a mission constraint, not a passive orbital solution. A PASS means
    geometric occultation is excluded while the host actively maintains the
    declared sunward half-space; propulsion, navigation, and fault tolerance are
    outside this model.
    """
    if acceptance_limit_h < 0.0:
        raise ValueError("acceptance_limit_h must be non-negative")
    duration_h = 0.0 if sunward_constraint_maintained else math.inf
    return ShadowResult(
        name=name,
        architecture="hosted_active_sunward_standoff",
        maximum_shadow_h=duration_h,
        acceptance_limit_h=acceptance_limit_h,
        status=_status(duration_h, acceptance_limit_h),
        guarantee_class=(
            "conditional_active_geometry_guarantee"
            if sunward_constraint_maintained
            else "no_guarantee_without_station_keeping"
        ),
        assumptions=(
            "host maintains sunward half-space",
            "navigation and propulsion remain available",
            "node remains thermally coupled only as separately modeled",
        ),
    )
