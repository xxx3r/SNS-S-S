"""Semantic event validation for evidence, beliefs, quests, and PRs."""

from __future__ import annotations

import re
from collections import defaultdict
from datetime import datetime
from typing import Iterable, Mapping

from .ids import validate_identifier
from .models import BeliefEffect, EvidencePolarity, PRLifecycleState, QuestActionType

_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_QUEST_RE = re.compile(r"^QST-[A-Z0-9]+-[0-9]{4}$")


def _timestamp(value: object, field: str) -> None:
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field} must be ISO-8601") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{field} must include a timezone")


def _required(record: Mapping[str, object], fields: set[str], label: str) -> None:
    missing = fields - set(record)
    if missing:
        raise ValueError(f"{label} missing fields: {', '.join(sorted(missing))}")


def validate_evidence_event(event: Mapping[str, object]) -> None:
    _required(
        event,
        {
            "schema", "evidence_id", "claim_cluster_id", "claim", "source_uri",
            "source_kind", "source_fingerprint", "observed_at", "independence",
            "polarity", "confidence", "provenance",
        },
        "evidence event",
    )
    if event["schema"] != "sns.evidence-event.v1":
        raise ValueError("unsupported evidence schema")
    validate_identifier(str(event["evidence_id"]), prefix="EVID")
    validate_identifier(str(event["claim_cluster_id"]), prefix="CLM")
    if not str(event["claim"]).strip():
        raise ValueError("claim cannot be empty")
    if not str(event["source_uri"]).strip():
        raise ValueError("source_uri cannot be empty")
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", str(event["source_fingerprint"])):
        raise ValueError("source_fingerprint must be sha256:<64 lowercase hex>")
    _timestamp(event["observed_at"], "observed_at")
    if event["independence"] not in {"independent", "shared_origin", "unknown"}:
        raise ValueError("invalid independence classification")
    if event["polarity"] not in {value.value for value in EvidencePolarity}:
        raise ValueError("invalid evidence polarity")
    confidence = float(event["confidence"])
    if not 0.0 <= confidence <= 1.0:
        raise ValueError("evidence confidence must be in [0, 1]")
    provenance = event["provenance"]
    if not isinstance(provenance, dict) or not provenance:
        raise ValueError("provenance must be a non-empty object")


def cluster_evidence_events(events: Iterable[Mapping[str, object]]) -> dict[str, dict[str, object]]:
    """Group reports by underlying claim cluster without erasing source diversity."""

    clusters: dict[str, list[Mapping[str, object]]] = defaultdict(list)
    seen_evidence_ids: set[str] = set()
    seen_fingerprints: set[str] = set()
    for event in events:
        validate_evidence_event(event)
        evidence_id = str(event["evidence_id"])
        fingerprint = str(event["source_fingerprint"])
        if evidence_id in seen_evidence_ids:
            raise ValueError(f"duplicate evidence_id: {evidence_id}")
        if fingerprint in seen_fingerprints:
            raise ValueError(f"duplicate source fingerprint: {fingerprint}")
        seen_evidence_ids.add(evidence_id)
        seen_fingerprints.add(fingerprint)
        clusters[str(event["claim_cluster_id"])].append(event)

    result: dict[str, dict[str, object]] = {}
    for cluster_id, members in sorted(clusters.items()):
        independent = [member for member in members if member["independence"] == "independent"]
        result[cluster_id] = {
            "claim_cluster_id": cluster_id,
            "claim": members[0]["claim"],
            "evidence_ids": [member["evidence_id"] for member in members],
            "source_count": len(members),
            "independent_source_count": len(independent),
            "polarities": sorted({str(member["polarity"]) for member in members}),
            "max_confidence": max(float(member["confidence"]) for member in members),
        }
    return result


def validate_belief_event(event: Mapping[str, object], *, evidence_ids: set[str] | None = None) -> None:
    _required(
        event,
        {
            "schema", "belief_event_id", "belief_key", "evidence_ids", "magnitude",
            "confidence", "effect", "rationale", "recorded_at",
        },
        "belief event",
    )
    if event["schema"] != "sns.belief-event.v1":
        raise ValueError("unsupported belief schema")
    validate_identifier(str(event["belief_event_id"]), prefix="BEL")
    if not str(event["belief_key"]).strip():
        raise ValueError("belief_key cannot be empty")
    refs = event["evidence_ids"]
    if not isinstance(refs, list) or not refs:
        raise ValueError("belief event must cite at least one evidence ID")
    for evidence_id in refs:
        validate_identifier(str(evidence_id), prefix="EVID")
        if evidence_ids is not None and evidence_id not in evidence_ids:
            raise ValueError(f"belief event cites missing evidence: {evidence_id}")
    magnitude = float(event["magnitude"])
    confidence = float(event["confidence"])
    if not -1.0 <= magnitude <= 1.0:
        raise ValueError("belief magnitude must be in [-1, 1]")
    if not 0.0 <= confidence <= 1.0:
        raise ValueError("belief confidence must be in [0, 1]")
    if event["effect"] not in {value.value for value in BeliefEffect}:
        raise ValueError("invalid belief effect")
    if not str(event["rationale"]).strip():
        raise ValueError("belief rationale cannot be empty")
    _timestamp(event["recorded_at"], "recorded_at")


def consolidate_belief_events(
    events: Iterable[Mapping[str, object]],
    *,
    evidence_ids: set[str] | None = None,
) -> dict[str, dict[str, object]]:
    """Create a traceable weighted summary without mutating raw belief events."""

    grouped: dict[str, list[Mapping[str, object]]] = defaultdict(list)
    seen: set[str] = set()
    for event in events:
        validate_belief_event(event, evidence_ids=evidence_ids)
        event_id = str(event["belief_event_id"])
        if event_id in seen:
            raise ValueError(f"duplicate belief_event_id: {event_id}")
        seen.add(event_id)
        grouped[str(event["belief_key"])].append(event)

    consolidated: dict[str, dict[str, object]] = {}
    for key, members in sorted(grouped.items()):
        total_weight = sum(float(member["confidence"]) for member in members)
        weighted = sum(float(member["magnitude"]) * float(member["confidence"]) for member in members)
        magnitude = weighted / total_weight if total_weight else 0.0
        consolidated[key] = {
            "belief_key": key,
            "magnitude": max(-1.0, min(1.0, magnitude)),
            "confidence": min(1.0, total_weight / max(1, len(members))),
            "belief_event_ids": [member["belief_event_id"] for member in members],
            "evidence_ids": sorted({eid for member in members for eid in member["evidence_ids"]}),
        }
    return consolidated


def validate_quest_action(
    action: Mapping[str, object],
    *,
    active_ids: set[str],
    completed_ids: set[str],
    proposed_ids: set[str],
    blocked_ids: set[str],
) -> None:
    _required(
        action,
        {
            "schema", "quest_action_id", "action_type", "quest_id", "target_quest_ids",
            "proposed_by_loop", "authority", "rationale", "recorded_at",
        },
        "quest action",
    )
    if action["schema"] != "sns.quest-action.v1":
        raise ValueError("unsupported quest-action schema")
    validate_identifier(str(action["quest_action_id"]), prefix="QA")
    action_type = str(action["action_type"])
    if action_type not in {value.value for value in QuestActionType}:
        raise ValueError("invalid quest action type")
    quest_id = str(action["quest_id"])
    if action_type != QuestActionType.NO_ACTION.value and not _QUEST_RE.fullmatch(quest_id):
        raise ValueError("quest_id has invalid format")
    targets = action["target_quest_ids"]
    if not isinstance(targets, list):
        raise ValueError("target_quest_ids must be a list")

    all_ids = active_ids | completed_ids | proposed_ids | blocked_ids
    if action_type == QuestActionType.PROPOSE_NEW.value:
        if quest_id in all_ids:
            raise ValueError(f"new quest reuses existing ID: {quest_id}")
    elif action_type == QuestActionType.REFINE_EXISTING.value:
        if quest_id not in active_ids:
            raise ValueError("refinement must target an active quest")
    elif action_type in {QuestActionType.BLOCK.value, QuestActionType.RETIRE.value}:
        if quest_id not in active_ids:
            raise ValueError(f"{action_type} must target an active quest")
    elif action_type == QuestActionType.MERGE_WITH.value:
        if quest_id not in active_ids or not targets:
            raise ValueError("merge_with requires an active quest and at least one target")
        missing_targets = set(map(str, targets)) - all_ids
        if missing_targets:
            raise ValueError(f"merge targets do not exist: {sorted(missing_targets)}")
    elif action_type == QuestActionType.NO_ACTION.value:
        if quest_id:
            raise ValueError("no_action must use an empty quest_id")

    authority = str(action["authority"])
    loop = str(action["proposed_by_loop"])
    if authority not in {"proposal", "enacted", "emergency_escalation"}:
        raise ValueError("invalid quest action authority")
    if loop == "weekly-evidence-synthesis" and authority == "enacted":
        raise ValueError("weekly evidence may propose but not enact queue governance")
    if authority == "enacted" and loop not in {"monthly-governance", "daily-research-operator"}:
        raise ValueError("only monthly governance or scoped daily execution may enact actions")
    _timestamp(action["recorded_at"], "recorded_at")


def validate_pr_lifecycle(record: Mapping[str, object]) -> None:
    _required(
        record,
        {
            "schema", "pr_number", "quest_id", "acceptance_slice", "state",
            "owner_run_id", "source_commit", "head_commit", "updated_at",
            "next_review_after", "supersedes",
        },
        "PR lifecycle",
    )
    if record["schema"] != "sns.pr-lifecycle.v1":
        raise ValueError("unsupported PR lifecycle schema")
    if int(record["pr_number"]) <= 0:
        raise ValueError("pr_number must be positive")
    quest_id = str(record["quest_id"])
    if quest_id and not _QUEST_RE.fullmatch(quest_id):
        raise ValueError("quest_id has invalid format")
    if not str(record["acceptance_slice"]).strip():
        raise ValueError("acceptance_slice cannot be empty")
    if record["state"] not in {value.value for value in PRLifecycleState}:
        raise ValueError("invalid PR lifecycle state")
    validate_identifier(str(record["owner_run_id"]), prefix="RUN")
    for field in ("source_commit", "head_commit"):
        if not _SHA_RE.fullmatch(str(record[field])):
            raise ValueError(f"{field} must be a lowercase 40-character Git SHA")
    _timestamp(record["updated_at"], "updated_at")
    _timestamp(record["next_review_after"], "next_review_after")
    if not isinstance(record["supersedes"], list):
        raise ValueError("supersedes must be a list")
