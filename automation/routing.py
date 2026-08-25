"""Deterministic, inspectable routing for the Pre-Game Daily research slot."""

from __future__ import annotations

import re
from typing import Mapping, Sequence

_PRIORITY_RE = re.compile(r"^P([0-9]+)$")
_BLOCKER_SCOPES = {"none", "local", "shared", "global", "protected"}


def _priority_rank(value: object) -> int:
    match = _PRIORITY_RE.fullmatch(str(value))
    if match is None:
        raise ValueError(f"priority must use P<number> form: {value!r}")
    return int(match.group(1))


def _validate_candidate(candidate: Mapping[str, object]) -> None:
    required = {
        "quest_id",
        "priority",
        "active_index",
        "eligible",
        "executable",
        "blocker_scope",
    }
    missing = required - set(candidate)
    if missing:
        raise ValueError(f"routing candidate missing fields: {', '.join(sorted(missing))}")
    if not str(candidate["quest_id"]).strip():
        raise ValueError("quest_id cannot be empty")
    _priority_rank(candidate["priority"])
    if not isinstance(candidate["active_index"], int) or int(candidate["active_index"]) < 1:
        raise ValueError("active_index must be a positive integer")
    if not isinstance(candidate["eligible"], bool) or not isinstance(candidate["executable"], bool):
        raise ValueError("eligible and executable must be booleans")
    scope = str(candidate["blocker_scope"])
    if scope not in _BLOCKER_SCOPES:
        raise ValueError(f"unknown blocker_scope: {scope}")


def route_daily_slot(
    candidates: Sequence[Mapping[str, object]],
    *,
    live_owner_quest_id: str | None = None,
) -> dict[str, object]:
    """Return one deterministic routing decision without mutating queue priority.

    ``eligible`` means the caller has already established that the quest is active,
    inside the current delegation, source-current, owner-compatible, and bounded to
    allowed write/check budgets. ``executable`` means a concrete acceptance slice
    exists now. Blocker scope is orthogonal to the decision level that discovered it.
    """

    rows = [dict(candidate) for candidate in candidates]
    if not rows:
        return {
            "decision": "NO_AUTHORIZATION",
            "selected_quest_id": None,
            "escalated_quest_ids": [],
            "reason": "no active routing candidates",
        }

    for row in rows:
        _validate_candidate(row)

    quest_ids = [str(row["quest_id"]) for row in rows]
    if len(set(quest_ids)) != len(quest_ids):
        raise ValueError("routing quest_ids must be unique")
    active_indexes = [int(row["active_index"]) for row in rows]
    if len(set(active_indexes)) != len(active_indexes):
        raise ValueError("active_index values must be unique")

    by_id = {str(row["quest_id"]): row for row in rows}
    if live_owner_quest_id is not None and live_owner_quest_id not in by_id:
        raise ValueError("live owner must name a routing candidate")

    ordered = sorted(
        rows,
        key=lambda row: (
            _priority_rank(row["priority"]),
            int(row["active_index"]),
            str(row["quest_id"]),
        ),
    )
    escalated: list[str] = []

    def inspect(row: Mapping[str, object], *, owner: bool) -> dict[str, object] | None:
        quest_id = str(row["quest_id"])
        scope = str(row["blocker_scope"])

        if scope == "local":
            escalated.append(quest_id)
            return None
        if scope in {"shared", "global", "protected"}:
            return {
                "decision": "NO_AUTHORIZATION",
                "selected_quest_id": None,
                "escalated_quest_ids": escalated + [quest_id],
                "reason": f"{scope} blocker on {quest_id}",
            }
        if bool(row["eligible"]) and bool(row["executable"]):
            return {
                "decision": "CONTINUE_OWNER" if owner else "AUTHORIZE",
                "selected_quest_id": quest_id,
                "escalated_quest_ids": list(escalated),
                "reason": "valid live owner" if owner else "highest-priority executable eligible route",
            }
        return None

    owner_row: Mapping[str, object] | None = None
    if live_owner_quest_id is not None:
        owner_row = by_id[live_owner_quest_id]
        owner_result = inspect(owner_row, owner=True)
        if owner_result is not None:
            return owner_result

    for row in ordered:
        if owner_row is not None and str(row["quest_id"]) == live_owner_quest_id:
            continue
        result = inspect(row, owner=False)
        if result is not None:
            return result

    return {
        "decision": "NO_AUTHORIZATION",
        "selected_quest_id": None,
        "escalated_quest_ids": list(escalated),
        "reason": "no executable eligible route remains",
    }
