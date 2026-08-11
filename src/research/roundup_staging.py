"""Stage and serialize parsed weekly roundup data without enacting governance."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from src.research.quest_engine import QuestActionSpec, quest_actions_from_roundup
from src.research.roundup import Roundup


@dataclass(frozen=True)
class StagedRoundup:
    week: str
    quest_actions: tuple[QuestActionSpec, ...]
    belief_shift_count: int
    research_paths: tuple[int, ...]


def stage_roundup(
    roundup: Roundup,
    *,
    active_quest_ids: Iterable[str],
    all_quest_ids: Iterable[str],
) -> StagedRoundup:
    """Validate deterministic structure and return proposal-only staged data."""
    if not roundup.week.strip():
        raise ValueError("roundup week must be non-empty")
    actions = tuple(
        quest_actions_from_roundup(
            roundup,
            active_quest_ids=active_quest_ids,
            all_quest_ids=all_quest_ids,
        )
    )
    return StagedRoundup(
        roundup.week,
        actions,
        len(roundup.weighted_belief_shifts),
        tuple(roundup.research_paths),
    )


def staged_roundup_payload(staged: StagedRoundup) -> dict[str, object]:
    """Return a stable proposal-only representation of staged roundup semantics.

    Immutable quest-action IDs are intentionally excluded: they contain time/random
    material and belong to later receipt/event publication, not deterministic staging.
    """
    return {
        "schema": "sns.roundup-staging.v1",
        "week": staged.week,
        "quest_actions": [
            {
                "action_type": action.action_type,
                "authority": action.authority,
                "quest": {
                    "quest_id": action.quest.quest_id,
                    "title": action.quest.title,
                    "objective": action.quest.objective,
                    "artifact": action.quest.artifact,
                    "success_metric": action.quest.success_metric,
                    "source_week": action.quest.source_week,
                },
                "target_quest_ids": list(action.target_quest_ids),
            }
            for action in staged.quest_actions
        ],
        "belief_shift_count": staged.belief_shift_count,
        "research_paths": list(staged.research_paths),
    }


def serialize_staged_roundup(staged: StagedRoundup) -> str:
    """Serialize a staged roundup deterministically as canonical readable JSON."""
    return json.dumps(staged_roundup_payload(staged), indent=2, sort_keys=True) + "\n"


def write_staged_roundup(staged: StagedRoundup, output_path: str | Path) -> Path:
    """Write deterministic staged JSON without enacting any governance effects."""
    path = Path(output_path)
    if path.suffix != ".json":
        raise ValueError("staged roundup output path must end in .json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(serialize_staged_roundup(staged), encoding="utf-8")
    return path
