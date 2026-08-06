from __future__ import annotations

import json
from pathlib import Path

from automation.receipts import validate_run_receipt
from experiments.mission_dependency_config_check import build_check, load_config_cases


RESULT_PATH = Path(
    "outputs/qst_stor_0002/mission_dependency_config_check.json"
)


def test_versioned_allocation_config_matches_accepted_inputs():
    cases = load_config_cases()
    result = build_check()

    assert [case["name"] for case in cases] == [
        "measured_fast_rotator_surface",
        "active_sunward_hosted",
    ]
    assert result["matches_accepted_inputs"] is True
    assert result["mismatches"] == []


def test_config_check_artifact_is_bound_to_immutable_receipt():
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    run_id = result["run_id"]
    receipt_path = Path("automation/runs/2026/08") / f"{run_id}.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))

    validate_run_receipt(receipt)
    assert receipt["run_id"] == run_id
    assert receipt["source_commit"] == result["source_commit"]
    assert receipt["terminal_state"] == "DONE_WITH_LIMITATIONS"
    assert any(
        check["name"] == "P1 config reproducibility"
        and check["status"] == "passed"
        for check in receipt["checks"]
    )
    artifact_paths = {
        artifact["path"] if isinstance(artifact, dict) else artifact
        for artifact in receipt["artifacts"]
    }
    assert str(RESULT_PATH) in artifact_paths
