import json
from pathlib import Path

from experiments.thermal_shadow_mass_budget import build_mass_budget_rows, summarize


def _load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_mass_budget_boundary_has_no_baseline_survivors() -> None:
    config = _load("configs/thermal_shadow_mass_budget.json")
    geometry = _load(config["geometry_config"])
    rows = build_mass_budget_rows(config, geometry)
    summary = summarize(rows)

    assert len(rows) == 63
    assert summary["combined_pass_count"] == 0
    assert summary["thermal_pass_count"] == 0
    assert summary["electrical_pass_count"] == 63
    assert summary["maximum_pcm_mass_kg"] <= summary["geometry_total_mass_kg"]


def test_pcm_mass_is_fraction_of_fixed_geometry_mass() -> None:
    config = _load("configs/thermal_shadow_mass_budget.json")
    geometry = _load(config["geometry_config"])
    rows = build_mass_budget_rows(config, geometry)

    for row in rows:
        expected_mass_kg = row["geometry_total_mass_kg"] * row["pcm_mass_fraction"]
        assert abs(row["pcm_mass_kg"] - expected_mass_kg) < 1e-15
        assert row["thermal_capacity_J_K"] > 0.0
