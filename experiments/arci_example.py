"""Evaluate one synthetic ARCI target with bounded sensitivity."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Mapping

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.arci import ArciAssessment, ArciDimension, DEFAULT_WEIGHTS  # noqa: E402


def _assessment(
    data: Mapping,
    *,
    weights: Mapping[str, float] | None = None,
    confidence_overrides: Mapping[str, float] | None = None,
) -> ArciAssessment:
    overrides = dict(confidence_overrides or {})
    dimensions = {
        name: ArciDimension(
            score=float(values["score"]),
            confidence=overrides.get(name, float(values["confidence"])),
            rationale=str(values.get("rationale", "")),
        )
        for name, values in data["dimensions"].items()
    }
    return ArciAssessment(dimensions=dimensions, weights=weights or data.get("weights"))


def _serialized_grade(value: float) -> str:
    """Classify the same rounded value that is written to the artifact."""
    if value >= 0.80:
        return "A"
    if value >= 0.70:
        return "B+"
    if value >= 0.60:
        return "B"
    if value >= 0.50:
        return "C+"
    if value >= 0.40:
        return "C"
    return "research-only"


def _compact(result) -> dict:
    adjusted = round(result.confidence_adjusted_score, 12)
    return {
        "score": round(result.score, 12),
        "confidence": round(result.confidence, 12),
        "confidence_adjusted_score": adjusted,
        "lower_bound": round(result.lower_bound, 12),
        "upper_bound": round(result.upper_bound, 12),
        "grade": _serialized_grade(adjusted),
        "evidence_ladder_rung": "none_synthetic",
        "recommendation": result.recommendation,
    }


def build_payload(data: Mapping) -> dict:
    if data.get("synthetic") is not True:
        raise ValueError("ARCI example accepts only an explicitly synthetic target")

    baseline = _assessment(data).evaluate()
    relative = float(data["sensitivity"]["weight_relative_perturbation"])
    confidence_delta = float(data["sensitivity"]["confidence_absolute_perturbation"])
    if not 0.0 < relative <= 0.25:
        raise ValueError("weight perturbation must be in (0, 0.25]")
    if not 0.0 < confidence_delta <= 0.25:
        raise ValueError("confidence perturbation must be in (0, 0.25]")

    scenarios = []
    for name in DEFAULT_WEIGHTS:
        for direction, factor in (("down", 1.0 - relative), ("up", 1.0 + relative)):
            weights = dict(DEFAULT_WEIGHTS)
            weights[name] *= factor
            scenarios.append(
                {
                    "kind": "weight",
                    "dimension": name,
                    "direction": direction,
                    "result": _compact(_assessment(data, weights=weights).evaluate()),
                }
            )
        base_confidence = float(data["dimensions"][name]["confidence"])
        for direction, delta in (("down", -confidence_delta), ("up", confidence_delta)):
            confidence = min(1.0, max(0.0, base_confidence + delta))
            scenarios.append(
                {
                    "kind": "confidence",
                    "dimension": name,
                    "direction": direction,
                    "result": _compact(
                        _assessment(data, confidence_overrides={name: confidence}).evaluate()
                    ),
                }
            )

    baseline_result = _compact(baseline)
    weight_grades = sorted(
        {
            scenario["result"]["grade"]
            for scenario in scenarios
            if scenario["kind"] == "weight"
        }
    )
    confidence_grades = sorted(
        {
            scenario["result"]["grade"]
            for scenario in scenarios
            if scenario["kind"] == "confidence"
        }
    )
    major_grade_reversal = any(
        grade != baseline_result["grade"] for grade in weight_grades
    )
    missing = [
        name for name, values in data["dimensions"].items() if values["missing_data"]
    ]
    next_dimension = max(
        data["dimensions"],
        key=lambda name: (
            DEFAULT_WEIGHTS[name] * (1.0 - float(data["dimensions"][name]["confidence"])),
            name,
        ),
    )
    adjusted_values = [
        scenario["result"]["confidence_adjusted_score"] for scenario in scenarios
    ]
    return {
        "schema": "sns.arci-synthetic-sensitivity.v1",
        "target": data["target"],
        "synthetic": True,
        "provenance": data["provenance"],
        "evidence": {
            name: {
                "evidence_type": values["evidence_type"],
                "evidence_ladder_rung": values["evidence_ladder_rung"],
                "missing_data": values["missing_data"],
            }
            for name, values in data["dimensions"].items()
        },
        "missing_dimensions": missing,
        "baseline": baseline_result,
        "sensitivity": {
            "weight_relative_perturbation": relative,
            "confidence_absolute_perturbation": confidence_delta,
            "scenario_count": len(scenarios),
            "weight_observed_grades": weight_grades,
            "confidence_observed_grades": confidence_grades,
            "confidence_adjusted_score_range": [
                round(min(adjusted_values), 12),
                round(max(adjusted_values), 12),
            ],
            "major_grade_reversal": major_grade_reversal,
            "falsifier_status": (
                "TRIGGERED_WEIGHT_GRADE_REVERSAL"
                if major_grade_reversal
                else "NOT_TRIGGERED_ON_BOUNDED_WEIGHT_PERTURBATIONS"
            ),
            "scenarios": scenarios,
        },
        "next_measurement": {
            "dimension": next_dimension,
            "priority_basis": "default_weight_times_one_minus_confidence",
            "recommendation": data["dimensions"][next_dimension]["next_measurement"],
        },
        "limitations": [
            "This is one declared synthetic target, not a real asteroid assessment.",
            "No external observations or unsupported dollar valuations are used.",
            "Sensitivity exercises the accepted ARCI v0.1 model and does not qualify its ontology.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs" / "arci_synthetic_target.json",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "outputs" / "qst_arci_0001",
    )
    args = parser.parse_args()
    data = json.loads(args.config.read_text(encoding="utf-8"))
    payload = build_payload(data)
    args.out.mkdir(parents=True, exist_ok=True)
    output = args.out / "synthetic_target_sensitivity.json"
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
