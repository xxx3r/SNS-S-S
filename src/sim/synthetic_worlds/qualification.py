"""Deny-by-default privacy scan, export manifest, and qualification receipt."""
from __future__ import annotations

import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .common import EXPORT_MANIFEST_SCHEMA, HUMAN_RELEASE_STATE, RECEIPT_SCHEMA, TERMINAL_STATE, ValidationError, file_sha256, load_json, safe_relative, stable_hash
from .recipe import load_recipe
from .shards import read_shards

_REVIEW_TERMS = re.compile(r"<!--\s*PRIVATE_REVIEW_DENYLIST_JSON\s*(\[.*?\])\s*PRIVATE_REVIEW_DENYLIST_JSON\s*-->", re.DOTALL)
_SECRET_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"(?i)\b(?:api[_-]?key|access[_-]?token|secret[_-]?key|password)\s*[:=]\s*['\"]?[^\s'\"]{8,}"),
    re.compile(r"https?://[^\s/:]+:[^\s/@]+@"),
    re.compile(r"(?<![A-Za-z0-9_])/(?:Users|home|workspace|mnt)/[A-Za-z0-9_.-]+/"),
)


def _ignored(path: Path) -> bool:
    return any(part in {"__pycache__", ".pytest_cache", ".git"} for part in path.parts) or path.name in {"EXPORT_MANIFEST.json", ".DS_Store"} or path.name.endswith((".pyc", ".pyo"))


def candidate_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*") if path.is_file() and not _ignored(path))


def _terms(review: Path) -> list[str]:
    match = _REVIEW_TERMS.search(review.read_text(encoding="utf-8"))
    if not match:
        raise ValidationError("security review is missing the structured denylist")
    terms = json.loads(match.group(1))
    if not isinstance(terms, list) or not terms or any(not isinstance(term, str) or not term for term in terms):
        raise ValidationError("security review denylist is invalid")
    return terms


def scan_candidate_tree(root: str | Path) -> dict[str, int]:
    root = Path(root); review = root / "SECURITY_AND_SCOPE_REVIEW.md"; terms = _terms(review)
    findings, scanned = [], 0
    for path in candidate_files(root):
        relative = path.relative_to(root).as_posix()
        if relative == "SECURITY_AND_SCOPE_REVIEW.md":
            continue
        if path.stat().st_size > 2_000_000:
            findings.append(f"oversize file: {relative}"); continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            findings.append(f"binary file: {relative}"); continue
        scanned += 1
        for term in terms:
            pattern = r"(?<![A-Za-z0-9_])" + re.escape(term) + r"(?![A-Za-z0-9_])"
            if re.search(pattern, text, flags=re.IGNORECASE):
                findings.append(f"private term {term!r} in {relative}")
        if any(pattern.search(text) for pattern in _SECRET_PATTERNS):
            findings.append(f"secret or private-path pattern in {relative}")
    if findings:
        raise ValidationError("candidate privacy scan failed: " + "; ".join(findings))
    return {"scanned_files": scanned, "private_term_count": len(terms), "findings": 0}


def build_export_manifest(root: str | Path, recipe: Mapping[str, Any], shards: Mapping[str, Any], *, qualified_source_fingerprint: str, test_result: str) -> dict[str, Any]:
    root = Path(root); scan = scan_candidate_tree(root)
    files = []
    for path in candidate_files(root):
        relative = path.relative_to(root).as_posix()
        files.append({
            "source_path": relative,
            "destination_path": relative,
            "purpose": "allowlisted synthetic-world candidate file",
            "transformation": "new neutral standalone implementation or reviewed candidate artifact",
            "dependencies": ["python-stdlib"],
            "tests": ["pytest -q tests", "python -m synthetic_worlds.cli validate-export EXPORT_MANIFEST.json"],
            "reviewer_disposition": "INCLUDED_AFTER_PRIVATE_REVIEW",
            "bytes": path.stat().st_size,
            "sha256": file_sha256(path),
        })
    receipt_payload = {
        "schema_version": RECEIPT_SCHEMA,
        "terminal_state": TERMINAL_STATE,
        "human_release_state": HUMAN_RELEASE_STATE,
        "recipe_sha256": stable_hash(recipe),
        "shard_manifest_sha256": stable_hash(shards),
        "file_set_sha256": stable_hash(files),
        "privacy_scan": scan,
        "isolated_test_command": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. pytest -q tests && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python -m synthetic_worlds.cli validate-export EXPORT_MANIFEST.json",
        "isolated_test_result": test_result,
    }
    receipt = {**receipt_payload, "receipt_sha256": stable_hash(receipt_payload)}
    payload = {
        "schema_version": EXPORT_MANIFEST_SCHEMA,
        "candidate_identity": "synthetic_worlds",
        "candidate_version": "0.1.0-candidate",
        "qualified_source_fingerprint": qualified_source_fingerprint,
        "runtime_dependencies": ["Python 3.10+ standard library"],
        "test_dependencies": ["pytest>=8,<9"],
        "recipe_path": "example_recipes/basic_world.json",
        "recipe_sha256": stable_hash(recipe),
        "shard_manifest": dict(shards),
        "files": files,
        "privacy_review_state": "COMPLETE",
        "human_release_state": HUMAN_RELEASE_STATE,
        "terminal_state": TERMINAL_STATE,
        "qualification_receipt": receipt,
    }
    return {**payload, "manifest_sha256": stable_hash(payload)}


def validate_export_manifest(manifest_path: str | Path, export_root: str | Path | None = None) -> dict[str, Any]:
    path = Path(manifest_path); root = Path(export_root) if export_root is not None else path.parent; manifest = load_json(path)
    required = {"schema_version", "candidate_identity", "candidate_version", "qualified_source_fingerprint", "runtime_dependencies", "test_dependencies", "recipe_path", "recipe_sha256", "shard_manifest", "files", "privacy_review_state", "human_release_state", "terminal_state", "qualification_receipt", "manifest_sha256"}
    if not isinstance(manifest, dict) or set(manifest) != required or manifest["schema_version"] != EXPORT_MANIFEST_SCHEMA:
        raise ValidationError("export manifest schema mismatch")
    if manifest["manifest_sha256"] != stable_hash({key: value for key, value in manifest.items() if key != "manifest_sha256"}):
        raise ValidationError("export manifest self-hash mismatch")
    if manifest["terminal_state"] != TERMINAL_STATE or manifest["human_release_state"] != HUMAN_RELEASE_STATE:
        raise ValidationError("export state mismatch")
    recipe = load_recipe(str(root / safe_relative(manifest["recipe_path"], "recipe path")))
    if manifest["recipe_sha256"] != stable_hash(recipe):
        raise ValidationError("export recipe hash mismatch")
    entries, listed = manifest["files"], []
    if not isinstance(entries, list) or not entries:
        raise ValidationError("export manifest has no files")
    entry_keys = {"source_path", "destination_path", "purpose", "transformation", "dependencies", "tests", "reviewer_disposition", "bytes", "sha256"}
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != entry_keys:
            raise ValidationError("export allowlist entry schema mismatch")
        source, destination = safe_relative(entry["source_path"], "source path"), safe_relative(entry["destination_path"], "destination path")
        if source != destination:
            raise ValidationError("candidate source and destination paths must match")
        file = root / destination
        if not file.is_file() or file.stat().st_size != entry["bytes"] or file_sha256(file) != entry["sha256"]:
            raise ValidationError(f"export file identity mismatch: {destination}")
        listed.append(destination)
    actual = [file.relative_to(root).as_posix() for file in candidate_files(root)]
    if len(set(listed)) != len(listed) or sorted(listed) != sorted(actual):
        raise ValidationError("export allowlist does not match exact file set")
    rows = list(read_shards(root / "shards", manifest["shard_manifest"])); scan = scan_candidate_tree(root); receipt = manifest["qualification_receipt"]
    receipt_keys = {"schema_version", "terminal_state", "human_release_state", "recipe_sha256", "shard_manifest_sha256", "file_set_sha256", "privacy_scan", "isolated_test_command", "isolated_test_result", "receipt_sha256"}
    if not isinstance(receipt, dict) or set(receipt) != receipt_keys or receipt["receipt_sha256"] != stable_hash({key: value for key, value in receipt.items() if key != "receipt_sha256"}):
        raise ValidationError("qualification receipt schema or hash mismatch")
    bindings = (receipt["schema_version"] == RECEIPT_SCHEMA, receipt["terminal_state"] == TERMINAL_STATE, receipt["human_release_state"] == HUMAN_RELEASE_STATE, receipt["recipe_sha256"] == manifest["recipe_sha256"], receipt["shard_manifest_sha256"] == stable_hash(manifest["shard_manifest"]), receipt["file_set_sha256"] == stable_hash(entries), receipt["privacy_scan"] == scan)
    if not all(bindings):
        raise ValidationError("qualification receipt bindings mismatch")
    return {"terminal_state": TERMINAL_STATE, "human_release_state": HUMAN_RELEASE_STATE, "records": len(rows), "files": len(entries)}
