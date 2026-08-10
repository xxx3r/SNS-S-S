"""Stage parsed weekly roundup data without enacting governance."""
from dataclasses import dataclass
from typing import Iterable
from src.research.quest_engine import QuestActionSpec, quest_actions_from_roundup
from src.research.roundup import Roundup

@dataclass(frozen=True)
class StagedRoundup:
    week: str
    quest_actions: tuple[QuestActionSpec, ...]
    belief_shift_count: int
    research_paths: tuple[int, ...]

def stage_roundup(roundup: Roundup, *, active_quest_ids: Iterable[str], all_quest_ids: Iterable[str]) -> StagedRoundup:
    """Validate deterministic structure and return proposal-only staged data."""
    if not roundup.week.strip():
        raise ValueError("roundup week must be non-empty")
    actions = tuple(quest_actions_from_roundup(roundup, active_quest_ids=active_quest_ids, all_quest_ids=all_quest_ids))
    return StagedRoundup(roundup.week, actions, len(roundup.weighted_belief_shifts), tuple(roundup.research_paths))
