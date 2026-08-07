"""Shared-state ownership, snapshots, and repository semantic validation."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Iterable, Mapping

from .authorizations import validate_governance_authorization
from .contracts import ContractRegistry
from .governance import validate_delegation_envelope
from .receipts import ReceiptStore
from .semantics import cluster_evidence_events, consolidate_belief_events, validate_pr_lifecycle, validate_quest_action

_QUEST_RE = re.compile(r"(QST-[A-Z0-9]+-[0-9]{4})")
_SHA_RE = re.compile(r"^[0-9a-f]{40}$")


class ConflictKind(str, Enum):
    NONE = "none"
    SOURCE_COMMIT_CHANGED = "source_commit_changed"
    OWNED_STATE_CHANGED = "owned_state_changed"
    GOVERNANCE_CHANGED = "governance_changed"
    PR_OWNERSHIP_CHANGED = "pr_ownership_changed"


@dataclass(frozen=True)
class StateSnapshot:
    source_commit: str
    state_hash: str
    governance_hash: str
    pr_ownership_hash: str

    def validate(self) -> None:
        if not _SHA_RE.fullmatch(self.source_commit):
            raise ValueError("source_commit must be a lowercase 40-character Git SHA")
        for name in ("state_hash", "governance_hash", "pr_ownership_hash"):
            if not re.fullmatch(r"sha256:[0-9a-f]{64}", getattr(self, name)):
                raise ValueError(f"{name} must be sha256:<64 lowercase hex>")


def hash_bytes(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def hash_files(root: str | Path, paths: Iterable[str | Path]) -> str:
    base = Path(root)
    digest = hashlib.sha256()
    for item in sorted(str(Path(path)) for path in paths):
        path = base / item
        digest.update(item.encode())
        digest.update(b"\0")
        digest.update(path.read_bytes() if path.is_file() else b"<missing>")
        digest.update(b"\0")
    return "sha256:" + digest.hexdigest()


def classify_conflict(expected: StateSnapshot, current: StateSnapshot) -> ConflictKind:
    expected.validate()
    current.validate()
    if expected.pr_ownership_hash != current.pr_ownership_hash:
        return ConflictKind.PR_OWNERSHIP_CHANGED
    if expected.governance_hash != current.governance_hash:
        return ConflictKind.GOVERNANCE_CHANGED
    if expected.state_hash != current.state_hash:
        return ConflictKind.OWNED_STATE_CHANGED
    if expected.source_commit != current.source_commit:
        return ConflictKind.SOURCE_COMMIT_CHANGED
    return ConflictKind.NONE


def validate_ownership_matrix(matrix: Mapping[str, object]) -> None:
    if matrix.get("schema") != "sns.state-ownership.v1":
        raise ValueError("unsupported ownership schema")
    surfaces = matrix.get("surfaces")
    if not isinstance(surfaces, list) or not surfaces:
        raise ValueError("ownership matrix requires surfaces")
    seen: set[str] = set()
    authorities = {
        "daily-governance-triage",
        "daily-research-operator",
        "weekly-evidence-synthesis",
        "monthly-governance",
        "system-audit",
        "human",
    }
    permissions = {"read", "write", "propose", "none", "observe"}
    for surface in surfaces:
        if not isinstance(surface, dict):
            raise ValueError("each state surface must be an object")
        required = {"path", "authority", "triage", "daily", "weekly", "monthly", "audit", "reconciliation"}
        if required - set(surface):
            raise ValueError(f"state surface missing: {sorted(required - set(surface))}")
        path = str(surface["path"])
        if path in seen:
            raise ValueError(f"duplicate state surface: {path}")
        seen.add(path)
        if surface["authority"] not in authorities:
            raise ValueError(f"unknown authority for {path}")
        for key in ("triage", "daily", "weekly", "monthly", "audit"):
            if surface[key] not in permissions:
                raise ValueError(f"invalid {key} permission for {path}")
        if not str(surface["reconciliation"]).strip():
            raise ValueError(f"surface {path} requires a reconciliation rule")


def _load_json_files(directory: Path) -> list[dict[str, object]]:
    if not directory.exists():
        return []
    return [json.loads(path.read_text(encoding="utf-8")) for path in sorted(directory.glob("**/*.json"))]


def _quest_ids(directory: Path) -> set[str]:
    ids: set[str] = set()
    if not directory.exists():
        return ids
    for path in sorted(directory.glob("*.md")):
        if path.name == "README.md":
            continue
        match = _QUEST_RE.search(path.name) or _QUEST_RE.search(path.read_text(encoding="utf-8"))
        if match:
            ids.add(match.group(1))
    return ids


def validate_repository_state(root: str | Path, *, strict: bool = True) -> dict[str, object]:
    repo = Path(root)
    errors: list[str] = []
    counts: dict[str, int] = {}
    try:
        contracts = ContractRegistry.from_directory(repo / "automation/contracts")
        contracts.validate_required_loops()
    except Exception as exc:
        errors.append(f"contracts: {exc}")
        contracts = None
    try:
        validate_ownership_matrix(json.loads((repo / "automation/state_ownership.json").read_text(encoding="utf-8")))
    except Exception as exc:
        errors.append(f"ownership: {exc}")

    queues = {name: _quest_ids(repo / f"quests/{name}") for name in ("active", "completed", "proposed", "blocked")}
    counts.update({f"quests_{name}": len(ids) for name, ids in queues.items()})
    reverse: dict[str, list[str]] = {}
    for queue, ids in queues.items():
        for quest_id in ids:
            reverse.setdefault(quest_id, []).append(queue)
    duplicates = {quest_id: states for quest_id, states in reverse.items() if len(states) > 1}
    if duplicates:
        errors.append(f"quest IDs appear in multiple queues: {duplicates}")
    if not 1 <= len(queues["active"]) <= 8:
        errors.append(f"active quest queue must contain 1-8 quests, found {len(queues['active'])}")

    delegation_records = _load_json_files(repo / "automation/delegations")
    counts["governance_delegations"] = len(delegation_records)
    delegations: dict[str, dict[str, object]] = {}
    for envelope in delegation_records:
        try:
            validate_delegation_envelope(envelope)
            delegation_id = str(envelope["delegation_id"])
            if delegation_id in delegations:
                raise ValueError(f"duplicate delegation_id: {delegation_id}")
            delegations[delegation_id] = envelope
        except Exception as exc:
            errors.append(f"delegation {envelope.get('delegation_id', '<unknown>')}: {exc}")

    authorization_records = _load_json_files(repo / "automation/authorizations")
    counts["governance_authorizations"] = len(authorization_records)
    seen_authorizations: set[str] = set()
    for authorization in authorization_records:
        try:
            validate_governance_authorization(
                authorization,
                delegations=delegations,
                active_ids=queues["active"],
            )
            authorization_id = str(authorization["authorization_id"])
            if authorization_id in seen_authorizations:
                raise ValueError(f"duplicate authorization_id: {authorization_id}")
            seen_authorizations.add(authorization_id)
        except Exception as exc:
            errors.append(f"authorization {authorization.get('authorization_id', '<unknown>')}: {exc}")

    actions = _load_json_files(repo / "quests/actions")
    counts["quest_actions"] = len(actions)
    for action in actions:
        try:
            validate_quest_action(action, active_ids=queues["active"], completed_ids=queues["completed"], proposed_ids=queues["proposed"], blocked_ids=queues["blocked"])
        except Exception as exc:
            errors.append(f"quest action {action.get('quest_action_id', '<unknown>')}: {exc}")

    evidence = _load_json_files(repo / "calendar/evidence")
    beliefs = _load_json_files(repo / "calendar/belief_events")
    counts["evidence_events"] = len(evidence)
    counts["belief_events"] = len(beliefs)
    try:
        clusters = cluster_evidence_events(evidence) if evidence else {}
    except Exception as exc:
        errors.append(f"evidence: {exc}")
        clusters = {}
    try:
        consolidated = consolidate_belief_events(beliefs, evidence_ids={str(item["evidence_id"]) for item in evidence}) if beliefs else {}
    except Exception as exc:
        errors.append(f"beliefs: {exc}")
        consolidated = {}

    lifecycle = _load_json_files(repo / "automation/pr_lifecycle")
    counts["pr_lifecycle_records"] = len(lifecycle)
    ownership: dict[tuple[str, str], list[int]] = {}
    for record in lifecycle:
        try:
            validate_pr_lifecycle(record)
            if record["state"] not in {"merged", "superseded", "closed_abandoned"}:
                ownership.setdefault((str(record["quest_id"]), str(record["acceptance_slice"])), []).append(int(record["pr_number"]))
        except Exception as exc:
            errors.append(f"PR lifecycle {record.get('pr_number', '<unknown>')}: {exc}")
    duplicate_owners = {key: prs for key, prs in ownership.items() if len(prs) > 1}
    if duplicate_owners:
        errors.append(f"multiple active PR owners for one acceptance slice: {duplicate_owners}")

    try:
        receipts = ReceiptStore(repo / "automation/runs", contracts=contracts).load_all()
    except Exception as exc:
        errors.append(f"receipts: {exc}")
        receipts = []
    counts["run_receipts"] = len(receipts)
    receipt_ids = {str(item["run_id"]) for item in receipts}
    for record in lifecycle:
        owner_run = str(record.get("owner_run_id", ""))
        if owner_run and owner_run not in receipt_ids:
            errors.append(f"PR lifecycle {record.get('pr_number')} cites missing owner run {owner_run}")
    for receipt in receipts:
        for artifact in receipt.get("artifacts", []):
            artifact_path = artifact.get("path") if isinstance(artifact, dict) else artifact
            if artifact_path and not (repo / str(artifact_path)).exists():
                errors.append(f"receipt {receipt['run_id']} cites missing artifact {artifact_path}")

    report = {
        "schema": "sns.repository-validation.v1",
        "valid": not errors,
        "errors": errors,
        "counts": counts,
        "claim_clusters": len(clusters),
        "consolidated_beliefs": len(consolidated),
    }
    if errors and strict:
        raise ValueError("repository semantic validation failed:\n- " + "\n- ".join(errors))
    return report
