#!/usr/bin/env python3
"""Score the LEO perovskite PV risk checklist.

The scorer is intentionally conservative: mission readiness is measured only by
mission-ready gate closure, while the overall readiness score gives partial
credit for tabletop and subscale evidence so early progress is still visible.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CHECKLIST = ROOT / "data" / "pv_leo_perovskite_risks.csv"
VALID_STATUSES = {"open", "in_progress", "closed"}
STATUS_POINTS = {"open": 0.0, "in_progress": 0.5, "closed": 1.0}
GATE_WEIGHTS = {
    "tabletop_status": 0.2,
    "subscale_in_space_status": 0.3,
    "mission_ready_status": 0.5,
}
PRIORITY_POINTS = {"low": 1, "medium": 2, "high": 3}
REQUIRED_FIELDS = {
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
}


def load_risks(path: Path) -> list[dict[str, str]]:
    """Load and validate checklist rows from a CSV file."""

    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        missing = REQUIRED_FIELDS - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path} is missing required fields: {sorted(missing)}")
        rows = [{key: (value or "").strip() for key, value in row.items()} for row in reader]

    if not rows:
        raise ValueError(f"{path} contains no risk rows")

    for row in rows:
        for field in GATE_WEIGHTS:
            status = row[field]
            if status not in VALID_STATUSES:
                raise ValueError(
                    f"{row.get('risk_id', '<unknown>')} has invalid {field}={status!r}; "
                    f"expected one of {sorted(VALID_STATUSES)}"
                )
    return rows


def priority_score(row: dict[str, str]) -> int:
    """Return a sortable risk priority score from severity and likelihood."""

    severity = PRIORITY_POINTS.get(row["severity"].lower(), 0)
    likelihood = PRIORITY_POINTS.get(row["likelihood"].lower(), 0)
    return severity * likelihood


def summarize_readiness(rows: Iterable[dict[str, str]], top_n: int = 5) -> dict:
    """Compute readiness summary metrics from risk rows."""

    risk_rows = list(rows)
    gate_counts: Counter[str] = Counter()
    gate_total = 0
    weighted_score = 0.0
    max_weighted_score = 0.0

    for row in risk_rows:
        risk_weight = priority_score(row) or 1
        for gate_field, gate_weight in GATE_WEIGHTS.items():
            status = row[gate_field]
            gate_counts[status] += 1
            gate_total += 1
            weighted_score += STATUS_POINTS[status] * gate_weight * risk_weight
            max_weighted_score += gate_weight * risk_weight

    mission_closed = sum(1 for row in risk_rows if row["mission_ready_status"] == "closed")
    combined_counts = Counter(row["combined_stressor_coverage"] for row in risk_rows)
    unresolved = [row for row in risk_rows if row["mission_ready_status"] != "closed"]
    unresolved.sort(key=lambda row: (-priority_score(row), row["risk_id"]))

    readiness_score = weighted_score / max_weighted_score if max_weighted_score else 0.0
    return {
        "total_risks": len(risk_rows),
        "total_gates": gate_total,
        "gate_status_counts": {status: gate_counts.get(status, 0) for status in sorted(VALID_STATUSES)},
        "mission_ready_closed": mission_closed,
        "mission_ready_closed_percent": round(100.0 * mission_closed / len(risk_rows), 1),
        "weighted_readiness_score": round(readiness_score, 3),
        "combined_stressor_coverage_counts": dict(sorted(combined_counts.items())),
        "highest_priority_unresolved": [
            {
                "risk_id": row["risk_id"],
                "risk_title": row["risk_title"],
                "severity": row["severity"],
                "likelihood": row["likelihood"],
                "priority_score": priority_score(row),
                "tabletop_status": row["tabletop_status"],
                "subscale_in_space_status": row["subscale_in_space_status"],
                "mission_ready_status": row["mission_ready_status"],
                "proof_artifact": row["proof_artifact"],
            }
            for row in unresolved[:top_n]
        ],
    }


def format_summary(summary: dict) -> str:
    """Render a concise human-readable readiness report."""

    lines = [
        "PV LEO perovskite readiness summary",
        f"- Risks: {summary['total_risks']}",
        f"- Gates: {summary['total_gates']}",
        f"- Gate status counts: {summary['gate_status_counts']}",
        f"- Mission-ready gates closed: {summary['mission_ready_closed']} "
        f"({summary['mission_ready_closed_percent']}%)",
        f"- Weighted readiness score: {summary['weighted_readiness_score']}",
        f"- Combined-stressor coverage: {summary['combined_stressor_coverage_counts']}",
        "- Highest-priority unresolved risks:",
    ]
    for row in summary["highest_priority_unresolved"]:
        lines.append(
            f"  - {row['risk_id']} ({row['severity']}/{row['likelihood']}, "
            f"P={row['priority_score']}): {row['risk_title']}"
        )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checklist", type=Path, default=DEFAULT_CHECKLIST, help="Path to PV risk checklist CSV.")
    parser.add_argument("--json-out", type=Path, help="Optional path for machine-readable summary JSON.")
    parser.add_argument("--top", type=int, default=5, help="Number of unresolved risks to list.")
    args = parser.parse_args()

    rows = load_risks(args.checklist)
    summary = summarize_readiness(rows, top_n=args.top)
    print(format_summary(summary))

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(summary, indent=2) + "\n")


if __name__ == "__main__":
    main()
