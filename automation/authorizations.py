"""Immutable fast-governance authorization records."""

from __future__ import annotations

import re
from typing import Mapping

from .governance import validate_triage_authorization

_AUTH_RE = re.compile(r"^AUTH-[0-9]{8}T[0-9]{12}Z-[a-z0-9-]+-[0-9a-f]{20}$")
_QUEST_RE = re.compile(r"^QST-[A-Z0-9]+-[0-9]{4}$")


def validate_governance_authorization(
    record: Mapping[str, object],
    *,
    delegations: Mapping[str, Mapping[str, object]],
    active_ids: set[str],
) -> None:
    required = {
        "schema",
        "authorization_id",
        "issued_by_loop",
        "action_type",
        "quest_id",
        "recorded_at",
        "authorization",
    }
    missing = required - set(record)
    if missing:
        raise ValueError(f"governance authorization missing fields: {', '.join(sorted(missing))}")
    if record["schema"] != "sns.governance-authorization.v1":
        raise ValueError("unsupported governance authorization schema")
    if not _AUTH_RE.fullmatch(str(record["authorization_id"])):
        raise ValueError("authorization_id has invalid format")
    if record["issued_by_loop"] != "daily-governance-triage":
        raise ValueError("governance authorization must be issued by daily-governance-triage")
    if record["action_type"] != "refine_existing":
        raise ValueError("fast governance may authorize only refine_existing work")
    quest_id = str(record["quest_id"])
    if not _QUEST_RE.fullmatch(quest_id):
        raise ValueError("authorization quest_id has invalid format")
    if quest_id not in active_ids:
        raise ValueError("fast governance may authorize only an already-active quest")
    authorization = record["authorization"]
    if not isinstance(authorization, dict):
        raise ValueError("authorization must be an object")
    validate_triage_authorization(
        authorization,
        quest_id=quest_id,
        recorded_at=record["recorded_at"],
        delegations=delegations,
    )
