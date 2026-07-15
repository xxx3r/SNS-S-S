from pathlib import Path

from automation.state import ConflictKind, StateSnapshot, classify_conflict, hash_files


def snapshot(source: str, state: str, governance: str, pr: str) -> StateSnapshot:
    return StateSnapshot(
        source_commit=source,
        state_hash="sha256:" + state * 64,
        governance_hash="sha256:" + governance * 64,
        pr_ownership_hash="sha256:" + pr * 64,
    )


def test_daily_recheck_detects_monthly_governance_change() -> None:
    expected = snapshot("a" * 40, "1", "2", "3")
    current = snapshot("b" * 40, "1", "4", "3")
    assert classify_conflict(expected, current) is ConflictKind.GOVERNANCE_CHANGED


def test_second_daily_run_detects_pr_ownership_change() -> None:
    expected = snapshot("a" * 40, "1", "2", "3")
    current = snapshot("a" * 40, "1", "2", "4")
    assert classify_conflict(expected, current) is ConflictKind.PR_OWNERSHIP_CHANGED


def test_source_commit_change_without_owned_state_change_is_rebasable() -> None:
    expected = snapshot("a" * 40, "1", "2", "3")
    current = snapshot("b" * 40, "1", "2", "3")
    assert classify_conflict(expected, current) is ConflictKind.SOURCE_COMMIT_CHANGED


def test_state_hash_is_order_stable(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("alpha", encoding="utf-8")
    (tmp_path / "b.txt").write_text("beta", encoding="utf-8")
    assert hash_files(tmp_path, ["a.txt", "b.txt"]) == hash_files(tmp_path, ["b.txt", "a.txt"])
