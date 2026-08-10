import pytest
from src.research.roundup import Roundup
from src.research.roundup_staging import stage_roundup

def make_roundup(actions, week="2026-08-09"):
    return Roundup(week=week, weighted_belief_shifts=(), suggested_actions=tuple(actions), sns_awareness_update={}, research_paths=(1,), body="fixture")

def make_action(quest_id):
    return {"id": quest_id, "title": "Fixture", "objective": "Validate staging.", "artifact": "outputs/fixture.json", "success_metric": "Staging succeeds."}

def test_staging_keeps_actions_as_proposals():
    staged = stage_roundup(make_roundup([make_action("QST-CALENDAR-0001")]), active_quest_ids={"QST-CALENDAR-0001"}, all_quest_ids={"QST-CALENDAR-0001"})
    assert staged.quest_actions[0].action_type == "refine_existing"
    assert staged.quest_actions[0].authority == "proposal"
    assert staged.research_paths == (1,)

def test_staging_rejects_duplicate_ids():
    with pytest.raises(ValueError, match="duplicate quest ID"):
        stage_roundup(make_roundup([make_action("QST-CALENDAR-0001"), make_action("QST-CALENDAR-0001")]), active_quest_ids={"QST-CALENDAR-0001"}, all_quest_ids={"QST-CALENDAR-0001"})

def test_staging_rejects_empty_week():
    with pytest.raises(ValueError, match="week must be non-empty"):
        stage_roundup(make_roundup([make_action("QST-CALENDAR-0001")], week=""), active_quest_ids={"QST-CALENDAR-0001"}, all_quest_ids={"QST-CALENDAR-0001"})
