from experiments.thermal_shadow_sweep import (
    baseline_survivor_report,
    build_sweep_rows,
    summarize,
)


def _config():
    return {
        "sweep": {
            "eclipse_duration_h": [0.5, 2.0],
            "initial_temperature_K": [273.15],
            "pcm_mass_kg": [0.0, 0.002],
            "duty_cycle": [0.25, 1.0],
        },
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


def _geometry():
    return {"cases": [
        {"name":"low","outer_diameter_m":0.01,"core_diameter_m":0.008,
         "core_density_kg_m3":1800.0,"core_specific_heat_J_kg_K":900.0,
         "shell_density_kg_m3":1200.0,"shell_specific_heat_J_kg_K":1000.0,
         "effective_emissivity":0.05,"linearization_temperature_K":270.0,
         "parasitic_conductance_W_K":0.0},
        {"name":"high","outer_diameter_m":0.01,"core_diameter_m":0.008,
         "core_density_kg_m3":1800.0,"core_specific_heat_J_kg_K":900.0,
         "shell_density_kg_m3":1200.0,"shell_specific_heat_J_kg_K":1000.0,
         "effective_emissivity":0.8,"linearization_temperature_K":270.0,
         "parasitic_conductance_W_K":0.001},
    ]}


def _baseline_geometry():
    return {"cases": [
        {"name":"baseline_surface","outer_diameter_m":0.01,"core_diameter_m":0.008,
         "core_density_kg_m3":1800.0,"core_specific_heat_J_kg_K":900.0,
         "shell_density_kg_m3":1200.0,"shell_specific_heat_J_kg_K":1000.0,
         "effective_emissivity":0.2,"linearization_temperature_K":270.0,
         "parasitic_conductance_W_K":0.0002},
    ]}


def test_sweep_is_cartesian_and_preserves_independent_statuses():
    rows = build_sweep_rows(_config(), _geometry())
    assert len(rows) == 2 * 2 * 1 * 2 * 2
    assert all(row["status"] in {"PASS", "FAIL"} for row in rows)
    assert all(row["temperature_status"] in {"PASS", "FAIL"} for row in rows)
    assert all(row["electrical_status"] in {"PASS", "FAIL"} for row in rows)


def test_higher_duty_cycle_never_improves_electrical_margin_for_matching_case():
    rows = build_sweep_rows(_config(), _geometry())
    for geometry in {"low", "high"}:
        for eclipse_h in {0.5, 2.0}:
            for pcm_kg in {0.0, 0.002}:
                matched = [r for r in rows if r["geometry_case"] == geometry
                           and r["eclipse_duration_h"] == eclipse_h
                           and r["pcm_mass_kg"] == pcm_kg]
                low = next(r for r in matched if r["duty_cycle"] == 0.25)
                high = next(r for r in matched if r["duty_cycle"] == 1.0)
                assert high["electrical_margin_Wh"] <= low["electrical_margin_Wh"]


def test_summary_counts_geometry_cases():
    rows = build_sweep_rows(_config(), _geometry())
    report = summarize(rows)
    assert report["case_count"] == len(rows)
    assert set(report["by_geometry"]) == {"low", "high"}


def test_baseline_survivor_report_exposes_declared_grid_boundary():
    config = _config()
    config["sweep"]["initial_temperature_K"] = [263.15, 273.15, 283.15]
    config["sweep"]["duty_cycle"] = [0.25, 0.5, 1.0]
    rows = build_sweep_rows(config, _baseline_geometry())
    report = baseline_survivor_report(rows)

    assert report["combined_pass_count"] == 6
    assert report["boundary"] == {
        "maximum_eclipse_duration_h": 0.5,
        "minimum_initial_temperature_K": 273.15,
        "minimum_pcm_mass_kg": 0.002,
        "passing_duty_cycles": [0.25, 0.5, 1.0],
        "heater_activation_observed": False,
    }
    assert all(case["pcm_mass_kg"] == 0.002 for case in report["survivors"])
    assert all(case["minimum_temperature_K"] == 273.15 for case in report["survivors"])
