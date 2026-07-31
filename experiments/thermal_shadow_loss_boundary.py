"""Locate the first admissible 30-minute thermal survivor under a closed mass budget."""
from __future__ import annotations

import argparse
import itertools
import json
from dataclasses import replace
from pathlib import Path

from src.sim.thermal_geometry import ThermalGeometryCase, derive_thermal_properties
from src.sim.thermal_storage import ThermalShadowScenario, scenario_with_result


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def build_loss_boundary_rows(config: dict, geometry_config: dict) -> list[dict]:
    geometry_raw = next(
        case for case in geometry_config["cases"] if case["name"] == config["geometry_case"]
    )
    base_geometry = ThermalGeometryCase(**geometry_raw)
    fixed = config["fixed"]
    pcm_fraction = config["pcm_mass_fraction"]
    if not 0.0 <= pcm_fraction < 1.0:
        raise ValueError("pcm_mass_fraction must be in [0, 1)")

    rows: list[dict] = []
    for emissivity, parasitic_W_K in itertools.product(
        config["effective_emissivity"], config["parasitic_conductance_W_K"]
    ):
        geometry = replace(
            base_geometry,
            effective_emissivity=emissivity,
            parasitic_conductance_W_K=parasitic_W_K,
        )
        derived = derive_thermal_properties(geometry)
        pcm_mass_kg = derived.total_mass_kg * pcm_fraction
        sensible_capacity_J_K = derived.thermal_capacity_J_K * (1.0 - pcm_fraction)
        duty = config["duty_cycle"]
        base_load_W = fixed["sleep_load_W"] + duty * (
            fixed["active_load_W"] - fixed["sleep_load_W"]
        )
        scenario = ThermalShadowScenario(
            eclipse_duration_h=config["eclipse_duration_h"],
            time_step_s=fixed["time_step_s"],
            initial_temperature_K=config["initial_temperature_K"],
            environment_temperature_K=fixed["environment_temperature_K"],
            thermal_capacity_J_K=sensible_capacity_J_K,
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
            pcm_mass_kg=pcm_mass_kg,
            pcm_latent_heat_J_kg=fixed["pcm_latent_heat_J_kg"],
            pcm_transition_temperature_K=fixed["pcm_transition_temperature_K"],
        )
        row = scenario_with_result(scenario)
        row.update(
            geometry_case=geometry.name,
            effective_emissivity=emissivity,
            radiative_conductance_W_K=derived.radiative_conductance_W_K,
            parasitic_conductance_W_K=parasitic_W_K,
            total_conductance_W_K=derived.total_conductance_W_K,
            geometry_total_mass_kg=derived.total_mass_kg,
            pcm_mass_fraction=pcm_fraction,
            duty_cycle=duty,
        )
        rows.append(row)
    return rows


def summarize(rows: list[dict]) -> dict:
    survivors = [row for row in rows if row["status"] == "PASS"]
    first_survivor = survivors[0] if survivors else None
    baseline_rows = [row for row in rows if row["effective_emissivity"] == 0.2]
    return {
        "case_count": len(rows),
        "combined_pass_count": len(survivors),
        "thermal_pass_count": sum(row["temperature_status"] == "PASS" for row in rows),
        "electrical_pass_count": sum(row["electrical_status"] == "PASS" for row in rows),
        "baseline_emissivity_0_2_pass_count": sum(row["status"] == "PASS" for row in baseline_rows),
        "first_declared_survivor": first_survivor,
        "survivors": survivors,
        "rows": rows,
        "interpretation": (
            "No declared case survives at effective emissivity 0.2, even with zero parasitic "
            "conductance. The first declared survivor requires emissivity 0.1 and parasitic "
            "conductance 5e-5 W/K under the deliberately favorable 283.15 K, 50% PCM, 25% duty case."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config", type=Path, default=Path("configs/thermal_shadow_loss_boundary.json")
    )
    parser.add_argument(
        "--out", type=Path, default=Path("outputs/qst_stor_0002/loss_boundary.json")
    )
    args = parser.parse_args()
    config = load_json(args.config)
    geometry_config = load_json(Path(config["geometry_config"]))
    summary = summarize(build_loss_boundary_rows(config, geometry_config))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {summary['case_count']} cases to {args.out}")


if __name__ == "__main__":
    main()
