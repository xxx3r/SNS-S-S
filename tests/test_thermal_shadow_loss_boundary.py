from experiments.thermal_shadow_loss_boundary import build_loss_boundary_rows, summarize


def test_loss_boundary_finds_first_declared_survivor():
    config = {
        "geometry_case": "baseline_surface",
        "eclipse_duration_h": 0.5,
        "initial_temperature_K": 283.15,
        "pcm_mass_fraction": 0.5,
        "duty_cycle": 0.25,
        "effective_emissivity": [0.2, 0.15, 0.1, 0.075, 0.05, 0.02],
        "parasitic_conductance_W_K": [0.0002, 0.00015, 0.0001, 0.000075, 0.00005, 0.000025, 0.0],
        "fixed": {
            "time_step_s": 5.0,
            "environment_temperature_K": 3.0,
            "heater_threshold_K": 253.15,
            "heater_power_W": 0.02,
            "sleep_load_W": 0.001,
            "active_load_W": 0.004,
            "nominal_battery_Wh": 0.25,
            "discharge_efficiency": 0.9,
            "reserve_fraction": 0.2,
            "derating_reference_K": 293.15,
            "derating_floor_K": 243.15,
            "minimum_capacity_fraction": 0.5,
            "minimum_operating_temperature_K": 233.15,
            "pcm_latent_heat_J_kg": 180000.0,
            "pcm_transition_temperature_K": 273.15,
        },
    }
    geometry_config = {
        "cases": [{
            "name": "baseline_surface",
            "outer_diameter_m": 0.01,
            "core_diameter_m": 0.008,
            "core_density_kg_m3": 1800.0,
            "core_specific_heat_J_kg_K": 900.0,
            "shell_density_kg_m3": 1200.0,
            "shell_specific_heat_J_kg_K": 1000.0,
            "effective_emissivity": 0.2,
            "linearization_temperature_K": 270.0,
            "parasitic_conductance_W_K": 0.0002,
        }]
    }

    summary = summarize(build_loss_boundary_rows(config, geometry_config))

    assert summary["case_count"] == 42
    assert summary["baseline_emissivity_0_2_pass_count"] == 0
    first = summary["first_declared_survivor"]
    assert first["effective_emissivity"] == 0.1
    assert first["parasitic_conductance_W_K"] == 0.00005
    assert first["minimum_temperature_K"] >= 233.15
    assert all(row["electrical_margin_Wh"] > 0 for row in summary["survivors"])


def test_loss_boundary_rejects_invalid_pcm_fraction():
    config = {
        "geometry_case": "baseline_surface",
        "eclipse_duration_h": 0.5,
        "initial_temperature_K": 283.15,
        "pcm_mass_fraction": 1.0,
        "duty_cycle": 0.25,
        "effective_emissivity": [0.1],
        "parasitic_conductance_W_K": [0.0],
        "fixed": {},
    }
    geometry_config = {"cases": [{"name": "baseline_surface"}]}

    try:
        build_loss_boundary_rows(config, geometry_config)
    except (TypeError, ValueError):
        pass
    else:
        raise AssertionError("expected invalid PCM fraction to fail")
