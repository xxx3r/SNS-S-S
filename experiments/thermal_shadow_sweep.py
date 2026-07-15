"""Run the geometry-derived QST-STOR-0002 shadow-survival sweep."""
from __future__ import annotations

import argparse
import csv
import itertools
import json
from pathlib import Path

from src.sim.thermal_geometry import ThermalGeometryCase, derive_thermal_properties
from src.sim.thermal_storage import ThermalShadowScenario, scenario_with_result


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def build_sweep_rows(config: dict, geometry_config: dict) -> list[dict]:
    fixed = config["fixed"]
    sweep = config["sweep"]
    rows: list[dict] = []
    for geometry_raw in geometry_config["cases"]:
        geometry = ThermalGeometryCase(**geometry_raw)
        derived = derive_thermal_properties(geometry)
        for eclipse_h, initial_K, pcm_kg, duty in itertools.product(
            sweep["eclipse_duration_h"],
            sweep["initial_temperature_K"],
            sweep["pcm_mass_kg"],
            sweep["duty_cycle"],
        ):
            base_load_W = fixed["sleep_load_W"] + duty * (
                fixed["active_load_W"] - fixed["sleep_load_W"]
            )
            scenario = ThermalShadowScenario(
                eclipse_duration_h=eclipse_h,
                time_step_s=fixed["time_step_s"],
                initial_temperature_K=initial_K,
                environment_temperature_K=fixed["environment_temperature_K"],
                thermal_capacity_J_K=derived.thermal_capacity_J_K,
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
                pcm_mass_kg=pcm_kg,
                pcm_latent_heat_J_kg=fixed["pcm_latent_heat_J_kg"],
                pcm_transition_temperature_K=fixed["pcm_transition_temperature_K"],
            )
            row = scenario_with_result(scenario)
            row.update(
                geometry_case=geometry.name,
                duty_cycle=duty,
                geometry_total_mass_kg=derived.total_mass_kg,
            )
            rows.append(row)
    return rows


def summarize(rows: list[dict]) -> dict:
    by_geometry: dict[str, dict] = {}
    for name in sorted({str(row["geometry_case"]) for row in rows}):
        selected = [row for row in rows if row["geometry_case"] == name]
        by_geometry[name] = {
            "case_count": len(selected),
            "thermal_pass_count": sum(row["temperature_status"] == "PASS" for row in selected),
            "electrical_pass_count": sum(row["electrical_status"] == "PASS" for row in selected),
            "combined_pass_count": sum(row["status"] == "PASS" for row in selected),
            "minimum_temperature_K": min(row["minimum_temperature_K"] for row in selected),
            "minimum_electrical_margin_Wh": min(row["electrical_margin_Wh"] for row in selected),
        }
    return {"case_count": len(rows), "by_geometry": by_geometry}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("configs/thermal_shadow_sweep.json"))
    parser.add_argument("--out", type=Path, default=Path("outputs/qst_stor_0002"))
    args = parser.parse_args()
    config = load_json(args.config)
    geometry_config = load_json(Path(config["geometry_config"]))
    rows = build_sweep_rows(config, geometry_config)
    args.out.mkdir(parents=True, exist_ok=True)
    csv_path = args.out / "geometry_coupled_sweep.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    summary_path = args.out / "geometry_coupled_sweep_summary.json"
    summary_path.write_text(json.dumps(summarize(rows), indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(rows)} cases to {csv_path}")
    print(f"wrote summary to {summary_path}")


if __name__ == "__main__":
    main()
