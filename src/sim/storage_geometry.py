"""Geometry-derived seed storage envelope calculations for SNS nodes."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from math import pi


@dataclass(frozen=True)
class StorageScenario:
    core_diameter_mm: float
    shell_thickness_mm: float
    energy_density_wh_per_l: float
    reserve_fraction: float
    round_trip_efficiency: float
    active_duty_cycle: float
    load_power_mw: float


@dataclass(frozen=True)
class StorageResult:
    core_diameter_mm: float
    shell_thickness_mm: float
    energy_density_wh_per_l: float
    reserve_fraction: float
    round_trip_efficiency: float
    active_duty_cycle: float
    load_power_mw: float
    storage_volume_l: float
    usable_energy_wh: float
    required_energy_wh: float
    margin_wh: float
    status: str


def sphere_volume_l(diameter_mm: float) -> float:
    """Return sphere volume in liters for a diameter in millimeters."""
    radius_m = diameter_mm / 2000.0
    return (4.0 / 3.0) * pi * radius_m**3 * 1000.0


def shell_volume_l(core_diameter_mm: float, shell_thickness_mm: float) -> float:
    """Return spherical shell volume in liters."""
    return sphere_volume_l(core_diameter_mm + 2.0 * shell_thickness_mm) - sphere_volume_l(core_diameter_mm)


def evaluate_storage_scenario(scenario: StorageScenario, eclipse_hours: float) -> StorageResult:
    """Evaluate whether a storage geometry can cover an eclipse duty cycle."""
    volume_l = shell_volume_l(scenario.core_diameter_mm, scenario.shell_thickness_mm)
    usable_wh = (
        volume_l
        * scenario.energy_density_wh_per_l
        * (1.0 - scenario.reserve_fraction)
        * scenario.round_trip_efficiency
    )
    required_wh = (scenario.load_power_mw / 1000.0) * scenario.active_duty_cycle * eclipse_hours
    margin_wh = usable_wh - required_wh
    return StorageResult(**asdict(scenario), storage_volume_l=volume_l, usable_energy_wh=usable_wh, required_energy_wh=required_wh, margin_wh=margin_wh, status="PASS" if margin_wh >= 0 else "FAIL")
