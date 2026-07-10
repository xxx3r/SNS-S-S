"""Tests for the PV perovskite readiness checklist and scorer."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from scripts.score_pv_readiness import load_risks, summarize_readiness  # noqa: E402


def test_default_pv_checklist_has_required_gate_rows():
    rows = load_risks(ROOT / "data" / "pv_leo_perovskite_risks.csv")

    assert len(rows) == 10
    assert {"PV-01", "PV-02", "PV-06", "PV-10"}.issubset({row["risk_id"] for row in rows})
    assert all(row["proof_artifact"] for row in rows)
    assert all(row["mission_ready_status"] in {"open", "in_progress", "closed"} for row in rows)


def test_pv_readiness_summary_prioritizes_unresolved_high_risks():
    rows = load_risks(ROOT / "data" / "pv_leo_perovskite_risks.csv")
    summary = summarize_readiness(rows, top_n=3)

    assert summary["total_risks"] == 10
    assert summary["total_gates"] == 30
    assert summary["gate_status_counts"]["open"] == 29
    assert summary["gate_status_counts"]["in_progress"] == 1
    assert summary["mission_ready_closed_percent"] == 0.0
    assert summary["highest_priority_unresolved"][0]["risk_id"] in {"PV-02", "PV-06", "PV-10"}


def test_pv_readiness_scorer_accepts_closed_fixture(tmp_path):
    checklist = tmp_path / "risks.csv"
    fieldnames = [
        "risk_id",
        "risk_title",
        "severity",
        "likelihood",
        "tabletop_status",
        "subscale_in_space_status",
        "mission_ready_status",
        "proof_artifact",
        "evidence_link",
        "combined_stressor_coverage",
    ]
    with checklist.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(
            {
                "risk_id": "PV-X",
                "risk_title": "Fixture risk",
                "severity": "High",
                "likelihood": "High",
                "tabletop_status": "closed",
                "subscale_in_space_status": "closed",
                "mission_ready_status": "closed",
                "proof_artifact": "fixture proof",
                "evidence_link": "https://example.invalid",
                "combined_stressor_coverage": "full",
            }
        )

    summary = summarize_readiness(load_risks(checklist))

    assert summary["gate_status_counts"]["closed"] == 3
    assert summary["mission_ready_closed_percent"] == 100.0
    assert summary["weighted_readiness_score"] == 1.0
