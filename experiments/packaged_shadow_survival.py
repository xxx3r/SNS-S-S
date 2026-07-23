"""Propagate package conductance and BOL/EOL emissivity through shadow survival."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.sim.thermal_geometry import ThermalGeometryCase, derive_thermal_properties
from src.sim.thermal_storage import ThermalShadowScenario, scenario_with_result


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def build_rows(config: dict, geometry_config: dict) -> list[dict]:
    geometry_raw = next(
        case for case in geometry_config["cases"] if case["name"] == config["geometry_case"]
    )
    fixed = config["fixed"]
    rows: list[dict] = []

    for emissivity_case in config["effective_emissivity_cases"]:
        geometry = ThermalGeometryCase(
            **{
                **geometry_raw,
                "effective_emissivity": emissivity_case["effective_emissivity"],
                "parasitic_conductance_W_K": config[
                    "conservative_package_conductance_W_K"
                ],
            }
        )
        derived = derive_thermal_properties(geometry)

        for pcm_fraction in config["pcm_mass_fraction"]:
            if not 0.0 <= pcm_fraction < 1.0:
                raise ValueError("pcm_mass_fraction must be in [0, 1)")
            pcm_mass_kg = derived.total_mass_kg * pcm_fraction
            sensible_capacity_J_K = derived.thermal_capacity_J_K * (1.0 - pcm_fraction)
            base_load_W = fixed["sleep_load_W"] + config["duty_cycle"] * (
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
                minimum_operating_temperature_K=fixed[
                    "minimum_operating_temperature_K"
                ],
                pcm_mass_kg=pcm_mass_kg,
                pcm_latent_heat_J_kg=fixed["pcm_latent_heat_J_kg"],
                pcm_transition_temperature_K=fixed[
                    "pcm_transition_temperature_K"
                ],
            )
            row = scenario_with_result(scenario)
            row.update(
                emissivity_case=emissivity_case["name"],
                emissivity_evidence_class=emissivity_case["evidence_class"],
                effective_emissivity=emissivity_case["effective_emissivity"],
                package_parasitic_conductance_W_K=config[
                    "conservative_package_conductance_W_K"
                ],
                radiative_conductance_W_K=derived.radiative_conductance_W_K,
                total_conductance_W_K=derived.total_conductance_W_K,
                geometry_total_mass_kg=derived.total_mass_kg,
                pcm_mass_fraction=pcm_fraction,
                duty_cycle=config["duty_cycle"],
            )
            rows.append(row)
    return rows


def summarize(rows: list[dict]) -> dict:
    by_case: dict[str, dict] = {}
    for name in sorted({row["emissivity_case"] for row in rows}):
        subset = [row for row in rows if row["emissivity_case"] == name]
        survivors = [row for row in subset if row["status"] == "PASS"]
        by_case[name] = {
            "case_count": len(subset),
            "combined_pass_count": len(survivors),
            "thermal_pass_count": sum(
                row["temperature_status"] == "PASS" for row in subset
            ),
            "electrical_pass_count": sum(
                row["electrical_status"] == "PASS" for row in subset
            ),
            "minimum_temperature_K": min(row["minimum_temperature_K"] for row in subset),
            "minimum_electrical_margin_Wh": min(
                row["electrical_margin_Wh"] for row in subset
            ),
            "survivors": survivors,
        }

    survivors = [row for row in rows if row["status"] == "PASS"]
    eol_names = {"EOL_moderate", "EOL_conservative"}
    eol_survivors = [row for row in survivors if row["emissivity_case"] in eol_names]
    return {
        "case_count": len(rows),
        "combined_pass_count": len(survivors),
        "thermal_pass_count": sum(row["temperature_status"] == "PASS" for row in rows),
        "electrical_pass_count": sum(row["electrical_status"] == "PASS" for row in rows),
        "eol_combined_pass_count": len(eol_survivors),
        "by_emissivity_case": by_case,
        "survivors": survivors,
        "gate": "HOLD" if eol_survivors else "FAIL",
        "interpretation": (
            "The conservative package conductance is propagated independently from the "
            "declared BOL/EOL emissivity proxies. PASS is a model result only; promotion "
            "requires package-level environmental evidence."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/qst_stor_0002_packaged_shadow.json"),
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("outputs/qst_stor_0002/packaged_shadow_summary.json"),
    )
    args = parser.parse_args()
    config = load_json(args.config)
    geometry_config = load_json(Path(config["geometry_config"]))
    summary = summarize(build_rows(config, geometry_config))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {summary['case_count']} cases to {args.out}")


if __name__ == "__main__":
    main()
