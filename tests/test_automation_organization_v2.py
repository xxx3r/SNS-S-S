from __future__ import annotations

import pytest

from automation.audit import eligible_receipts, information_inheritance_rate
from automation.organization import communication_observability, validate_receipt_observability


RUN_1 = "RUN-20260902T090000000000Z-weekly-evidence-synthesis-" + "a" * 20
RUN_2 = "RUN-20260902T100000000000Z-monthly-governance-" + "b" * 20


def base_receipt(run_id: str, created_at: str, source_commit: str) -> dict[str, object]:
    return {
        "run_id": run_id,
        "created_at": created_at,
        "source_commit": source_commit,
        "terminal_state": "DONE",
        "artifacts": [],
        "checks": [],
        "consumed_ids": [],
    }


def test_cutoff_commit_requires_real_ancestry_and_excludes_unrelated_source() -> None:
    before = base_receipt("before", "2026-09-01T13:00:00Z", "a" * 40)
    unrelated = base_receipt("unrelated", "2026-09-01T13:30:00Z", "c" * 40)
    included, excluded = eligible_receipts(
        [before, unrelated],
        cutoff_time="2026-09-01T14:00:00Z",
        cutoff_commit="f" * 40,
        cutoff_ancestors={"a" * 40, "f" * 40},
    )
    assert [item["run_id"] for item in included] == ["before"]
    assert [item["run_id"] for item in excluded] == ["unrelated"]

    with pytest.raises(ValueError, match="ancestry evidence"):
        eligible_receipts(
            [before],
            cutoff_time="2026-09-01T14:00:00Z",
            cutoff_commit="f" * 40,
        )


def test_contract_complete_inheritance_preserves_run_only_diagnostic() -> None:
    first = base_receipt(RUN_1, "2026-09-02T09:00:00Z", "a" * 40)
    second = base_receipt(RUN_2, "2026-09-02T10:00:00Z", "a" * 40)
    second["inheritance"] = [{"kind": "RUN", "ref": RUN_1}]
    second["decision_effect"] = "The Monthly transition used the accepted audit evidence."
    third = base_receipt(
        "RUN-20260902T110000000000Z-daily-research-operator-" + "c" * 20,
        "2026-09-02T11:00:00Z",
        "a" * 40,
    )
    metric = information_inheritance_rate([first, second, third])
    assert metric["eligible_run_count"] == 2
    assert metric["inherited_run_count"] == 0
    assert metric["contract_complete"]["inherited_receipt_count"] == 1
    assert metric["contract_complete"]["reference_counts"] == {"RUN": 1}
    assert metric["contract_complete"]["lineage_gap_count"] == 1


def test_communication_observability_generates_latency_and_admin_cost() -> None:
    first = base_receipt(RUN_1, "2026-09-02T09:00:00Z", "a" * 40)
    first["observability"] = {
        "proposal_at": "2026-09-02T09:00:00Z",
        "authorization_at": "2026-09-02T10:00:00Z",
        "first_artifact_at": "2026-09-02T10:30:00Z",
        "administrative_transactions": 2,
        "scientific_artifacts": 1,
    }
    second = base_receipt(RUN_2, "2026-09-02T10:00:00Z", "a" * 40)
    second["observability"] = {
        "administrative_transactions": 1,
        "scientific_artifacts": 0,
    }
    metrics = communication_observability([first, second])
    assert metrics["proposal_to_authorization_latency_seconds"]["mean_seconds"] == 3600.0
    assert metrics["authorization_to_first_artifact_latency_seconds"]["mean_seconds"] == 1800.0
    assert metrics["administrative_transactions_per_scientific_artifact"] == 3.0


def test_invalid_observability_fails_closed() -> None:
    record = base_receipt(RUN_1, "2026-09-02T09:00:00Z", "a" * 40)
    record["inheritance"] = [{"kind": "RUN", "ref": "not-a-run-id"}]
    with pytest.raises(ValueError, match="invalid immutable identifier"):
        validate_receipt_observability(record)
