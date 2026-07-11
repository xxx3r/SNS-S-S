from __future__ import annotations

from dataclasses import replace

import pytest

from src.sim.thermal_storage import (
    ThermalShadowScenario,
    capacity_fraction_at_temperature,
    simulate_thermal_shadow,
)


def baseline_scenario(**overrides: float) -> ThermalShadowScenario:
    scenario = ThermalShadowScenario(
        eclipse_duration_h=2.0,
        time_step_s=60.0,
        initial_temperature_K=283.15,
        environment_temperature_K=220.0,
        thermal_capacity_J_K=120.0,
        thermal_conductance_W_K=0.002,
        heater_threshold_K=263.15,
        heater_power_W=0.08,
        base_load_W=0.01,
        nominal_battery_Wh=0.50,
        pcm_mass_kg=0.0,
        pcm_latent_heat_J_kg=180_000.0,
        pcm_transition_temperature_K=273.15,
    )
    return replace(scenario, **overrides)


def test_capacity_derating_is_bounded_and_linear() -> None:
    scenario = baseline_scenario()
    assert capacity_fraction_at_temperature(scenario, 300.0) == pytest.approx(1.0)
    assert capacity_fraction_at_temperature(scenario, 243.15) == pytest.approx(0.5)
    assert capacity_fraction_at_temperature(scenario, 268.15) == pytest.approx(0.75)


def test_pcm_preserves_temperature_and_reduces_heater_energy() -> None:
    without_pcm = simulate_thermal_shadow(baseline_scenario())
    with_pcm = simulate_thermal_shadow(baseline_scenario(pcm_mass_kg=0.002))

    assert with_pcm.minimum_temperature_K > without_pcm.minimum_temperature_K
    assert with_pcm.heater_energy_Wh < without_pcm.heater_energy_Wh
    assert with_pcm.pcm_latent_energy_used_J > 0.0


def test_pcm_cannot_rescue_undersized_battery() -> None:
    result = simulate_thermal_shadow(
        baseline_scenario(pcm_mass_kg=0.010, nominal_battery_Wh=0.015)
    )

    assert result.temperature_status == "PASS"
    assert result.electrical_status == "FAIL"
    assert result.status == "FAIL"


def test_temperature_and_electrical_status_are_separate() -> None:
    result = simulate_thermal_shadow(
        baseline_scenario(
            initial_temperature_K=250.0,
            environment_temperature_K=210.0,
            minimum_operating_temperature_K=245.0,
            heater_power_W=0.0,
            nominal_battery_Wh=1.0,
        )
    )

    assert result.temperature_status == "FAIL"
    assert result.electrical_status == "PASS"
    assert result.status == "FAIL"


def test_invalid_scenario_is_rejected() -> None:
    with pytest.raises(ValueError, match="eclipse_duration_h"):
        simulate_thermal_shadow(baseline_scenario(eclipse_duration_h=0.0))
