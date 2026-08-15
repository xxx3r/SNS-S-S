"""Quantify QST-STOR-0002 fast-rotator scarcity and thermal constraint cost."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from src.sim.thermal_geometry import ThermalGeometryCase, derive_thermal_properties
from src.sim.thermal_storage import ThermalShadowScenario, scenario_with_result


STEFAN_BOLTZMANN_W_M2_K4 = 5.670374419e-8


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def required_screen_count(probability: float, confidence: float) -> int:
    """Return independent screens required to reach the declared discovery confidence."""
    if not 0.0 < probability <= 1.0:
        raise ValueError("target availability probability must be in (0, 1]")
    if not 0.0 < confidence < 1.0:
        raise ValueError("discovery confidence must be in (0, 1)")
    if probability == 1.0:
        return 1
    return math.ceil(math.log1p(-confidence) / math.log1p(-probability))


def _thermal_row(config: dict, geometry_raw: dict, emissivity: float) -> dict:
    fixed = config["fixed"]
    geometry = ThermalGeometryCase(
        **{
            **geometry_raw,
            "effective_emissivity": emissivity,
            "parasitic_conductance_W_K": config[
                "conservative_package_conductance_W_K"
            ],
        }
    )
    derived = derive_thermal_properties(geometry)
    pcm_fraction = config["pcm_mass_fraction"]
    base_load_W = fixed["sleep_load_W"] + config["duty_cycle"] * (
        fixed["active_load_W"] - fixed["sleep_load_W"]
    )
    scenario = ThermalShadowScenario(
        eclipse_duration_h=config["rotation_limit_h"] / 2.0,
        time_step_s=fixed["time_step_s"],
        initial_temperature_K=config["initial_temperature_K"],
        environment_temperature_K=config["environment_temperature_K"],
        thermal_capacity_J_K=derived.thermal_capacity_J_K * (1.0 - pcm_fraction),
        thermal_conductance_W_K=derived.total_conductance_W_K,
        heater_threshold_K=fixed["heater_threshold_K"],
        heater_power_W=fixed["heater_power_W"],
        base_load_W=base_load_W,
        nominal_battery_Wh=fixed["nominal_battery_Wh"],
        discharge_efficiency=fixed["discharge_efficiency"],
        reserve_fraction=fixed["reserve_fraction"],
        derating_reference_K=fixed["derating_reference_K"],
        derating_floor_K=fixed["derating_floor_K"],
        minimum_capacity_fraction=fixed["minimum_capacity_fraction"],
        minimum_operating_temperature_K=fixed["minimum_operating_temperature_K"],
        pcm_mass_kg=derived.total_mass_kg * pcm_fraction,
        pcm_latent_heat_J_kg=fixed["pcm_latent_heat_J_kg"],
        pcm_transition_temperature_K=fixed["pcm_transition_temperature_K"],
    )
    shadow = scenario_with_result(scenario)
    radiating_area_m2 = math.pi * geometry.outer_diameter_m**2
    rejection_budget_W = (
        emissivity
        * STEFAN_BOLTZMANN_W_M2_K4
        * radiating_area_m2
        * (
            config["thermal_reference_K"] ** 4
            - config["environment_temperature_K"] ** 4
        )
    )
    illuminated = [
        {
            "synthetic_absorbed_heat_load_W": load_W,
            "status_at_thermal_reference": (
                "PASS" if load_W <= rejection_budget_W + 1e-12 else "FAIL"
            ),
            "dual_shadow_and_illuminated_status": (
                "PASS"
                if shadow["status"] == "PASS"
                and load_W <= rejection_budget_W + 1e-12
                else "FAIL"
            ),
        }
        for load_W in config["synthetic_absorbed_heat_load_W"]
    ]
    return {
        "effective_emissivity": emissivity,
        "inherited_shadow_duration_h": scenario.eclipse_duration_h,
        "shadow_status": shadow["status"],
        "minimum_shadow_temperature_K": shadow["minimum_temperature_K"],
        "shadow_electrical_margin_Wh": shadow["electrical_margin_Wh"],
        "radiative_conductance_W_K": derived.radiative_conductance_W_K,
        "conservative_package_conductance_W_K": config[
            "conservative_package_conductance_W_K"
        ],
        "total_conductance_W_K": derived.total_conductance_W_K,
        "illuminated_model": "exact outer-sphere radiation only; package conductance is eclipse-only",
        "illuminated_radiating_area_m2": radiating_area_m2,
        "illuminated_radiative_rejection_budget_at_reference_W": rejection_budget_W,
        "illuminated_load_cases": illuminated,
        "dual_pass_count": sum(
            case["dual_shadow_and_illuminated_status"] == "PASS"
            for case in illuminated
        ),
    }


def build_artifact(config: dict, geometry_config: dict) -> dict:
    geometry_raw = next(
        case
        for case in geometry_config["cases"]
        if case["name"] == config["geometry_case"]
    )
    availability = []
    for probability in config["target_availability_probability"]:
        required = required_screen_count(probability, config["discovery_confidence"])
        availability.append(
            {
                "synthetic_target_availability_probability": probability,
                "screened_targets_required": required,
                "status": (
                    "WITHIN_SCREENING_BUDGET"
                    if required <= config["max_screened_targets"]
                    else "EXCEEDS_SCREENING_BUDGET"
                ),
            }
        )

    thermal = [
        _thermal_row(config, geometry_raw, emissivity)
        for emissivity in config["effective_emissivity"]
    ]
    availability_survives = any(
        row["status"] == "WITHIN_SCREENING_BUDGET" for row in availability
    )
    thermal_survives = any(row["dual_pass_count"] > 0 for row in thermal)
    falsifier_triggered = not (availability_survives and thermal_survives)
    return {
        "schema": "sns.qst-stor-0002.fast-rotator-constraint-cost.v1",
        "quest_id": "QST-STOR-0002",
        "measurement_only": True,
        "rotation_constraint": {
            "maximum_rotation_period_h": config["rotation_limit_h"],
            "inherited_maximum_shadow_h": config["rotation_limit_h"] / 2.0,
        },
        "target_availability_screen": {
            "discovery_confidence": config["discovery_confidence"],
            "max_screened_targets": config["max_screened_targets"],
            "cases": availability,
        },
        "thermal_screen": {
            "thermal_reference_K": config["thermal_reference_K"],
            "environment_temperature_K": config["environment_temperature_K"],
            "cases": thermal,
        },
        "falsifier": {
            "triggered": falsifier_triggered,
            "status": (
                "FALSIFIED_ON_DECLARED_GRID"
                if falsifier_triggered
                else "CONDITIONAL_SCREENING_SURVIVOR"
            ),
            "rule": config["falsifier"],
        },
        "uncertainty": [
            config["assumption_classes"]["target_availability_probability"],
            config["assumption_classes"]["synthetic_absorbed_heat_load_W"],
            "Illuminated rejection uses exact outer-sphere radiation at the declared reference temperature; the accepted package conductance remains confined to eclipse leakage.",
            "Rotation period alone omits irregular shape, terrain, latitude, tumbling, and seasonal Sun geometry.",
        ],
        "nonclaims": [
            "No target-population frequency is inferred.",
            "No surface or hosted architecture is selected or recommended.",
            "No optical absorptivity, material qualification, or external mission evidence is introduced.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/qst_stor_0002_fast_rotator_constraint_cost.json"),
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("outputs/qst_stor_0002/fast_rotator_constraint_cost.json"),
    )
    args = parser.parse_args()
    config = load_json(args.config)
    geometry_config = load_json(Path(config["geometry_config"]))
    artifact = build_artifact(config, geometry_config)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(artifact, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(args.out)


if __name__ == "__main__":
    main()
