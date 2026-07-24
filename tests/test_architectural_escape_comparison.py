from __future__ import annotations

import json
from pathlib import Path

import pytest

from experiments.architectural_escape_comparison import build_rows, summarize


ROOT = Path(__file__).resolve().parents[1]


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _summary() -> dict:
    config = _load(ROOT / "configs/qst_stor_0002_escape_routes.json")
    geometry = _load(ROOT / config["geometry_config"])
    return summarize(build_rows(config, geometry))


def test_escape_comparison_preserves_falsified_baseline_and_three_routes():
    summary = _summary()

    assert summary["case_count"] == 17
    assert summary["baseline_status"] == "FAIL"
    assert set(summary["by_route"]) == {
        "increased_seed_diameter",
        "shorter_eclipse",
        "host_assisted_thermal",
    }
    rows = [
        row
        for route in summary["by_route"].values()
        for row in route["cases"]
    ]
    assert all("minimum_temperature_K" in row for row in rows)
    assert all("electrical_margin_Wh" in row for row in rows)
    assert all("total_mass_kg" in row for row in rows)
    assert all("total_conductance_W_K" in row for row in rows)


def test_each_route_is_monotonic_in_its_declared_intervention():
    summary = _summary()
    diameter = summary["by_route"]["increased_seed_diameter"]["cases"]
    assert [row["change_value"] for row in diameter] == sorted(
        row["change_value"] for row in diameter
    )
    assert diameter[-1]["total_mass_kg"] > diameter[0]["total_mass_kg"]
    assert diameter[-1]["thermal_capacity_J_K"] > diameter[0]["thermal_capacity_J_K"]

    eclipse = summary["by_route"]["shorter_eclipse"]["cases"]
    assert [row["change_value"] for row in eclipse] == sorted(
        (row["change_value"] for row in eclipse), reverse=True
    )
    assert eclipse[-1]["consumed_energy_Wh"] < eclipse[0]["consumed_energy_Wh"]

    host = summary["by_route"]["host_assisted_thermal"]["cases"]
    assert [row["change_value"] for row in host] == sorted(
        row["change_value"] for row in host
    )
    assert all(row["external_heater_energy_Wh"] >= 0.0 for row in host)
    assert all(row["local_consumed_energy_Wh"] > 0.0 for row in host)


def test_first_surviving_thresholds_are_pinned():
    summary = _summary()

    assert set(summary["routes_restoring_survival"]) == {
        "increased_seed_diameter",
        "shorter_eclipse",
        "host_assisted_thermal",
    }
    assert summary["by_route"]["increased_seed_diameter"]["first_pass"][
        "change_value"
    ] == pytest.approx(0.015)
    assert summary["by_route"]["shorter_eclipse"]["first_pass"][
        "change_value"
    ] == pytest.approx(0.25)
    assert summary["by_route"]["host_assisted_thermal"]["first_pass"][
        "change_value"
    ] == pytest.approx(0.08)

    assert "screening" in summary["interpretation"]
    assert "qualification" in summary["interpretation"]
