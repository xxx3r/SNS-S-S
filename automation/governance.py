"""Bounded delegation and fast-governance authorization rules."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Mapping

_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_QUEST_RE = re.compile(r"^QST-[A-Z0-9]+-[0-9]{4}$")
_DELEGATION_RE = re.compile(r"^DELEG-[A-Z0-9-]+$")

_PROTECTED_IMPLEMENTATION_PREFIXES = (
    "automation/",
    "calendar/",
    "memory/",
    "quests/",
    ".github/",
)


def _timestamp(value: object, field: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field} must be ISO-8601") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{field} must include a timezone")
    return parsed.astimezone(timezone.utc)


def _required(record: Mapping[str, object], fields: set[str], label: str) -> None:
    missing = fields - set(record)
    if missing:
        raise ValueError(f"{label} missing fields: {', '.join(sorted(missing))}")


def validate_delegation_envelope(envelope: Mapping[str, object]) -> None:
    _required(
        envelope,
        {
            "schema",
            "delegation_id",
            "period",
            "authority",
            "authorized_loop",
            "allowed_action_types",
            "allowed_quest_ids",
            "authorized_implementation_surfaces",
            "forbidden_surfaces",
            "max_authorizations_per_run",
            "max_pull_requests_per_authorization",
            "max_run_receipts_per_authorization",
            "required_checks",
            "recorded_at",
            "expires_at",
            "rationale",
        },
        "delegation envelope",
    )
    if envelope["schema"] != "sns.governance-delegation.v1":
        raise ValueError("unsupported governance delegation schema")
    if not _DELEGATION_RE.fullmatch(str(envelope["delegation_id"])):
        raise ValueError("delegation_id has invalid format")
    if envelope["authority"] not in {"monthly-governance", "explicit-human"}:
        raise ValueError("delegation authority must be monthly-governance or explicit-human")
    if envelope["authorized_loop"] != "daily-governance-triage":
        raise ValueError("delegation must target daily-governance-triage")

    actions = envelope["allowed_action_types"]
    if actions != ["refine_existing"]:
        raise ValueError("triage delegation may allow only refine_existing")

    quest_ids = envelope["allowed_quest_ids"]
    if not isinstance(quest_ids, list) or not quest_ids:
        raise ValueError("delegation requires at least one eligible active quest")
    if len(set(map(str, quest_ids))) != len(quest_ids):
        raise ValueError("delegation quest IDs must be unique")
    for quest_id in quest_ids:
        if not _QUEST_RE.fullmatch(str(quest_id)):
            raise ValueError(f"invalid delegated quest ID: {quest_id}")

    surfaces = envelope["authorized_implementation_surfaces"]
    if not isinstance(surfaces, list) or not surfaces:
        raise ValueError("delegation requires authorized implementation surfaces")
    for surface in surfaces:
        value = str(surface)
        if any(value.startswith(prefix) for prefix in _PROTECTED_IMPLEMENTATION_PREFIXES):
            raise ValueError(f"delegation cannot authorize protected implementation surface: {value}")

    forbidden = envelope["forbidden_surfaces"]
    if not isinstance(forbidden, list) or not forbidden:
        raise ValueError("delegation requires explicit forbidden surfaces")

    if not 1 <= int(envelope["max_authorizations_per_run"]) <= 8:
        raise ValueError("max_authorizations_per_run must be in [1, 8]")
    if int(envelope["max_pull_requests_per_authorization"]) != 1:
        raise ValueError("each triage authorization must allow exactly one implementation PR")
    if int(envelope["max_run_receipts_per_authorization"]) != 1:
        raise ValueError("each triage authorization must allow exactly one implementation receipt")

    checks = envelope["required_checks"]
    if not isinstance(checks, list) or not checks or any(not str(check).strip() for check in checks):
        raise ValueError("delegation requires non-empty required checks")

    recorded = _timestamp(envelope["recorded_at"], "recorded_at")
    expires = _timestamp(envelope["expires_at"], "expires_at")
    if expires <= recorded:
        raise ValueError("delegation expiry must follow recorded_at")
    if not str(envelope["rationale"]).strip():
        raise ValueError("delegation rationale cannot be empty")


def validate_triage_authorization(
    authorization: Mapping[str, object],
    *,
    quest_id: str,
    recorded_at: object,
    delegations: Mapping[str, Mapping[str, object]],
) -> None:
    _required(
        authorization,
        {
            "delegation_id",
            "authorized_loop",
            "acceptance_slice",
            "source_commit",
            "expires_at",
            "allowed_write_surfaces",
            "budgets",
            "max_pull_requests",
            "max_run_receipts",
            "mandatory_checks",
            "stop_conditions",
            "next_action",
        },
        "triage authorization",
    )
    delegation_id = str(authorization["delegation_id"])
    try:
        envelope = delegations[delegation_id]
    except KeyError as exc:
        raise ValueError(f"triage authorization cites missing delegation: {delegation_id}") from exc
    validate_delegation_envelope(envelope)

    action_time = _timestamp(recorded_at, "recorded_at")
    delegation_recorded = _timestamp(envelope["recorded_at"], "delegation recorded_at")
    delegation_expires = _timestamp(envelope["expires_at"], "delegation expires_at")
    authorization_expires = _timestamp(authorization["expires_at"], "authorization expires_at")
    if action_time < delegation_recorded or action_time >= delegation_expires:
        raise ValueError("triage authorization was issued outside its delegation validity window")
    if authorization_expires <= action_time or authorization_expires > delegation_expires:
        raise ValueError("triage authorization expiry must follow issuance and remain inside delegation expiry")

    if quest_id not in set(map(str, envelope["allowed_quest_ids"])):
        raise ValueError(f"quest {quest_id} is outside the delegation envelope")
    if authorization["authorized_loop"] != "daily-research-operator":
        raise ValueError("triage may authorize only the Daily Research Operator")
    if not str(authorization["acceptance_slice"]).strip():
        raise ValueError("authorization acceptance_slice cannot be empty")
    if not _SHA_RE.fullmatch(str(authorization["source_commit"])):
        raise ValueError("authorization source_commit must be a lowercase 40-character Git SHA")

    allowed = authorization["allowed_write_surfaces"]
    if not isinstance(allowed, list) or not allowed:
        raise ValueError("authorization requires allowed_write_surfaces")
    delegated_surfaces = set(map(str, envelope["authorized_implementation_surfaces"]))
    for surface in allowed:
        value = str(surface)
        if value not in delegated_surfaces:
            raise ValueError(f"authorization surface is outside delegation: {value}")
        if any(value.startswith(prefix) for prefix in _PROTECTED_IMPLEMENTATION_PREFIXES):
            raise ValueError(f"authorization cannot include protected surface: {value}")

    budgets = authorization["budgets"]
    if not isinstance(budgets, dict) or not budgets:
        raise ValueError("authorization budgets must be a non-empty object")
    if int(authorization["max_pull_requests"]) != 1:
        raise ValueError("authorization must allow exactly one implementation PR")
    if int(authorization["max_run_receipts"]) != 1:
        raise ValueError("authorization must allow exactly one implementation receipt")

    mandatory_checks = authorization["mandatory_checks"]
    if not isinstance(mandatory_checks, list) or not mandatory_checks:
        raise ValueError("authorization requires mandatory checks")
    required_checks = set(map(str, envelope["required_checks"]))
    if not required_checks.issubset(set(map(str, mandatory_checks))):
        raise ValueError("authorization omits delegation-required checks")

    stop_conditions = authorization["stop_conditions"]
    if not isinstance(stop_conditions, list) or not stop_conditions:
        raise ValueError("authorization requires stop conditions")
    if not str(authorization["next_action"]).strip():
        raise ValueError("authorization next_action cannot be empty")
