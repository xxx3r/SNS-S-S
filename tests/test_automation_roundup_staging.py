import json

import pytest

from src.research.roundup import Roundup
from src.research.roundup_staging import (
    serialize_staged_roundup,
    stage_roundup,
    write_staged_roundup,
)


def make_roundup(actions, week="2026-08-09"):
    return Roundup(
        week=week,
        weighted_belief_shifts=(),
        suggested_actions=tuple(actions),
        sns_awareness_update={},
        research_paths=(1,),
        body="fixture",
    )


def make_action(quest_id):
    return {
        "id": quest_id,
        "title": "Fixture",
        "objective": "Validate staging.",
        "artifact": "outputs/fixture.json",
        "success_metric": "Staging succeeds.",
    }


def staged_fixture():
    return stage_roundup(
        make_roundup([make_action("QST-CALENDAR-0001")]),
        active_quest_ids={"QST-CALENDAR-0001"},
        all_quest_ids={"QST-CALENDAR-0001"},
    )


def test_staging_keeps_actions_as_proposals():
    staged = staged_fixture()
    assert staged.quest_actions[0].action_type == "refine_existing"
    assert staged.quest_actions[0].authority == "proposal"
    assert staged.research_paths == (1,)


def test_staging_rejects_duplicate_ids():
    with pytest.raises(ValueError, match="duplicate quest ID"):
        stage_roundup(
            make_roundup(
                [
                    make_action("QST-CALENDAR-0001"),
                    make_action("QST-CALENDAR-0001"),
                ]
            ),
            active_quest_ids={"QST-CALENDAR-0001"},
            all_quest_ids={"QST-CALENDAR-0001"},
        )


def test_staging_rejects_empty_week():
    with pytest.raises(ValueError, match="week must be non-empty"):
        stage_roundup(
            make_roundup([make_action("QST-CALENDAR-0001")], week=""),
            active_quest_ids={"QST-CALENDAR-0001"},
            all_quest_ids={"QST-CALENDAR-0001"},
        )


def test_staged_serialization_is_deterministic_and_excludes_event_ids():
    first = serialize_staged_roundup(staged_fixture())
    second = serialize_staged_roundup(staged_fixture())

    assert first == second
    payload = json.loads(first)
    assert payload["schema"] == "sns.roundup-staging.v1"
    assert payload["quest_actions"][0]["authority"] == "proposal"
    assert payload["quest_actions"][0]["action_type"] == "refine_existing"
    assert "quest_action_id" not in payload["quest_actions"][0]


def test_staged_writer_emits_stable_json_without_governance_side_effects(tmp_path):
    staged = staged_fixture()
    output = tmp_path / "outputs" / "staged-roundup.json"

    written = write_staged_roundup(staged, output)

    assert written == output
    assert written.read_text(encoding="utf-8") == serialize_staged_roundup(staged)
    assert json.loads(written.read_text(encoding="utf-8"))["belief_shift_count"] == 0


def test_staged_writer_requires_json_output_path(tmp_path):
    with pytest.raises(ValueError, match="must end in .json"):
        write_staged_roundup(staged_fixture(), tmp_path / "staged-roundup.txt")
