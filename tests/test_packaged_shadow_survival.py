from __future__ import annotations

import json
from pathlib import Path

from experiments.packaged_shadow_survival import build_rows, load_json, summarize


def _repo_config() -> tuple[dict, dict]:
    config = load_json(Path("configs/qst_stor_0002_packaged_shadow.json"))
    geometry = load_json(Path(config["geometry_config"]))
    return config, geometry


def test_packaged_shadow_sweep_is_closed_and_mass_admissible():
    config, geometry = _repo_config()
    rows = build_rows(config, geometry)

    assert len(rows) == 4 * 6
    assert {row["emissivity_case"] for row in rows} == {
        "BOL_target",
        "BOL_degraded",
        "EOL_moderate",
        "EOL_conservative",
    }
    assert all(
        row["package_parasitic_conductance_W_K"]
        == config["conservative_package_conductance_W_K"]
        for row in rows
    )
    assert all(row["pcm_mass_kg"] <= row["geometry_total_mass_kg"] for row in rows)


def test_packaged_shadow_uses_independent_failure_channels():
    config, geometry = _repo_config()
    rows = build_rows(config, geometry)
    summary = summarize(rows)

    assert summary["case_count"] == 24
    assert summary["electrical_pass_count"] >= summary["combined_pass_count"]
    assert summary["thermal_pass_count"] >= summary["combined_pass_count"]
    assert summary["eol_combined_pass_count"] == 0
    assert summary["gate"] == "FAIL"


def test_packaged_shadow_runner_writes_json(tmp_path):
    config, geometry = _repo_config()
    summary = summarize(build_rows(config, geometry))
    output = tmp_path / "summary.json"
    output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["case_count"] == 24
    assert set(payload["by_emissivity_case"]) == {
        "BOL_target",
        "BOL_degraded",
        "EOL_moderate",
        "EOL_conservative",
    }
