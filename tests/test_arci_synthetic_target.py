from __future__ import annotations

import json
from pathlib import Path

from experiments.arci_example import build_payload


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "arci_synthetic_target.json"
OUTPUT = ROOT / "outputs" / "qst_arci_0001" / "synthetic_target_sensitivity.json"


def test_synthetic_arci_sensitivity_reproduces_versioned_artifact():
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    expected = json.loads(OUTPUT.read_text(encoding="utf-8"))

    assert build_payload(config) == expected
    assert expected["synthetic"] is True
    assert expected["sensitivity"]["scenario_count"] == 28
    assert expected["sensitivity"]["major_grade_reversal"] is False
    assert expected["sensitivity"]["weight_observed_grades"] == ["research-only"]
    assert expected["sensitivity"]["confidence_observed_grades"] == ["research-only"]
    assert expected["next_measurement"]["dimension"] == "surface_operations"


def test_synthetic_arci_keeps_evidence_missingness_and_score_confidence_separate():
    payload = build_payload(json.loads(CONFIG.read_text(encoding="utf-8")))

    assert payload["baseline"]["score"] > payload["baseline"]["confidence"]
    assert payload["missing_dimensions"] == [
        "composition",
        "recoverability",
        "surface_operations",
        "market_mission_value",
    ]
    assert all(
        {"evidence_type", "evidence_ladder_rung", "missing_data"} == set(evidence)
        for evidence in payload["evidence"].values()
    )


def test_synthetic_arci_rejects_unbounded_or_non_synthetic_fixture():
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    config["synthetic"] = False
    try:
        build_payload(config)
    except ValueError as exc:
        assert "explicitly synthetic" in str(exc)
    else:
        raise AssertionError("non-synthetic target was accepted")

    config["synthetic"] = True
    config["sensitivity"]["weight_relative_perturbation"] = 0.5
    try:
        build_payload(config)
    except ValueError as exc:
        assert "weight perturbation" in str(exc)
    else:
        raise AssertionError("unbounded perturbation was accepted")


def test_weight_falsifier_excludes_confidence_only_grade_change():
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    for dimension in config["dimensions"].values():
        dimension["score"] = 0.8
        dimension["confidence"] = 0.755

    payload = build_payload(config)

    assert payload["baseline"]["grade"] == "B"
    assert payload["sensitivity"]["weight_observed_grades"] == ["B"]
    assert payload["sensitivity"]["confidence_observed_grades"] == ["B", "C+"]
    assert payload["sensitivity"]["major_grade_reversal"] is False


def test_grade_threshold_uses_serialized_precision_consistently():
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    for dimension in config["dimensions"].values():
        dimension["score"] = 0.8
        dimension["confidence"] = 0.75

    payload = build_payload(config)

    assert payload["baseline"]["confidence_adjusted_score"] == 0.6
    assert payload["baseline"]["grade"] == "B"
    assert payload["sensitivity"]["weight_observed_grades"] == ["B"]
    assert all(
        scenario["result"]["grade"] == "B"
        for scenario in payload["sensitivity"]["scenarios"]
        if scenario["kind"] == "weight"
    )
    assert all(
        scenario["result"]["evidence_ladder_rung"] == "none_synthetic"
        for scenario in payload["sensitivity"]["scenarios"]
    )
