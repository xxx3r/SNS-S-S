"""Convert roundup actions into typed, governance-aware quest proposals."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable

from automation.ids import new_event_id
from automation.models import QuestActionType
from src.research.roundup import Roundup


@dataclass(frozen=True)
class QuestSpec:
    quest_id: str
    title: str
    objective: str
    artifact: str
    success_metric: str
    source_week: str


@dataclass(frozen=True)
class QuestActionSpec:
    quest_action_id: str
    action_type: str
    quest: QuestSpec
    target_quest_ids: tuple[str, ...]
    authority: str = "proposal"

    def as_event(self) -> dict[str, object]:
        return {
            "schema": "sns.quest-action.v1",
            "quest_action_id": self.quest_action_id,
            "action_type": self.action_type,
            "quest_id": self.quest.quest_id,
            "target_quest_ids": list(self.target_quest_ids),
            "proposed_by_loop": "weekly-evidence-synthesis",
            "authority": self.authority,
            "rationale": self.quest.objective,
            "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }


def _quest_from_action(action: dict, source_week: str) -> QuestSpec:
    required = {"id", "title", "objective", "artifact", "success_metric"}
    missing = required - set(action)
    if missing:
        raise ValueError(f"suggested action missing: {', '.join(sorted(missing))}")
    return QuestSpec(
        quest_id=str(action["id"]),
        title=str(action["title"]),
        objective=str(action["objective"]),
        artifact=str(action["artifact"]),
        success_metric=str(action["success_metric"]),
        source_week=source_week,
    )


def quests_from_roundup(roundup: Roundup) -> list[QuestSpec]:
    """Compatibility view of roundup suggestions.

    New automation should call :func:`quest_actions_from_roundup` so an existing
    quest is represented as a refinement rather than staged as a duplicate file.
    """

    return [_quest_from_action(action, roundup.week) for action in roundup.suggested_actions]


def quest_actions_from_roundup(
    roundup: Roundup,
    *,
    active_quest_ids: Iterable[str],
    all_quest_ids: Iterable[str],
) -> list[QuestActionSpec]:
    """Translate suggestions into explicit create/refine/block/merge semantics."""

    active = set(active_quest_ids)
    existing = set(all_quest_ids)
    actions: list[QuestActionSpec] = []
    seen_ids: set[str] = set()
    for raw in roundup.suggested_actions:
        action = dict(raw)
        quest = _quest_from_action(action, roundup.week)
        if quest.quest_id in seen_ids:
            raise ValueError(f"roundup contains duplicate quest ID: {quest.quest_id}")
        seen_ids.add(quest.quest_id)

        declared = action.get("action_type")
        if declared is None:
            action_type = QuestActionType.REFINE_EXISTING.value if quest.quest_id in active else QuestActionType.PROPOSE_NEW.value
        else:
            action_type = str(declared)
        if action_type not in {value.value for value in QuestActionType}:
            raise ValueError(f"unsupported quest action type: {action_type}")
        if action_type == QuestActionType.PROPOSE_NEW.value and quest.quest_id in existing:
            raise ValueError(f"new quest reuses existing ID: {quest.quest_id}")
        if action_type == QuestActionType.REFINE_EXISTING.value and quest.quest_id not in active:
            raise ValueError(f"refinement targets non-active quest: {quest.quest_id}")

        actions.append(
            QuestActionSpec(
                quest_action_id=new_event_id("QA", f"{roundup.week}-{quest.quest_id}-{action_type}"),
                action_type=action_type,
                quest=quest,
                target_quest_ids=tuple(str(value) for value in action.get("target_quest_ids", [])),
            )
        )
    return actions


def render_quest_markdown(quest: QuestSpec) -> str:
    return f"""# {quest.quest_id}: {quest.title}

Status: Proposed
Source Week: {quest.source_week}

## Objective
{quest.objective}

## Success Metric
{quest.success_metric}

## Required Artifact
- `{quest.artifact}`

## Definition of Done
- Artifact exists and is reproducible.
- Assumptions and uncertainty are explicit.
- Tests or validation checks pass where applicable.
- The quest record points to the evidence produced.
"""


def render_refinement_markdown(action: QuestActionSpec) -> str:
    return f"""# Proposed refinement: {action.quest.quest_id}

Action: `{action.action_type}`  
Source week: {action.quest.source_week}

## Proposed objective
{action.quest.objective}

## Proposed artifact
`{action.quest.artifact}`

## Success metric
{action.quest.success_metric}

This is a governance proposal for the existing active quest. It is not a new quest file and does not change queue membership.
"""
