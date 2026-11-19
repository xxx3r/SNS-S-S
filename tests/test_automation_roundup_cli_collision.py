"""Regression: proposal staging must not overwrite historical artifacts.

This is a proposal-only, zero-world production CLI test; no quest enactment.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "roundup_to_quests.py"


def _roundup(path: Path, *, success_metric: str) -> None:
    metadata = {
        "week": "2026-11-19",
        "weighted_belief_shifts": [],
        "suggested_actions": [
            {
                "id": "QST-CALENDAR-9999",
                "title": "Collision fixture",
                "objective": "Test preservation of proposal artifacts.",
                "artifact": "outputs/calendar-collision-fixture.json",
                "success_metric": success_metric,
            }
        ],
        "sns_awareness_update": {},
        "research_paths": [8],
    }
    path.write_text(
        "---\n" + json.dumps(metadata) + "\n---\nTest-only roundup.\n",
        encoding="utf-8",
    )


def _run(roundup: Path, output: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(roundup), "--out", str(output)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def _snapshot(output: Path) -> dict[str, bytes]:
    return {path.name: path.read_bytes() for path in output.iterdir() if path.is_file()}


def test_identical_rerun_fails_closed_without_new_event_or_overwrite(tmp_path: Path) -> None:
    roundup = tmp_path / "roundup.md"
    output = tmp_path / "staged"
    _roundup(roundup, success_metric="First metric")

    first = _run(roundup, output)
    assert first.returncode == 0, first.stderr
    before = _snapshot(output)
    assert sum(name.endswith(".json") for name in before) == 1
    assert sum(name.endswith(".md") for name in before) == 1

    repeated = _run(roundup, output)
    assert repeated.returncode != 0
    assert "staging output already exists" in repeated.stderr
    assert _snapshot(output) == before

    independent = _run(roundup, tmp_path / "new-stage")
    assert independent.returncode == 0, independent.stderr


def test_changed_metric_cannot_replace_earlier_proposal(tmp_path: Path) -> None:
    roundup = tmp_path / "roundup.md"
    output = tmp_path / "staged"
    _roundup(roundup, success_metric="Original metric")
    first = _run(roundup, output)
    assert first.returncode == 0, first.stderr
    before = _snapshot(output)
    proposal = next(path for path in output.iterdir() if path.suffix == ".md")
    assert "Original metric" in proposal.read_text(encoding="utf-8")

    _roundup(roundup, success_metric="Different metric")
    second = _run(roundup, output)
    assert second.returncode != 0
    assert "staging output already exists" in second.stderr
    assert _snapshot(output) == before
    assert "Different metric" not in proposal.read_text(encoding="utf-8")
