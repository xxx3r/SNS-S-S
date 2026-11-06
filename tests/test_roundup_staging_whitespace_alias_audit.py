"""Independent zero-world characterization of proposal staging ID aliasing.

Evidence scope: source semantics only, not quest activation or governance enactment.
The test must run against the actual repository parser and quest-action code.
"""
import pytest

from src.research.roundup import Roundup
from src.research.roundup_staging import stage_roundup


def _action(quest_id: str) -> dict[str, str]:
    return {
        "id": quest_id,
        "title": "Existing calendar quest",
        "objective": "Probe staging identity and duplicate rejection.",
        "artifact": "outputs/qst_calendar_0001/alias_probe.json",
        "success_metric": "Reject semantically duplicate quest IDs.",
    }


def _roundup(*actions: dict[str, str]) -> Roundup:
    return Roundup(
        week="2026-11-06",
        weighted_belief_shifts=(),
        suggested_actions=tuple(actions),
        sns_awareness_update={},
        research_paths=(8,),
        body="Non-generating audit fixture.",
    )


def test_exact_existing_id_is_refinement_and_identical_duplicates_fail_closed():
    existing = {"QST-CALENDAR-0001"}
    exact = stage_roundup(
        _roundup(_action("QST-CALENDAR-0001")),
        active_quest_ids=existing,
        all_quest_ids=existing,
    )
    assert [(a.quest.quest_id, a.action_type) for a in exact.quest_actions] == [
        ("QST-CALENDAR-0001", "refine_existing")
    ]
    with pytest.raises(ValueError, match="duplicate quest ID"):
        stage_roundup(
            _roundup(_action("QST-CALENDAR-0001"), _action("QST-CALENDAR-0001")),
            active_quest_ids=existing,
            all_quest_ids=existing,
        )


def test_whitespace_alias_evades_duplicate_detection_in_current_source():
    """Characterize a negative finding; do not silently turn into a fix.

    The accepted code treats the whitespace-suffixed value as a distinct,
    proposal-only quest ID.  This test records current behavior, it does not
    bless that behavior or assert downstream governance accepts the ID.
    """
    existing = {"QST-CALENDAR-0001"}
    staged = stage_roundup(
        _roundup(
            _action("QST-CALENDAR-0001"),
            _action("QST-CALENDAR-0001 "),
        ),
        active_quest_ids=existing,
        all_quest_ids=existing,
    )
    assert [(a.quest.quest_id, a.action_type) for a in staged.quest_actions] == [
        ("QST-CALENDAR-0001", "refine_existing"),
        ("QST-CALENDAR-0001 ", "propose_new"),
    ]
    assert all(a.authority == "proposal" for a in staged.quest_actions)


def test_postgame_request_preflight_and_repository_semantics(tmp_path):
    """Run the repository's own CLI checks on the hosted exact-source checkout.

    These are structural/semantic checks, not an independent science review.
    """
    import json
    import subprocess
    import sys
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    request = {
        "loop_id": "post-game-research",
        "action": "implement",
        "scope": "research-tooling",
        "acceptance_slice": "QST-CALENDAR-0001 non-generating staging whitespace-alias counterexample",
        "paths": [
            "tests/test_roundup_staging_whitespace_alias_audit.py",
            "docs/research/calendar_staging_alias_audit.md",
            "outputs/qst_calendar_0001/staging_alias_audit.json",
            "automation/runs/2026/11/RUN-20261106T224047953948Z-post-game-research-7fe2b0356d68a8359343.json",
            "automation/pr_lifecycle/150.json",
        ],
        "budgets": {"worlds": 0, "records": 0, "runtime_s": 60, "disk_mb": 2},
        "transaction_count": 1,
        "evidence_refs": [
            "https://github.com/xxx3r/SNS-S-S/pull/149",
            "quests/active/QST-CALENDAR-0001-roundup-parser.md",
        ],
    }
    request_file = tmp_path / "postgame_request.json"
    request_file.write_text(json.dumps(request), encoding="utf-8")
    subprocess.run(
        [sys.executable, "-m", "automation.cli", "validate-standing-request",
         "--request", str(request_file), "--now", "2026-11-06T22:40:47Z"],
        cwd=root, check=True, capture_output=True, text=True,
    )
    subprocess.run(
        [sys.executable, "-m", "automation.cli", "validate-repository"],
        cwd=root, check=True, capture_output=True, text=True,
    )
