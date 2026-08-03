"""Dependency accounting for the two remaining QST-STOR-0002 routes.

This is a configurable screening ledger, not a spacecraft design or trajectory.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DependencyCase:
    name: str
    architecture: str
    node_mass_kg: float
    deployment_mass_kg: float
    navigation_mass_kg: float
    stationkeeping_mass_kg: float
    resilience_mass_kg: float
    host_service_mass_kg: float
    node_power_W: float
    navigation_power_W: float
    stationkeeping_power_W: float
    host_service_power_W: float
    target_rotation_period_h: float | None
    rotation_limit_h: float
    assumptions: tuple[str, ...]

    def __post_init__(self) -> None:
        values = (
            self.node_mass_kg,
            self.deployment_mass_kg,
            self.navigation_mass_kg,
            self.stationkeeping_mass_kg,
            self.resilience_mass_kg,
            self.host_service_mass_kg,
            self.node_power_W,
            self.navigation_power_W,
            self.stationkeeping_power_W,
            self.host_service_power_W,
            self.rotation_limit_h,
        )
        if any(value < 0.0 for value in values):
            raise ValueError("declared values must be non-negative")
        if self.target_rotation_period_h is not None and self.target_rotation_period_h <= 0.0:
            raise ValueError("target rotation period must be positive")

    @property
    def dependency_mass_kg(self) -> float:
        return sum((
            self.deployment_mass_kg,
            self.navigation_mass_kg,
            self.stationkeeping_mass_kg,
            self.resilience_mass_kg,
            self.host_service_mass_kg,
        ))

    @property
    def total_mass_kg(self) -> float:
        return self.node_mass_kg + self.dependency_mass_kg

    @property
    def dependency_power_W(self) -> float:
        return self.navigation_power_W + self.stationkeeping_power_W + self.host_service_power_W

    @property
    def daily_energy_Wh(self) -> float:
        return (self.node_power_W + self.dependency_power_W) * 24.0

    @property
    def geometry_status(self) -> str:
        if self.architecture == "fast_rotator_surface":
            if self.target_rotation_period_h is None:
                return "FAIL_MISSING_TARGET_ROTATION"
            if self.target_rotation_period_h <= self.rotation_limit_h + 1e-12:
                return "PASS_CONDITIONAL_TARGET"
            return "FAIL_TARGET_ROTATION"
        if self.architecture == "active_sunward_hosted":
            return "PASS_CONDITIONAL_ACTIVE_HOST"
        raise ValueError(f"unsupported architecture: {self.architecture}")

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "architecture": self.architecture,
            "geometry_status": self.geometry_status,
            "node_mass_kg": self.node_mass_kg,
            "dependency_mass_kg": self.dependency_mass_kg,
            "total_mass_kg": self.total_mass_kg,
            "dependency_power_W": self.dependency_power_W,
            "daily_energy_Wh": self.daily_energy_Wh,
            "target_rotation_period_h": self.target_rotation_period_h,
            "rotation_limit_h": self.rotation_limit_h,
            "assumptions": list(self.assumptions),
        }


def compare_min_materials(surface: DependencyCase, hosted: DependencyCase) -> dict:
    if surface.architecture != "fast_rotator_surface":
        raise ValueError("surface architecture mismatch")
    if hosted.architecture != "active_sunward_hosted":
        raise ValueError("hosted architecture mismatch")

    if not surface.geometry_status.startswith("PASS") or not hosted.geometry_status.startswith("PASS"):
        winner = "NO_MATCHED_WINNER"
    elif surface.total_mass_kg < hosted.total_mass_kg:
        winner = "fast_rotator_surface"
    elif hosted.total_mass_kg < surface.total_mass_kg:
        winner = "active_sunward_hosted"
    else:
        winner = "MASS_TIE"

    return {
        "winner_by_declared_total_mass": winner,
        "hosted_minus_surface_mass_kg": hosted.total_mass_kg - surface.total_mass_kg,
        "hosted_minus_surface_daily_energy_Wh": hosted.daily_energy_Wh - surface.daily_energy_Wh,
        "interpretation": (
            "The surface route uses less declared supporting mass, but only for a measured "
            "target within the rotation limit. Hosting broadens availability by adding "
            "navigation, stationkeeping, resilience, and host-service dependencies."
        ),
    }
