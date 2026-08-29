"""Deterministic provenance primitives for autonomous loop receipts.

The connector-facing snapshot is intentionally inspectable: it records the exact
Git blob identities of a small canonical state set plus the live PR ownership
rows observed by the loop.  It does not ask an LLM to invent an opaque hash.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Iterable, Mapping, Sequence

_SHA_RE = re.compile(r"^[0-9a-f]{40}$")

STATE_SNAPSHOT_SCHEMA = "sns.state-snapshot.v1"
RUN_RECEIPT_SCHEMA = "sns.loop-run.v2"

BASE_SNAPSHOT_ROLES = {
    "stable_law",
    "active_contract",
    "state_ownership",
    "active_quest_index",
    "research_graph",
    "runtime_manifest",
    "canonical_memory",
}


def git_blob_sha(payload: bytes) -> str:
    """Return the Git blob SHA-1 for raw file bytes without invoking git."""

    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def snapshot_fingerprint(snapshot: Mapping[str, object]) -> str:
    """Return a deterministic convenience digest of the inspectable snapshot.

    The digest is derivative only.  The receipt authority is the snapshot object
    itself, whose component Git identities remain directly auditable.
    """

    payload = dict(snapshot)
    payload.pop("fingerprint", None)
    return "sha256:" + hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def normalize_open_prs(rows: Iterable[Mapping[str, object]]) -> list[dict[str, object]]:
    normalized: list[dict[str, object]] = []
    seen: set[int] = set()
    for row in rows:
        number = int(row["number"])
        if number in seen:
            raise ValueError(f"duplicate open PR number in snapshot: {number}")
        seen.add(number)
        head_sha = str(row["head_sha"])
        if not _SHA_RE.fullmatch(head_sha):
            raise ValueError("open PR head_sha must be a lowercase 40-character Git SHA")
        state = str(row.get("state", "open"))
        if state != "open":
            raise ValueError("state snapshot may contain only open PR ownership rows")
        normalized.append(
            {
                "number": number,
                "head_sha": head_sha,
                "draft": bool(row.get("draft", False)),
                "state": "open",
            }
        )
    return sorted(normalized, key=lambda item: int(item["number"]))


def build_state_snapshot(
    root: str | Path,
    *,
    source_commit: str,
    records: Mapping[str, str],
    open_prs: Sequence[Mapping[str, object]] = (),
) -> dict[str, object]:
    """Build the canonical snapshot from named repository records.

    `records` maps semantic roles to paths.  The same role/path list can be
    reproduced from a GitHub connector by using each fetched file's returned
    blob SHA instead of reading a local checkout.
    """

    if not _SHA_RE.fullmatch(source_commit):
        raise ValueError("source_commit must be a lowercase 40-character Git SHA")
    missing_roles = BASE_SNAPSHOT_ROLES - set(records)
    if missing_roles:
        raise ValueError(f"snapshot missing canonical roles: {', '.join(sorted(missing_roles))}")

    base = Path(root)
    entries: list[dict[str, str]] = []
    seen_paths: set[str] = set()
    for role, raw_path in sorted(records.items()):
        role_name = str(role).strip()
        path = str(Path(raw_path))
        if not role_name or not path:
            raise ValueError("snapshot roles and paths must be non-empty")
        if path in seen_paths:
            raise ValueError(f"snapshot path assigned more than once: {path}")
        seen_paths.add(path)
        file_path = base / path
        if not file_path.is_file():
            raise ValueError(f"snapshot record does not exist: {path}")
        entries.append({"role": role_name, "path": path, "git_blob_sha": git_blob_sha(file_path.read_bytes())})

    snapshot: dict[str, object] = {
        "schema": STATE_SNAPSHOT_SCHEMA,
        "source_commit": source_commit,
        "records": entries,
        "open_prs": normalize_open_prs(open_prs),
    }
    snapshot["fingerprint"] = snapshot_fingerprint(snapshot)
    validate_state_snapshot(snapshot)
    return snapshot


def validate_state_snapshot(snapshot: Mapping[str, object]) -> None:
    required = {"schema", "source_commit", "records", "open_prs", "fingerprint"}
    missing = required - set(snapshot)
    if missing:
        raise ValueError(f"state snapshot missing fields: {', '.join(sorted(missing))}")
    if snapshot["schema"] != STATE_SNAPSHOT_SCHEMA:
        raise ValueError("unsupported state snapshot schema")
    if not _SHA_RE.fullmatch(str(snapshot["source_commit"])):
        raise ValueError("state snapshot source_commit must be a lowercase 40-character Git SHA")

    records = snapshot["records"]
    if not isinstance(records, list) or not records:
        raise ValueError("state snapshot records must be a non-empty list")
    roles: set[str] = set()
    paths: set[str] = set()
    for entry in records:
        if not isinstance(entry, dict) or set(entry) != {"role", "path", "git_blob_sha"}:
            raise ValueError("each state snapshot record requires only role, path, and git_blob_sha")
        role = str(entry["role"])
        path = str(entry["path"])
        blob_sha = str(entry["git_blob_sha"])
        if not role or not path:
            raise ValueError("state snapshot role/path cannot be empty")
        if role in roles or path in paths:
            raise ValueError("state snapshot roles and paths must be unique")
        roles.add(role)
        paths.add(path)
        if not _SHA_RE.fullmatch(blob_sha):
            raise ValueError("state snapshot git_blob_sha must be a lowercase 40-character Git SHA")
    missing_roles = BASE_SNAPSHOT_ROLES - roles
    if missing_roles:
        raise ValueError(f"state snapshot missing canonical roles: {', '.join(sorted(missing_roles))}")

    open_prs = snapshot["open_prs"]
    if not isinstance(open_prs, list):
        raise ValueError("state snapshot open_prs must be a list")
    normalized = normalize_open_prs(open_prs)
    if normalized != open_prs:
        raise ValueError("state snapshot open_prs must be canonical and sorted")

    fingerprint = str(snapshot["fingerprint"])
    if fingerprint != snapshot_fingerprint(snapshot):
        raise ValueError("state snapshot fingerprint does not match its inspectable content")


def snapshot_from_connector_records(
    *,
    source_commit: str,
    records: Sequence[Mapping[str, object]],
    open_prs: Sequence[Mapping[str, object]] = (),
) -> dict[str, object]:
    """Build a canonical snapshot from GitHub connector file identities.

    Each connector row must contain `role`, `path`, and the `git_blob_sha`
    returned by a repository file read.  This is the runtime-safe path when an
    agent has GitHub access but no local shell.
    """

    entries = [
        {
            "role": str(item["role"]),
            "path": str(item["path"]),
            "git_blob_sha": str(item["git_blob_sha"]),
        }
        for item in records
    ]
    snapshot: dict[str, object] = {
        "schema": STATE_SNAPSHOT_SCHEMA,
        "source_commit": source_commit,
        "records": sorted(entries, key=lambda item: (item["role"], item["path"])),
        "open_prs": normalize_open_prs(open_prs),
    }
    snapshot["fingerprint"] = snapshot_fingerprint(snapshot)
    validate_state_snapshot(snapshot)
    return snapshot


def build_run_receipt_v2(
    draft: Mapping[str, object],
    *,
    state_snapshot: Mapping[str, object],
    receipt_kind: str = "run",
    correction_of: str | None = None,
) -> dict[str, object]:
    """Stamp semantic receipt content into the current provenance envelope."""

    result = dict(draft)
    result["schema"] = RUN_RECEIPT_SCHEMA
    result.pop("state_hash", None)
    result["state_snapshot"] = dict(state_snapshot)
    result["receipt_kind"] = receipt_kind
    if correction_of is None:
        result.pop("correction_of", None)
    else:
        result["correction_of"] = correction_of
    return result


def implementation_receipts_for_authorization(
    receipts: Iterable[Mapping[str, object]], authorization_id: str
) -> list[Mapping[str, object]]:
    """Return budget-consuming receipts for one authorization.

    Append-only provenance corrections are deliberately excluded.  A malformed
    immutable receipt can therefore be corrected without granting a second
    scientific implementation attempt.
    """

    result: list[Mapping[str, object]] = []
    for receipt in receipts:
        if authorization_id not in set(map(str, receipt.get("consumed_ids", []))):
            continue
        if receipt.get("schema") == RUN_RECEIPT_SCHEMA and receipt.get("receipt_kind") == "correction":
            continue
        result.append(receipt)
    return result
