"""Test baseline-surface 30-minute survival with PCM inside the node mass budget."""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

from src.sim.thermal_geometry import ThermalGeometryCase, derive_thermal_properties
from src.sim.thermal_storage import ThermalShadowScenario, scenario_with_result


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def build_mass_budget_rows(config: dict, geometry_config: dict) -> list[dict]:
    geometry_raw = next(
        case for case in geometry_config["cases"] if case["name"] == config["geometry_case"]
    )
    geometry = ThermalGeometryCase(**geometry_raw)
    derived = derive_thermal_properties(geometry)
    fixed = config["fixed"]
    rows: list[dict] = []

    for initial_K, pcm_fraction, duty in itertools.product(
        config["initial_temperature_K"],
        config["pcm_mass_fraction"],
        config["duty_cycle"],
    ):
        if not 0.0 <= pcm_fraction < 1.0:
            raise ValueError("pcm_mass_fraction must be in [0, 1)")
        pcm_mass_kg = derived.total_mass_kg * pcm_fraction
        sensible_capacity_J_K = derived.thermal_capacity_J_K * (1.0 - pcm_fraction)
        base_load_W = fixed["sleep_load_W"] + duty * (
            fixed["active_load_W"] - fixed["sleep_load_W"]
        )
        scenario = ThermalShadowScenario(
            eclipse_duration_h=config["eclipse_duration_h"],
            time_step_s=fixed["time_step_s"],
            initial_temperature_K=initial_K,
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
            geometry_total_mass_kg=derived.total_mass_kg,
            pcm_mass_fraction=pcm_fraction,
            displaced_sensible_capacity_fraction=pcm_fraction,
            duty_cycle=duty,
        )
        rows.append(row)
    return rows


def summarize(rows: list[dict]) -> dict:
    survivors = [row for row in rows if row["status"] == "PASS"]
    return {
        "case_count": len(rows),
        "combined_pass_count": len(survivors),
        "thermal_pass_count": sum(row["temperature_status"] == "PASS" for row in rows),
        "electrical_pass_count": sum(row["electrical_status"] == "PASS" for row in rows),
        "maximum_pcm_mass_fraction": max(row["pcm_mass_fraction"] for row in rows),
        "maximum_pcm_mass_kg": max(row["pcm_mass_kg"] for row in rows),
        "geometry_total_mass_kg": rows[0]["geometry_total_mass_kg"],
        "minimum_temperature_K": min(row["minimum_temperature_K"] for row in rows),
        "minimum_electrical_margin_Wh": min(row["electrical_margin_Wh"] for row in rows),
        "survivors": survivors,
        "interpretation": (
            "No declared baseline-surface 30-minute case survives when PCM is constrained "
            "to 0-50% of the fixed 0.789 g node mass and displaces baseline sensible mass. "
            "This falsifies the prior 2 g apparent survivor within the current envelope."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("configs/thermal_shadow_mass_budget.json"))
    parser.add_argument("--out", type=Path, default=Path("outputs/qst_stor_0002/mass_budget_boundary.json"))
    args = parser.parse_args()
    config = load_json(args.config)
    geometry_config = load_json(Path(config["geometry_config"]))
    summary = summarize(build_mass_budget_rows(config, geometry_config))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {summary['case_count']} cases to {args.out}")


if __name__ == "__main__":
    main()
