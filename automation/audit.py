"""Frozen-cutoff metrics for the SNS autonomous-system audit."""

from __future__ import annotations

from collections import Counter
from datetime import datetime
from typing import Iterable, Mapping


def _timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("audit timestamps must include a timezone")
    return parsed


def eligible_receipts(
    receipts: Iterable[Mapping[str, object]],
    *,
    cutoff_time: str,
    cutoff_commit: str,
) -> tuple[list[Mapping[str, object]], list[Mapping[str, object]]]:
    """Split completed receipts from in-flight or post-cutoff work."""

    cutoff = _timestamp(cutoff_time)
    included: list[Mapping[str, object]] = []
    excluded: list[Mapping[str, object]] = []
    for receipt in receipts:
        completed = _timestamp(str(receipt["created_at"]))
        if completed < cutoff:
            included.append(receipt)
        else:
            excluded.append(receipt)
    return included, excluded


def information_inheritance_rate(receipts: Iterable[Mapping[str, object]]) -> dict[str, object]:
    ordered = sorted(receipts, key=lambda item: str(item["created_at"]))
    eligible_ids = {str(item["run_id"]) for item in ordered[:-1]}
    consumed: set[str] = set()
    for receipt in ordered:
        consumed.update(str(value) for value in receipt.get("consumed_ids", []) if str(value) in eligible_ids)
    denominator = len(eligible_ids)
    return {
        "inherited_run_count": len(consumed),
        "eligible_run_count": denominator,
        "rate": len(consumed) / denominator if denominator else 0.0,
        "inherited_run_ids": sorted(consumed),
    }


def build_audit_report(
    receipts: Iterable[Mapping[str, object]],
    *,
    cutoff_time: str,
    cutoff_commit: str,
    quest_actions: Iterable[Mapping[str, object]] = (),
    evidence_clusters: Mapping[str, Mapping[str, object]] | None = None,
    pr_lifecycle: Iterable[Mapping[str, object]] = (),
) -> dict[str, object]:
    receipt_list = list(receipts)
    included, excluded = eligible_receipts(receipt_list, cutoff_time=cutoff_time, cutoff_commit=cutoff_commit)
    terminal_counts = Counter(str(receipt["terminal_state"]) for receipt in included)
    concrete = sum(bool(receipt.get("artifacts")) for receipt in included)
    checks = [check for receipt in included for check in receipt.get("checks", [])]
    executed_checks = [check for check in checks if check.get("status") != "not_run"]
    passed_checks = sum(check.get("status") == "passed" for check in executed_checks)
    actions = list(quest_actions)
    action_counts = Counter(str(action.get("action_type")) for action in actions)
    lifecycle = list(pr_lifecycle)
    lifecycle_counts = Counter(str(record.get("state")) for record in lifecycle)
    inheritance = information_inheritance_rate(included)

    return {
        "schema": "sns.system-audit.v1",
        "cutoff_time": cutoff_time,
        "cutoff_commit": cutoff_commit,
        "triggered_run_count": len(receipt_list),
        "included_completed_run_count": len(included),
        "excluded_or_in_flight_run_count": len(excluded),
        "terminal_state_counts": dict(sorted(terminal_counts.items())),
        "concrete_artifact_rate": concrete / len(included) if included else 0.0,
        "prose_only_rate": (len(included) - concrete) / len(included) if included else 0.0,
        "verification_pass_rate": passed_checks / len(executed_checks) if executed_checks else 0.0,
        "quest_action_counts": dict(sorted(action_counts.items())),
        "duplicate_evidence_cluster_count": sum(
            int(cluster.get("source_count", 0)) > int(cluster.get("independent_source_count", 0))
            for cluster in (evidence_clusters or {}).values()
        ),
        "pr_lifecycle_counts": dict(sorted(lifecycle_counts.items())),
        "stale_or_superseded_pr_count": sum(
            state in {"superseded", "closed_abandoned"} for state in lifecycle_counts.elements()
        ),
        "information_inheritance": inheritance,
        "included_run_ids": [str(receipt["run_id"]) for receipt in included],
        "excluded_run_ids": [str(receipt["run_id"]) for receipt in excluded],
    }


def render_audit_markdown(report: Mapping[str, object]) -> str:
    inheritance = dict(report["information_inheritance"])
    return f"""# SNS Autonomous-System Audit

- Frozen cutoff: `{report['cutoff_time']}`
- Cutoff commit: `{report['cutoff_commit']}`
- Included completed runs: **{report['included_completed_run_count']}**
- Excluded or in-flight runs: **{report['excluded_or_in_flight_run_count']}**
- Concrete-artifact rate: **{float(report['concrete_artifact_rate']):.1%}**
- Prose-only rate: **{float(report['prose_only_rate']):.1%}**
- Verification pass rate: **{float(report['verification_pass_rate']):.1%}**
- Information inheritance: **{float(inheritance['rate']):.1%}** ({inheritance['inherited_run_count']}/{inheritance['eligible_run_count']})

## Terminal states

```json
{report['terminal_state_counts']}
```

## Quest actions

```json
{report['quest_action_counts']}
```

## PR lifecycle

```json
{report['pr_lifecycle_counts']}
```

This report is generated from immutable records. In-flight work is visible but excluded from completed-period rates.
"""
