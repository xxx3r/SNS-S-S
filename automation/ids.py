"""Collision-safe identifiers for immutable SNS automation records."""

from __future__ import annotations

import re
import secrets
from datetime import datetime, timezone
from typing import Callable

_ID_RE = re.compile(r"^[A-Z]+-[0-9]{8}T[0-9]{12}Z-[a-z0-9-]+-[0-9a-f]{20}$")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _slug(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not normalized:
        raise ValueError("identifier namespace must contain a letter or digit")
    return normalized


def new_event_id(
    prefix: str,
    namespace: str,
    *,
    now: datetime | None = None,
    token_factory: Callable[[int], str] = secrets.token_hex,
) -> str:
    """Return a time-sortable identifier with 80 random bits.

    The timestamp provides operator legibility. The random suffix provides the
    collision boundary across loops, hosts, branches, and same-microsecond starts.
    Callers may inject a token factory for deterministic tests.
    """

    instant = now or _utc_now()
    if instant.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    instant = instant.astimezone(timezone.utc)
    stamp = instant.strftime("%Y%m%dT%H%M%S%fZ")
    prefix_slug = re.sub(r"[^A-Z]", "", prefix.upper())
    if not prefix_slug:
        raise ValueError("prefix must contain an ASCII letter")
    token = token_factory(10)
    if not re.fullmatch(r"[0-9a-f]{20}", token):
        raise ValueError("token_factory must return exactly 20 lowercase hex characters")
    return f"{prefix_slug}-{stamp}-{_slug(namespace)}-{token}"


def new_run_id(
    loop_id: str,
    *,
    now: datetime | None = None,
    token_factory: Callable[[int], str] = secrets.token_hex,
) -> str:
    return new_event_id("RUN", loop_id, now=now, token_factory=token_factory)


def validate_identifier(value: str, *, prefix: str | None = None) -> None:
    if not _ID_RE.fullmatch(value):
        raise ValueError(f"invalid immutable identifier: {value!r}")
    if prefix is not None and not value.startswith(prefix.upper() + "-"):
        raise ValueError(f"identifier {value!r} must start with {prefix.upper()}-")
