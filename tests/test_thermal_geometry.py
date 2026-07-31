import math
import pytest

from src.sim.thermal_geometry import ThermalGeometryCase, derive_thermal_properties


def baseline_case(**overrides):
    values = dict(
        name="baseline",
        outer_diameter_m=0.010,
        core_diameter_m=0.008,
        core_density_kg_m3=1800.0,
        core_specific_heat_J_kg_K=900.0,
        shell_density_kg_m3=1200.0,
        shell_specific_heat_J_kg_K=1000.0,
        effective_emissivity=0.2,
        linearization_temperature_K=270.0,
        parasitic_conductance_W_K=0.0,
    )
    values.update(overrides)
    return ThermalGeometryCase(**values)


def test_10mm_sphere_geometry_and_capacity_are_explicit():
    result = derive_thermal_properties(baseline_case())
    assert result.outer_area_m2 == pytest.approx(math.pi * 1e-4)
    assert result.total_mass_kg == pytest.approx(7.892e-4, rel=1e-3)
    assert result.thermal_capacity_J_K == pytest.approx(0.7409, rel=1e-3)


def test_radiative_conductance_scales_with_emissivity():
    low = derive_thermal_properties(baseline_case(effective_emissivity=0.05))
    high = derive_thermal_properties(baseline_case(effective_emissivity=0.8))
    assert high.radiative_conductance_W_K == pytest.approx(16.0 * low.radiative_conductance_W_K)


def test_parasitic_conductance_is_added_separately():
    result = derive_thermal_properties(baseline_case(parasitic_conductance_W_K=2e-4))
    assert result.total_conductance_W_K == pytest.approx(result.radiative_conductance_W_K + 2e-4)


def test_invalid_core_geometry_is_rejected():
    with pytest.raises(ValueError):
        derive_thermal_properties(baseline_case(core_diameter_m=0.010))
