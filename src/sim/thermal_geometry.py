"""Geometry-derived first-order thermal properties for a 10 mm SNS node."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import math

STEFAN_BOLTZMANN_W_M2_K4 = 5.670374419e-8


@dataclass(frozen=True)
class ThermalGeometryCase:
    name: str
    outer_diameter_m: float
    core_diameter_m: float
    core_density_kg_m3: float
    core_specific_heat_J_kg_K: float
    shell_density_kg_m3: float
    shell_specific_heat_J_kg_K: float
    effective_emissivity: float
    linearization_temperature_K: float
    parasitic_conductance_W_K: float = 0.0

    def validate(self) -> None:
        if self.outer_diameter_m <= 0 or self.core_diameter_m <= 0:
            raise ValueError("diameters must be positive")
        if self.core_diameter_m >= self.outer_diameter_m:
            raise ValueError("core diameter must be smaller than outer diameter")
        for name in (
            "core_density_kg_m3",
            "core_specific_heat_J_kg_K",
            "shell_density_kg_m3",
            "shell_specific_heat_J_kg_K",
            "linearization_temperature_K",
        ):
            if getattr(self, name) <= 0:
                raise ValueError(f"{name} must be positive")
        if not 0.0 <= self.effective_emissivity <= 1.0:
            raise ValueError("effective_emissivity must be in [0, 1]")
        if self.parasitic_conductance_W_K < 0:
            raise ValueError("parasitic_conductance_W_K must be non-negative")


@dataclass(frozen=True)
class ThermalGeometryResult:
    outer_area_m2: float
    core_volume_m3: float
    shell_volume_m3: float
    core_mass_kg: float
    shell_mass_kg: float
    total_mass_kg: float
    thermal_capacity_J_K: float
    radiative_conductance_W_K: float
    total_conductance_W_K: float


def _sphere_volume(diameter_m: float) -> float:
    return math.pi * diameter_m**3 / 6.0


def derive_thermal_properties(case: ThermalGeometryCase) -> ThermalGeometryResult:
    """Derive lumped heat capacity and linearized radiative conductance."""
    case.validate()
    outer_radius_m = case.outer_diameter_m / 2.0
    outer_area_m2 = 4.0 * math.pi * outer_radius_m**2
    outer_volume_m3 = _sphere_volume(case.outer_diameter_m)
    core_volume_m3 = _sphere_volume(case.core_diameter_m)
    shell_volume_m3 = outer_volume_m3 - core_volume_m3
    core_mass_kg = core_volume_m3 * case.core_density_kg_m3
    shell_mass_kg = shell_volume_m3 * case.shell_density_kg_m3
    thermal_capacity_J_K = (
        core_mass_kg * case.core_specific_heat_J_kg_K
        + shell_mass_kg * case.shell_specific_heat_J_kg_K
    )
    radiative_conductance_W_K = (
        4.0
        * case.effective_emissivity
        * STEFAN_BOLTZMANN_W_M2_K4
        * outer_area_m2
        * case.linearization_temperature_K**3
    )
    return ThermalGeometryResult(
        outer_area_m2=outer_area_m2,
        core_volume_m3=core_volume_m3,
        shell_volume_m3=shell_volume_m3,
        core_mass_kg=core_mass_kg,
        shell_mass_kg=shell_mass_kg,
        total_mass_kg=core_mass_kg + shell_mass_kg,
        thermal_capacity_J_K=thermal_capacity_J_K,
        radiative_conductance_W_K=radiative_conductance_W_K,
        total_conductance_W_K=radiative_conductance_W_K + case.parasitic_conductance_W_K,
    )


def case_with_result(case: ThermalGeometryCase) -> dict[str, float | str]:
    return {**asdict(case), **asdict(derive_thermal_properties(case))}
