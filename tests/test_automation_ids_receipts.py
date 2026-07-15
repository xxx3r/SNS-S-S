from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import pytest

from automation.ids import new_run_id
from automation.receipts import ReceiptStore, generate_long_log, validate_run_receipt


NOW = datetime(2026, 7, 15, 2, 30, 0, 123456, tzinfo=timezone.utc)
SHA = "a" * 40
STATE_HASH = "sha256:" + "b" * 64


def receipt(run_id: str, loop_id: str = "daily-research-operator") -> dict:
    return {
        "schema": "sns.loop-run.v1",
        "run_id": run_id,
        "loop_id": loop_id,
        "contract_version": "1.0.0",
        "trigger": "scheduled",
        "trigger_time": "2026-07-15T02:30:00Z",
        "source_commit": SHA,
        "state_hash": STATE_HASH,
        "quest_context": {"quest_id": "QST-STOR-0002", "acceptance_slice": "geometry sweep"},
        "pr_context": {"pr_number": 22, "lifecycle_state": "draft_active"},
        "consumed_ids": [],
        "artifacts": [{"path": "outputs/example.json", "kind": "data"}],
        "checks": [{"name": "pytest", "status": "passed", "evidence": "12 passed"}],
        "belief_effects": [],
        "terminal_state": "DONE_WITH_LIMITATIONS",
        "next_action": "Review the generated artifact.",
        "created_at": "2026-07-15T02:31:00Z",
    }


def test_same_commit_parallel_loops_receive_unique_addresses(tmp_path: Path) -> None:
    def make(loop: str) -> tuple[str, Path]:
        run_id = new_run_id(loop, now=NOW)
        payload = receipt(run_id, loop)
        path = ReceiptStore(tmp_path).write(payload)
        return run_id, path

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(make, ["daily-research-operator", "weekly-evidence-synthesis"]))

    assert results[0][0] != results[1][0]
    assert results[0][1] != results[1][1]
    assert all(path.exists() for _, path in results)


def test_receipt_store_refuses_overwrite(tmp_path: Path) -> None:
    run_id = new_run_id("daily-research-operator", now=NOW, token_factory=lambda _: "1" * 20)
    store = ReceiptStore(tmp_path)
    store.write(receipt(run_id))
    with pytest.raises(FileExistsError):
        store.write(receipt(run_id))


def test_duplicate_ids_are_detected_across_files(tmp_path: Path) -> None:
    run_id = new_run_id("daily-research-operator", now=NOW, token_factory=lambda _: "2" * 20)
    payload = receipt(run_id)
    first = tmp_path / "2026/07/first.json"
    second = tmp_path / "2026/07/second.json"
    first.parent.mkdir(parents=True)
    first.write_text(json.dumps(payload), encoding="utf-8")
    second.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate run_id"):
        ReceiptStore(tmp_path).load_all()


def test_receipt_requires_source_and_contract_metadata() -> None:
    run_id = new_run_id("daily-research-operator", now=NOW, token_factory=lambda _: "3" * 20)
    payload = receipt(run_id)
    del payload["source_commit"]
    with pytest.raises(ValueError, match="source_commit"):
        validate_run_receipt(payload)


def test_receipt_correction_is_separate_and_traceable(tmp_path: Path) -> None:
    original_id = new_run_id("daily-research-operator", now=NOW, token_factory=lambda _: "4" * 20)
    correction_id = new_run_id("daily-research-operator", now=NOW, token_factory=lambda _: "5" * 20)
    original = receipt(original_id)
    correction = receipt(correction_id)
    correction["correction_of"] = original_id
    store = ReceiptStore(tmp_path)
    store.write(original)
    store.write(correction)
    loaded = store.load_all()
    assert {item["run_id"] for item in loaded} == {original_id, correction_id}


def test_generated_log_is_derived_not_shared_mutable_history() -> None:
    first_id = new_run_id("daily-research-operator", now=NOW, token_factory=lambda _: "6" * 20)
    second_id = new_run_id("weekly-evidence-synthesis", now=NOW, token_factory=lambda _: "7" * 20)
    text = generate_long_log([receipt(second_id, "weekly-evidence-synthesis"), receipt(first_id)])
    assert "Do not edit by hand" in text
    assert first_id in text and second_id in text
