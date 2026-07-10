"""Parse machine-usable weekly roundup front matter."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


@dataclass(frozen=True)
class Roundup:
    """Weekly research roundup normalized for quest generation."""

    week: str
    weighted_belief_shifts: tuple[dict[str, Any], ...]
    suggested_actions: tuple[dict[str, Any], ...]
    sns_awareness_update: Mapping[str, Any]
    research_paths: tuple[int, ...]
    body: str


def parse_roundup(path: str | Path) -> Roundup:
    """Parse Markdown with JSON-compatible YAML 1.2 front matter."""
    text = Path(path).read_text()
    if not text.startswith("---\n"):
        raise ValueError("roundup must begin with front matter delimiter '---'")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError("roundup front matter is missing its closing delimiter")
    metadata = json.loads(text[4:end])
    required = {"week", "weighted_belief_shifts", "suggested_actions", "sns_awareness_update"}
    missing = required - set(metadata)
    if missing:
        raise ValueError(f"roundup metadata missing: {', '.join(sorted(missing))}")
    return Roundup(
        week=str(metadata["week"]),
        weighted_belief_shifts=tuple(dict(item) for item in metadata["weighted_belief_shifts"]),
        suggested_actions=tuple(dict(item) for item in metadata["suggested_actions"]),
        sns_awareness_update=dict(metadata["sns_awareness_update"]),
        research_paths=tuple(int(value) for value in metadata.get("research_paths", [])),
        body=text[end + 5 :].strip(),
    )
