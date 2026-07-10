"""Convert roundup actions into Codex-readable quest drafts."""

from __future__ import annotations

from dataclasses import dataclass

from src.research.roundup import Roundup


@dataclass(frozen=True)
class QuestSpec:
    quest_id: str
    title: str
    objective: str
    artifact: str
    success_metric: str
    source_week: str


def quests_from_roundup(roundup: Roundup) -> list[QuestSpec]:
    """Normalize ``suggested_actions`` into typed quest specifications."""
    quests = []
    for action in roundup.suggested_actions:
        required = {"id", "title", "objective", "artifact", "success_metric"}
        missing = required - set(action)
        if missing:
            raise ValueError(f"suggested action missing: {', '.join(sorted(missing))}")
        quests.append(
            QuestSpec(
                quest_id=str(action["id"]),
                title=str(action["title"]),
                objective=str(action["objective"]),
                artifact=str(action["artifact"]),
                success_metric=str(action["success_metric"]),
                source_week=roundup.week,
            )
        )
    return quests


def render_quest_markdown(quest: QuestSpec) -> str:
    """Render a quest file suitable for staging and human review."""
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
