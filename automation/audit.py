"""Frozen-cutoff metrics for the SNS autonomous-system audit."""

from __future__ import annotations

from collections import Counter
from datetime import datetime
from typing import Iterable, Mapping

from .organization import (
    communication_observability,
    cutoff_ancestry_set,
    information_inheritance_rate,
)


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
    cutoff_ancestors: Iterable[str] | None = None,
) -> tuple[list[Mapping[str, object]], list[Mapping[str, object]]]:
    """Split completed receipts using both time and commit ancestry."""

    cutoff = _timestamp(cutoff_time)
    ancestor_set = cutoff_ancestry_set(cutoff_commit, cutoff_ancestors)
    included: list[Mapping[str, object]] = []
    excluded: list[Mapping[str, object]] = []
    for receipt in receipts:
        completed = _timestamp(str(receipt["created_at"]))
        source_commit = str(receipt["source_commit"])
        if completed < cutoff and source_commit in ancestor_set:
            included.append(receipt)
        else:
            excluded.append(receipt)
    return included, excluded


def build_audit_report(
    receipts: Iterable[Mapping[str, object]],
    *,
    cutoff_time: str,
    cutoff_commit: str,
    cutoff_ancestors: Iterable[str] | None = None,
    quest_actions: Iterable[Mapping[str, object]] = (),
    evidence_clusters: Mapping[str, Mapping[str, object]] | None = None,
    pr_lifecycle: Iterable[Mapping[str, object]] = (),
) -> dict[str, object]:
    receipt_list = list(receipts)
    ancestor_set = cutoff_ancestry_set(cutoff_commit, cutoff_ancestors)
    included, excluded = eligible_receipts(
        receipt_list,
        cutoff_time=cutoff_time,
        cutoff_commit=cutoff_commit,
        cutoff_ancestors=ancestor_set,
    )
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
    communication = communication_observability(included)

    excluded_reasons = Counter()
    cutoff = _timestamp(cutoff_time)
    for receipt in excluded:
        completed = _timestamp(str(receipt["created_at"]))
        if completed >= cutoff:
            excluded_reasons["post_cutoff_time"] += 1
        elif str(receipt["source_commit"]) not in ancestor_set:
            excluded_reasons["outside_cutoff_ancestry"] += 1
        else:
            excluded_reasons["excluded_unknown"] += 1

    return {
        "schema": "sns.system-audit.v1",
        "cutoff_time": cutoff_time,
        "cutoff_commit": cutoff_commit,
        "cutoff_ancestry_size": len(ancestor_set),
        "triggered_run_count": len(receipt_list),
        "included_completed_run_count": len(included),
        "excluded_or_in_flight_run_count": len(excluded),
        "excluded_reason_counts": dict(sorted(excluded_reasons.items())),
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
        "communication_observability": communication,
        "included_run_ids": [str(receipt["run_id"]) for receipt in included],
        "excluded_run_ids": [str(receipt["run_id"]) for receipt in excluded],
    }


def render_audit_markdown(report: Mapping[str, object]) -> str:
    inheritance = dict(report["information_inheritance"])
    typed = dict(inheritance["contract_complete"])
    communication = dict(report["communication_observability"])
    return f"""# SNS Autonomous-System Audit

- Frozen cutoff: {report['cutoff_time']}
- Cutoff commit: {report['cutoff_commit']}
- Cutoff ancestry evidence: **{report['cutoff_ancestry_size']}** commits
- Included completed runs: **{report['included_completed_run_count']}**
- Excluded or in-flight runs: **{report['excluded_or_in_flight_run_count']}**
- Concrete-artifact rate: **{float(report['concrete_artifact_rate']):.1%}**
- Prose-only rate: **{float(report['prose_only_rate']):.1%}**
- Verification pass rate: **{float(report['verification_pass_rate']):.1%}**
- Contract-complete inheritance: **{float(typed['rate']):.1%}** ({typed['inherited_receipt_count']}/{typed['eligible_receipt_count']})
- Machine-visible lineage gaps: **{typed['lineage_gap_count']}**
- Proposal-to-authorization latency samples: **{communication['proposal_to_authorization_latency_seconds']['count']}**
- Authorization-to-first-artifact latency samples: **{communication['authorization_to_first_artifact_latency_seconds']['count']}**
- Administrative transactions per scientific artifact: **{communication['administrative_transactions_per_scientific_artifact']}**

## Terminal states

~~~json
{report['terminal_state_counts']}
~~~

## Quest actions

~~~json
{report['quest_action_counts']}
~~~

## PR lifecycle

~~~json
{report['pr_lifecycle_counts']}
~~~

This report is generated from immutable records. In-flight work is visible but excluded from completed-period rates.
"""
