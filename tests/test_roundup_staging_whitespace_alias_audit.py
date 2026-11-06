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

