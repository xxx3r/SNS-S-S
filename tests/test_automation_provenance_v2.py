from __future__ import annotations

from pathlib import Path

import pytest

from automation.provenance import (
    BASE_SNAPSHOT_ROLES,
    build_run_receipt_v2,
    build_state_snapshot,
    implementation_receipts_for_authorization,
    snapshot_from_connector_records,
)
from automation.receipts import validate_run_receipt


SOURCE = "a" * 40
AUTH = "AUTH-20260829T133000000000Z-meta-provenance-" + "b" * 20
ORIGINAL = "RUN-20260829T133000000000Z-daily-research-operator-" + "c" * 20
CORRECTION = "RUN-20260829T133100000000Z-daily-research-operator-" + "d" * 20


def _records(tmp_path: Path) -> dict[str, str]:
    records = {
        "stable_law": "AGENTS.md",
        "active_contract": "automation/contracts/daily-research-operator.v1.1.md",
        "state_ownership": "automation/state_ownership.json",
        "active_quest_index": "quests/active/README.md",
        "research_graph": "quests/research_graph.json",
        "runtime_manifest": "automation/runtime_manifest.json",
        "canonical_memory": "memory/mem_log_short.md",
    }
    assert set(records) == BASE_SNAPSHOT_ROLES
    for path in records.values():
        target = tmp_path / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(f"content:{path}\n", encoding="utf-8")
    return records


def _draft(run_id: str) -> dict[str, object]:
    return {
        "run_id": run_id,
        "loop_id": "daily-research-operator",
        "contract_version": "1.1.0",
        "trigger": "explicit-human",
        "trigger_time": "2026-08-29T13:30:00Z",
        "source_commit": SOURCE,
        "quest_context": {"quest_id": "QST-META-0001"},
        "pr_context": {"pr_number": 55},
        "consumed_ids": [AUTH],
        "artifacts": [],
        "checks": [],
        "belief_effects": [],
        "terminal_state": "DONE_WITH_LIMITATIONS",
        "next_action": "Validate provenance.",
        "created_at": "2026-08-29T13:31:00Z",
    }


def test_state_snapshot_is_inspectable_and_deterministic(tmp_path: Path) -> None:
    records = _records(tmp_path)
    first = build_state_snapshot(
        tmp_path,
        source_commit=SOURCE,
        records=records,
        open_prs=[{"number": 55, "head_sha": "e" * 40, "draft": True, "state": "open"}],
    )
    second = build_state_snapshot(
        tmp_path,
        source_commit=SOURCE,
        records=dict(reversed(list(records.items()))),
        open_prs=[{"number": 55, "head_sha": "e" * 40, "draft": True, "state": "open"}],
    )
    assert first == second
    assert first["schema"] == "sns.state-snapshot.v1"
    assert first["fingerprint"] != "sha256:" + "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"[0:64]


def test_connector_snapshot_requires_canonical_roles() -> None:
    records = [{"role": role, "path": f"{role}.txt", "git_blob_sha": "f" * 40} for role in sorted(BASE_SNAPSHOT_ROLES)]
    snapshot = snapshot_from_connector_records(source_commit=SOURCE, records=records)
    assert snapshot["source_commit"] == SOURCE
    with pytest.raises(ValueError, match="missing canonical roles"):
        snapshot_from_connector_records(source_commit=SOURCE, records=records[:-1])


def test_v2_receipt_replaces_opaque_state_hash_with_snapshot(tmp_path: Path) -> None:
    snapshot = build_state_snapshot(tmp_path, source_commit=SOURCE, records=_records(tmp_path))
    receipt = build_run_receipt_v2(_draft(ORIGINAL), state_snapshot=snapshot)
    validate_run_receipt(receipt)
    assert receipt["schema"] == "sns.loop-run.v2"
    assert receipt["receipt_kind"] == "run"
    assert "state_hash" not in receipt


def test_append_only_correction_does_not_consume_second_implementation_receipt(tmp_path: Path) -> None:
    snapshot = build_state_snapshot(tmp_path, source_commit=SOURCE, records=_records(tmp_path))
    original = build_run_receipt_v2(_draft(ORIGINAL), state_snapshot=snapshot)
    correction = build_run_receipt_v2(
        _draft(CORRECTION),
        state_snapshot=snapshot,
        receipt_kind="correction",
        correction_of=ORIGINAL,
    )
    validate_run_receipt(correction)
    consuming = implementation_receipts_for_authorization([original, correction], AUTH)
    assert [item["run_id"] for item in consuming] == [ORIGINAL]


def test_v2_correction_requires_target(tmp_path: Path) -> None:
    snapshot = build_state_snapshot(tmp_path, source_commit=SOURCE, records=_records(tmp_path))
    correction = build_run_receipt_v2(_draft(CORRECTION), state_snapshot=snapshot, receipt_kind="correction")
    with pytest.raises(ValueError, match="requires correction_of"):
        validate_run_receipt(correction)
