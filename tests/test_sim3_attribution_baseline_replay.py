"""Tests for the one-world SIM3 attribution measurement upgrade."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from experiments.sim3_attribution_baseline_replay import load_and_run, run_replay


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "qst_sim_0003_attribution_baseline_replay.json"


def test_replay_reproduces_legacy_summary_before_reporting_partition() -> None:
    result = load_and_run(CONFIG, ROOT)
    committed = json.loads(
        (ROOT / "outputs/qst_sim_0003/attribution_baseline_replay.json").read_text(
            encoding="utf-8"
        )
    )
    assert result == committed
    assert result["new_world_count"] == 1
    assert result["agent_step_records"] == 720
    assert result["legacy_reproduction"]["status"] == "MATCH"
    assert all(result["legacy_reproduction"]["field_matches"].values())

    measurement = result["measurement"]
    partition_total = sum(
        amount
        for role_amounts in measurement["delivered_energy_by_role_state_Wh"].values()
        for amount in role_amounts.values()
    )
    assert partition_total == pytest.approx(measurement["delivered_total_Wh"])
    assert measurement["delivery_partition_identity_holds"] is True


def test_replay_fails_closed_on_baseline_or_grid_mutation() -> None:
    spec = json.loads(CONFIG.read_text(encoding="utf-8"))
    baseline_bytes = (ROOT / spec["baseline_artifact"]).read_bytes()

    mutated = copy.deepcopy(spec)
    mutated["fixture"]["environment"]["receiver_visibility_fraction"] = 1.0
    with pytest.raises(ValueError, match="coordinates"):
        run_replay(mutated, baseline_bytes)

    mutated = copy.deepcopy(spec)
    mutated["baseline_artifact_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="hash mismatch"):
        run_replay(mutated, baseline_bytes)


def test_replay_fails_closed_before_interpretation_on_legacy_drift() -> None:
    spec = json.loads(CONFIG.read_text(encoding="utf-8"))
    baseline = json.loads((ROOT / spec["baseline_artifact"]).read_text(encoding="utf-8"))
    baseline["cases"][1]["metrics"]["delivered_total_Wh"] += 0.01
    mutated_bytes = json.dumps(baseline, indent=2).encode("utf-8")
    mutated_spec = copy.deepcopy(spec)
    import hashlib

    mutated_spec["baseline_artifact_sha256"] = hashlib.sha256(mutated_bytes).hexdigest()
    with pytest.raises(ValueError, match="legacy summary mismatch"):
        run_replay(mutated_spec, mutated_bytes)
