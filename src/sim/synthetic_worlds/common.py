"""Shared schemas, hashing, strict JSON, paths, and budgets."""
from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Any

RECORD_SCHEMA = "synthetic-worlds.record.v1"
RECIPE_SCHEMA = "synthetic-worlds.recipe.v1"
DATASET_MANIFEST_SCHEMA = "synthetic-worlds.dataset-manifest.v1"
EXPORT_MANIFEST_SCHEMA = "synthetic-worlds.export-manifest.v1"
RECEIPT_SCHEMA = "synthetic-worlds.qualification-receipt.v1"
TERMINAL_STATE = "PRIVATE_EXPORT_CANDIDATE_QUALIFIED"
HUMAN_RELEASE_STATE = "NOT_REVIEWED"
NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_.-]{0,63}$")


class ValidationError(ValueError):
    """Raised when a bounded contract fails closed."""


@dataclass(frozen=True)
class Budget:
    max_records: int = 100_000
    max_shards: int = 1_000
    max_parameter_combinations: int = 10_000
    max_points_per_record: int = 10_000
    max_total_points: int = 1_000_000
    max_bytes: int = 64 * 1024 * 1024

    def validate(self) -> None:
        for name, value in asdict(self).items():
            if not isinstance(value, int) or isinstance(value, bool) or value < 1:
                raise ValidationError(f"budget.{name} must be a positive integer")


def stable_json(value: Any) -> str:
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"value is not canonical JSON: {exc}") from exc


def stable_hash(value: Any) -> str:
    return hashlib.sha256(stable_json(value).encode()).hexdigest()


def file_sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValidationError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: str | Path) -> Any:
    try:
        return json.loads(
            Path(path).read_text(encoding="utf-8"),
            object_pairs_hook=strict_object,
            parse_constant=lambda token: (_ for _ in ()).throw(ValidationError(f"non-finite JSON number: {token}")),
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValidationError(f"invalid JSON file {path}: {exc}") from exc


def finite_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise ValidationError(f"{label} must be a finite number")
    return float(value)


def safe_relative(value: Any, label: str = "path") -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValidationError(f"{label} must be a non-empty POSIX relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise ValidationError(f"unsafe {label}: {value!r}")
    return path.as_posix()
