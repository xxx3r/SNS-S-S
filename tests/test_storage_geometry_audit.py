"""Tests for the QST-STOR-0001 storage geometry audit."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from experiments.storage_geometry_audit import load_config, run_audit, summarize  # noqa: E402
from src.sim.storage_geometry import shell_volume_l, sphere_volume_l  # noqa: E402


def test_sphere_geometry_matches_closed_form():
    assert math.isclose(sphere_volume_l(20.0), (4.0 / 3.0) * math.pi * 0.01**3 * 1000.0)


def test_shell_volume_is_outer_minus_inner():
    assert math.isclose(shell_volume_l(10.0, 1.0), sphere_volume_l(12.0) - sphere_volume_l(10.0))


def test_configured_sweep_has_1296_scenarios():
    rows = run_audit(load_config(ROOT / "configs" / "storage_geometry_audit.json"))
    assert len(rows) == 1296


def test_pass_fail_summary_is_consistent():
    summary = summarize(run_audit(load_config(ROOT / "configs" / "storage_geometry_audit.json")))
    assert summary["pass_count"] + summary["fail_count"] == summary["scenario_count"]
    assert set(summary["by_core_diameter"]) == {"10_mm", "20_mm", "30_mm"}


def test_checked_in_summary_matches_runner_schema():
    expected = summarize(run_audit(load_config(ROOT / "configs" / "storage_geometry_audit.json")))
    actual = json.loads((ROOT / "outputs" / "qst_stor_0001" / "summary.json").read_text())
    assert actual == expected
    assert "by_core_diameter" in actual
    assert "pass_rate_10_mm" not in actual
