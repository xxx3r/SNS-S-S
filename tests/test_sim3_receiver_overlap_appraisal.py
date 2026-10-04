"""Tests for the non-generating QST-SIM-0003 overlap appraisal."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from experiments.sim3_receiver_overlap_appraisal import INPUTS, build_appraisal


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs" / "qst_sim_0003" / "receiver_overlap_appraisal.json"


def test_overlap_appraisal_reproduces_checked_in_output() -> None:
    assert build_appraisal(ROOT) == json.loads(OUTPUT.read_text(encoding="utf-8"))


def test_overlap_appraisal_preserves_no_rerun_and_no_materiality_boundary() -> None:
    appraisal = build_appraisal(ROOT)
    assert appraisal["simulation_worlds_rerun"] == 0
    assert appraisal["new_world_count"] == 0
    assert appraisal["materiality_classification"] == "NOT_DEFINED_BY_ACCEPTED_ROUTE"
    assert appraisal["schedule_step_records_evaluated"] == 288


def test_overlap_counts_expose_phase_eclipse_interaction() -> None:
    cases = {case["case_id"]: case for case in build_appraisal(ROOT)["cases"]}
    expected = {
        "eclipse-0.05_phase-baseline": (115, 0, 0.37, 0.308333333),
        "eclipse-0.05_phase-antipodal": (87, 28, 0.283333333, 0.236111111),
        "eclipse-0.10_phase-baseline": (115, 0, 0.37, 0.308333333),
        "eclipse-0.10_phase-antipodal": (58, 57, 0.193333333, 0.161111111),
    }
    for case_id, values in expected.items():
        case = cases[case_id]
        assert case["receiver_visible_agent_step_count"] == 115
        assert case["receiver_visible_sunlit_agent_step_count"] == values[0]
        assert case["receiver_visible_eclipse_agent_step_count"] == values[1]
        assert case["accepted_delivered_total_Wh"] == values[2]
        assert case["accepted_host_service_fraction"] == values[3]


def test_overlap_appraisal_fails_closed_on_accepted_input_drift(tmp_path: Path) -> None:
    for _, (path, _) in INPUTS.items():
        target = tmp_path / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / path).read_bytes())
    phase_path = tmp_path / INPUTS["phase"][0]
    phase_path.write_bytes(phase_path.read_bytes() + b"\n")
    with pytest.raises(ValueError, match="accepted phase input hash mismatch"):
        build_appraisal(tmp_path)
