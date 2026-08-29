from __future__ import annotations

import json
from pathlib import Path

from automation.orchestration import compare_runtime_manifest, render_bootstrap_prompt, validate_runtime_manifest


def _manifest() -> dict:
    return json.loads(Path("automation/runtime_manifest.json").read_text(encoding="utf-8"))


def test_runtime_manifest_is_valid_and_binds_bootloader() -> None:
    manifest = _manifest()
    validate_runtime_manifest(manifest)
    prompt = render_bootstrap_prompt("daily-research-operator")
    assert "AGENTS.md" in prompt
    assert "resolve the one currently active repository contract" in prompt
    assert "1.1.0" not in prompt
    assert "Issue #38" not in prompt
    assert "August" not in prompt


def test_matching_observed_runtime_has_no_drift() -> None:
    manifest = _manifest()
    observed = []
    for row in manifest["loops"]:
        if not row["scheduler_managed"]:
            continue
        observed.append(
            {
                "title": row["automation_title"],
                "is_enabled": row["desired_enabled"],
                "schedule": row["schedule"],
                "timing_mode": row["timing_mode"],
                "prompt": render_bootstrap_prompt(row["loop_id"]),
            }
        )
    assert compare_runtime_manifest(manifest, observed) == []


def test_runtime_drift_reports_disabled_daily_and_stale_prompt() -> None:
    manifest = _manifest()
    observed = []
    for row in manifest["loops"]:
        if not row["scheduler_managed"]:
            continue
        observed.append(
            {
                "title": row["automation_title"],
                "is_enabled": False if row["loop_id"] == "daily-research-operator" else row["desired_enabled"],
                "schedule": row["schedule"],
                "timing_mode": row["timing_mode"],
                "prompt": "stale hard-coded prompt" if row["loop_id"] == "daily-research-operator" else render_bootstrap_prompt(row["loop_id"]),
            }
        )
    drift = compare_runtime_manifest(manifest, observed)
    daily_fields = {item["field"] for item in drift if item["loop_id"] == "daily-research-operator"}
    assert daily_fields == {"is_enabled", "prompt"}
