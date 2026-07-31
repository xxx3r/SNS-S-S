"""Compare bounded architectural escape routes after the packaged 10 mm falsifier."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.sim.thermal_geometry import ThermalGeometryCase, derive_thermal_properties
from src.sim.thermal_storage import (
    ThermalShadowScenario,
    capacity_fraction_at_temperature,
    scenario_with_result,
)


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _geometry_raw(config: dict, geometry_config: dict) -> dict:
    return next(
        case for case in geometry_config["cases"] if case["name"] == config["geometry_case"]
    )


def _base_load_W(config: dict) -> float:
    fixed = config["fixed"]
    return fixed["sleep_load_W"] + config["baseline"]["duty_cycle"] * (
        fixed["active_load_W"] - fixed["sleep_load_W"]
    )


def _scenario(
    config: dict,
    geometry_raw: dict,
    *,
    diameter_m: float,
    eclipse_duration_h: float,
    heater_power_W: float,
    nominal_battery_Wh: float,
) -> tuple[ThermalShadowScenario, dict]:
    baseline = config["baseline"]
    fixed = config["fixed"]
    geometry = ThermalGeometryCase(
        **{
            **geometry_raw,
            "name": f"escape_{diameter_m:g}",
            "outer_diameter_m": diameter_m,
            "core_diameter_m": diameter_m * baseline["core_diameter_ratio"],
            "effective_emissivity": baseline["effective_emissivity"],
            "parasitic_conductance_W_K": baseline["package_conductance_W_K"],
        }
    )
    derived = derive_thermal_properties(geometry)
    pcm_fraction = baseline["pcm_mass_fraction"]
    scenario = ThermalShadowScenario(
        eclipse_duration_h=eclipse_duration_h,
        time_step_s=fixed["time_step_s"],
        initial_temperature_K=baseline["initial_temperature_K"],
        environment_temperature_K=fixed["environment_temperature_K"],
        thermal_capacity_J_K=derived.thermal_capacity_J_K * (1.0 - pcm_fraction),
        thermal_conductance_W_K=derived.total_conductance_W_K,
        heater_threshold_K=fixed["heater_threshold_K"],
        heater_power_W=heater_power_W,
        base_load_W=_base_load_W(config),
        nominal_battery_Wh=nominal_battery_Wh,
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
    metadata = {
        "outer_diameter_m": diameter_m,
        "total_mass_kg": derived.total_mass_kg,
        "thermal_capacity_J_K": derived.thermal_capacity_J_K,
        "radiative_conductance_W_K": derived.radiative_conductance_W_K,
        "package_conductance_W_K": baseline["package_conductance_W_K"],
        "total_conductance_W_K": derived.total_conductance_W_K,
        "pcm_mass_kg": derived.total_mass_kg * pcm_fraction,
    }
    return scenario, metadata


def _localize_host_energy(scenario: ThermalShadowScenario, row: dict) -> dict:
    """Remove externally supplied heater energy from the node electrical ledger."""
    local_consumed_Wh = scenario.base_load_W * scenario.eclipse_duration_h
    fraction = capacity_fraction_at_temperature(scenario, row["minimum_temperature_K"])
    available_Wh = (
        scenario.nominal_battery_Wh
        * fraction
        * scenario.discharge_efficiency
        * (1.0 - scenario.reserve_fraction)
    )
    margin_Wh = available_Wh - local_consumed_Wh
    electrical_status = "PASS" if margin_Wh >= -1e-12 else "FAIL"
    row.update(
        local_consumed_energy_Wh=local_consumed_Wh,
        external_heater_energy_Wh=row["heater_energy_Wh"],
        electrical_margin_Wh=margin_Wh,
        electrical_status=electrical_status,
        status=(
            "PASS"
            if row["temperature_status"] == electrical_status == "PASS"
            else "FAIL"
        ),
    )
    return row


def build_rows(config: dict, geometry_config: dict) -> list[dict]:
    raw = _geometry_raw(config, geometry_config)
    baseline = config["baseline"]
    rows: list[dict] = []

    for diameter_m in config["routes"]["increased_seed_diameter"]["outer_diameter_m"]:
        volume_ratio = (diameter_m / baseline["outer_diameter_m"]) ** 3
        scenario, metadata = _scenario(
            config,
            raw,
            diameter_m=diameter_m,
            eclipse_duration_h=baseline["eclipse_duration_h"],
            heater_power_W=config["fixed"]["local_heater_power_W"],
            nominal_battery_Wh=baseline["nominal_battery_Wh"] * volume_ratio,
        )
        row = scenario_with_result(scenario)
        row.update(route="increased_seed_diameter", change_value=diameter_m, **metadata)
        rows.append(row)

    for duration_h in config["routes"]["shorter_eclipse"]["eclipse_duration_h"]:
        scenario, metadata = _scenario(
            config,
            raw,
            diameter_m=baseline["outer_diameter_m"],
            eclipse_duration_h=duration_h,
            heater_power_W=config["fixed"]["local_heater_power_W"],
            nominal_battery_Wh=baseline["nominal_battery_Wh"],
        )
        row = scenario_with_result(scenario)
        row.update(route="shorter_eclipse", change_value=duration_h, **metadata)
        rows.append(row)

    for external_heater_W in config["routes"]["host_assisted_thermal"][
        "external_heater_power_W"
    ]:
        scenario, metadata = _scenario(
            config,
            raw,
            diameter_m=baseline["outer_diameter_m"],
            eclipse_duration_h=baseline["eclipse_duration_h"],
            heater_power_W=external_heater_W,
            nominal_battery_Wh=baseline["nominal_battery_Wh"],
        )
        row = _localize_host_energy(scenario, scenario_with_result(scenario))
        row.update(route="host_assisted_thermal", change_value=external_heater_W, **metadata)
        rows.append(row)

    return rows


def _first_pass(rows: list[dict], route: str) -> dict | None:
    candidates = [row for row in rows if row["route"] == route and row["status"] == "PASS"]
    return candidates[0] if candidates else None


def summarize(rows: list[dict]) -> dict:
    routes = (
        "increased_seed_diameter",
        "shorter_eclipse",
        "host_assisted_thermal",
    )
    by_route = {}
    for route in routes:
        subset = [row for row in rows if row["route"] == route]
        by_route[route] = {
            "case_count": len(subset),
            "pass_count": sum(row["status"] == "PASS" for row in subset),
            "first_pass": _first_pass(rows, route),
            "cases": subset,
        }
    restored = [route for route in routes if by_route[route]["first_pass"] is not None]
    return {
        "case_count": len(rows),
        "baseline_status": rows[0]["status"],
        "routes_restoring_survival": restored,
        "by_route": by_route,
        "interpretation": (
            "Each route changes one declared architectural lever while preserving the same "
            "lumped thermal/electrical model. Results rank screening escape routes; they do "
            "not select flight hardware or establish qualification."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/qst_stor_0002_escape_routes.json"),
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("outputs/qst_stor_0002/architectural_escape_comparison.json"),
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
