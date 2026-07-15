from automation.audit import build_audit_report, information_inheritance_rate


def receipt(run_id: str, created_at: str, consumed: list[str]) -> dict:
    return {
        "run_id": run_id,
        "created_at": created_at,
        "source_commit": "a" * 40,
        "terminal_state": "DONE",
        "artifacts": [{"path": "artifact.json"}],
        "checks": [{"name": "pytest", "status": "passed", "evidence": "passed"}],
        "consumed_ids": consumed,
    }


def test_information_inheritance_requires_explicit_later_consumption() -> None:
    receipts = [
        receipt("run-1", "2026-07-01T00:00:00Z", []),
        receipt("run-2", "2026-07-02T00:00:00Z", ["run-1"]),
        receipt("run-3", "2026-07-03T00:00:00Z", []),
    ]
    metric = information_inheritance_rate(receipts)
    assert metric["eligible_run_count"] == 2
    assert metric["inherited_run_count"] == 1
    assert metric["rate"] == 0.5


def test_frozen_cutoff_excludes_overlapping_in_flight_work() -> None:
    receipts = [
        receipt("run-before", "2026-09-01T13:59:59Z", []),
        receipt("run-after", "2026-09-01T14:00:01Z", []),
    ]
    report = build_audit_report(receipts, cutoff_time="2026-09-01T14:00:00Z", cutoff_commit="f" * 40)
    assert report["included_run_ids"] == ["run-before"]
    assert report["excluded_run_ids"] == ["run-after"]
