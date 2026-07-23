"""Atomic JSONL shards and strict dataset manifests."""
from __future__ import annotations

import json
import math
import shutil
import tempfile
from collections.abc import Iterable, Iterator, Mapping, Sequence
from pathlib import Path
from typing import Any

from .common import Budget, DATASET_MANIFEST_SCHEMA, RECORD_SCHEMA, ValidationError, file_sha256, safe_relative, stable_hash, stable_json, strict_object

_RECORD_KEYS = {"schema_version", "record_id", "parameters", "samples", "rng", "record_hash"}
_SHARD_KEYS = {"path", "records", "bytes", "sha256"}


def _record(row: Any, expected_id: int | None = None) -> dict[str, Any]:
    if not isinstance(row, dict) or set(row) != _RECORD_KEYS or row["schema_version"] != RECORD_SCHEMA:
        raise ValidationError("record schema mismatch")
    record_id = row["record_id"]
    if not isinstance(record_id, int) or isinstance(record_id, bool) or record_id < 0 or (expected_id is not None and record_id != expected_id):
        raise ValidationError("record_id sequence mismatch")
    expected = row["record_hash"]
    if not isinstance(expected, str) or expected != stable_hash({key: value for key, value in row.items() if key != "record_hash"}):
        raise ValidationError("record hash mismatch")
    return row


def _write_one(directory: Path, index: int, rows: Sequence[Mapping[str, Any]], budget: Budget) -> dict[str, Any]:
    path = directory / f"shard-{index:05d}.jsonl"
    byte_count = 0
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            encoded = (stable_json(row) + "\n").encode()
            byte_count += len(encoded)
            if byte_count > budget.max_bytes:
                raise ValidationError("single shard exceeds byte budget")
            handle.write(encoded.decode())
    return {"path": path.name, "records": len(rows), "bytes": byte_count, "sha256": file_sha256(path)}


def write_shards(records: Iterable[Mapping[str, Any]], out_dir: str | Path, shard_size: int = 1000, budget: Budget | None = None, *, expected_records: int | None = None) -> dict[str, Any]:
    budget = budget or Budget(); budget.validate()
    if not isinstance(shard_size, int) or isinstance(shard_size, bool) or shard_size < 1:
        raise ValidationError("shard_size must be positive")
    if expected_records is not None and (expected_records > budget.max_records or math.ceil(expected_records / shard_size) > budget.max_shards):
        raise ValidationError("planned records or shards exceed budget")
    destination = Path(out_dir)
    if destination.exists() and any(destination.iterdir()):
        raise ValidationError("output shard directory must be absent or empty")
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f".{destination.name}.tmp-", dir=destination.parent))
    shards, buffer, total, total_bytes = [], [], 0, 0
    try:
        for item in records:
            row = _record(dict(item), total)
            buffer.append(row); total += 1
            if total > budget.max_records:
                raise ValidationError("record write exceeds budget")
            if len(buffer) == shard_size:
                shard = _write_one(temporary, len(shards), buffer, budget)
                shards.append(shard); total_bytes += shard["bytes"]; buffer = []
        if buffer:
            shard = _write_one(temporary, len(shards), buffer, budget)
            shards.append(shard); total_bytes += shard["bytes"]
        if not shards or (expected_records is not None and total != expected_records) or len(shards) > budget.max_shards or total_bytes > budget.max_bytes:
            raise ValidationError("written shard totals violate the declared contract")
        if destination.exists():
            destination.rmdir()
        temporary.replace(destination)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    return {"schema_version": DATASET_MANIFEST_SCHEMA, "record_schema_version": RECORD_SCHEMA, "record_count": total, "shard_count": len(shards), "total_bytes": total_bytes, "shards": shards}


def read_shards(directory: str | Path, manifest: Mapping[str, Any]) -> Iterator[dict[str, Any]]:
    required = {"schema_version", "record_schema_version", "record_count", "shard_count", "total_bytes", "shards"}
    if not isinstance(manifest, Mapping) or set(manifest) != required or manifest["schema_version"] != DATASET_MANIFEST_SCHEMA or manifest["record_schema_version"] != RECORD_SCHEMA:
        raise ValidationError("dataset manifest schema mismatch")
    shards = manifest["shards"]
    if not isinstance(shards, list) or not shards:
        raise ValidationError("dataset manifest must list shards")
    listed = []
    for shard in shards:
        if not isinstance(shard, Mapping) or set(shard) != _SHARD_KEYS:
            raise ValidationError("shard manifest schema mismatch")
        listed.append(safe_relative(shard["path"], "shard path"))
    if len(set(listed)) != len(listed):
        raise ValidationError("duplicate shard paths")
    root = Path(directory)
    actual = sorted(path.name for path in root.glob("shard-*.jsonl") if path.is_file())
    if sorted(listed) != actual:
        raise ValidationError("shard set mismatch")
    total, total_bytes, ids = 0, 0, set()
    for shard, relative in zip(shards, listed):
        path = root / relative
        if path.stat().st_size != shard["bytes"] or file_sha256(path) != shard["sha256"]:
            raise ValidationError(f"shard identity mismatch: {relative}")
        count = 0
        with path.open(encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, 1):
                if not line.endswith("\n") or not line.strip():
                    raise ValidationError(f"invalid JSONL framing: {relative}:{line_number}")
                try:
                    row = json.loads(line, object_pairs_hook=strict_object, parse_constant=lambda token: (_ for _ in ()).throw(ValidationError(f"non-finite JSON number: {token}")))
                except json.JSONDecodeError as exc:
                    raise ValidationError(f"invalid JSON: {relative}:{line_number}") from exc
                row = _record(row)
                if row["record_id"] in ids:
                    raise ValidationError("duplicate record_id")
                ids.add(row["record_id"]); count += 1; total += 1
                yield row
        if count != shard["records"]:
            raise ValidationError("shard record count mismatch")
        total_bytes += shard["bytes"]
    if total != manifest["record_count"] or len(shards) != manifest["shard_count"] or total_bytes != manifest["total_bytes"] or ids != set(range(total)):
        raise ValidationError("dataset manifest totals do not reconcile")


def build_dataset_manifest(recipe: Mapping[str, Any], shard_manifest: Mapping[str, Any]) -> dict[str, Any]:
    payload = {"schema_version": DATASET_MANIFEST_SCHEMA, "recipe_sha256": stable_hash(recipe), "shard_manifest": dict(shard_manifest)}
    return {**payload, "manifest_sha256": stable_hash(payload)}


def validate_dataset_manifest(manifest: Mapping[str, Any], shard_dir: str | Path, recipe: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    required = {"schema_version", "recipe_sha256", "shard_manifest", "manifest_sha256"}
    if not isinstance(manifest, Mapping) or set(manifest) != required or manifest["schema_version"] != DATASET_MANIFEST_SCHEMA:
        raise ValidationError("dataset wrapper manifest schema mismatch")
    if manifest["manifest_sha256"] != stable_hash({key: value for key, value in manifest.items() if key != "manifest_sha256"}):
        raise ValidationError("dataset manifest self-hash mismatch")
    if recipe is not None and manifest["recipe_sha256"] != stable_hash(recipe):
        raise ValidationError("dataset recipe hash mismatch")
    return list(read_shards(shard_dir, manifest["shard_manifest"]))
