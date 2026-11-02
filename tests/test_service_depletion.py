from dataclasses import replace
import pytest
from src.sim.service_depletion import simulate_service_depletion
from src.sim.thermal_storage import ThermalShadowScenario

def scenario(**updates):
    base=ThermalShadowScenario(eclipse_duration_h=0.1,time_step_s=60.0,
        initial_temperature_K=283.15,environment_temperature_K=220.0,
        thermal_capacity_J_K=50.0,thermal_conductance_W_K=0.005,
        heater_threshold_K=263.15,heater_power_W=0.08,base_load_W=0.01,
        nominal_battery_Wh=1.0,pcm_latent_heat_J_kg=180000.0,
        pcm_transition_temperature_K=273.15)
    return replace(base,**updates)

def test_abundant_energy_serves_full_fixed_policy():
    result=simulate_service_depletion(scenario())
    assert result.cutoff_time_s is None
    assert result.served_host_energy_Wh == pytest.approx(result.requested_host_energy_Wh)
    assert result.served_heater_energy_Wh == pytest.approx(result.requested_heater_energy_Wh)
    assert all(step.service_fraction == pytest.approx(1.0) for step in result.trace)

def test_zero_accessible_energy_serves_nothing():
    result=simulate_service_depletion(scenario(),initial_accessible_energy_Wh=0.0)
    assert result.served_host_energy_Wh == 0.0
    assert result.served_heater_energy_Wh == 0.0
    assert result.cutoff_time_s == 0.0
    assert all(step.service_fraction == 0.0 for step in result.trace)

def test_one_step_partial_depletion_is_proportional_and_closes_energy():
    s=scenario(eclipse_duration_h=1/60,initial_temperature_K=250.0)
    result=simulate_service_depletion(s,initial_accessible_energy_Wh=0.00075)
    step=result.trace[0]
    requested=(s.base_load_W+s.heater_power_W)/60
    assert step.service_fraction == pytest.approx(0.00075/requested)
    assert step.served_host_Wh == pytest.approx(0.00075*s.base_load_W/(s.base_load_W+s.heater_power_W))
    assert step.served_heater_Wh == pytest.approx(0.00075*s.heater_power_W/(s.base_load_W+s.heater_power_W))
    assert result.maximum_conservation_residual_Wh < 1e-12

def test_no_service_after_cutoff_and_no_negative_delivery():
    result=simulate_service_depletion(scenario(initial_temperature_K=250.0),initial_accessible_energy_Wh=0.00075)
    partial=next(i for i,x in enumerate(result.trace) if x.service_fraction < 1.0)
    assert all(x.service_fraction == 0.0 and x.served_host_Wh == 0.0 and x.served_heater_Wh == 0.0
               for x in result.trace[partial+1:])
    assert result.served_host_energy_Wh >= 0 and result.served_heater_energy_Wh >= 0

def test_thirty_and_sixty_second_steps_stay_within_frozen_development_tolerance():
    sixty=simulate_service_depletion(scenario(time_step_s=60.0,initial_temperature_K=260.0),initial_accessible_energy_Wh=0.004)
    thirty=simulate_service_depletion(scenario(time_step_s=30.0,initial_temperature_K=260.0),initial_accessible_energy_Wh=0.004)
    assert abs(sixty.served_host_energy_Wh-thirty.served_host_energy_Wh) <= 5e-5
    assert abs(sixty.final_temperature_K-thirty.final_temperature_K) <= 0.25
    assert sixty.maximum_conservation_residual_Wh < 1e-12
    assert thirty.maximum_conservation_residual_Wh < 1e-12

def test_fixture_override_cannot_create_energy():
    s=scenario()
    with pytest.raises(ValueError,match="model-derived limit"):
        simulate_service_depletion(s,initial_accessible_energy_Wh=2.0)
