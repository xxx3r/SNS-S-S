from src.research.quest_engine import quest_actions_from_roundup
from src.research.roundup import Roundup


def roundup(action: dict) -> Roundup:
    return Roundup(
        week="2026-07-12",
        weighted_belief_shifts=(),
        suggested_actions=(action,),
        sns_awareness_update={},
        research_paths=(),
        body="",
    )


def action(quest_id: str) -> dict:
    return {
        "id": quest_id,
        "title": "Thermal derating",
        "objective": "Extend the active sweep.",
        "artifact": "outputs/thermal.json",
        "success_metric": "One reproducible sweep.",
    }


def test_existing_active_quest_becomes_refinement_not_creation() -> None:
    result = quest_actions_from_roundup(
        roundup(action("QST-STOR-0002")),
        active_quest_ids={"QST-STOR-0002"},
        all_quest_ids={"QST-STOR-0002"},
    )
    assert result[0].action_type == "refine_existing"


def test_unused_id_becomes_new_proposal() -> None:
    result = quest_actions_from_roundup(
        roundup(action("QST-STOR-0099")),
        active_quest_ids=set(),
        all_quest_ids=set(),
    )
    assert result[0].action_type == "propose_new"
