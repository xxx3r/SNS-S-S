"""Tests for QST-STOR-0001 storage geometry calculations and artifacts."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from experiments.storage_geometry_audit import run_storage_geometry_audit  # noqa: E402
from src.sim.storage_geometry import (  # noqa: E402
    DEFAULT_SWEEP,
    StorageAuditAssumptions,
    StorageAuditPoint,
    evaluate_storage_point,
    iter_storage_sweep,
    sphere_volume_liters,
)


def test_ten_millimetre_sphere_volume_matches_geometry():
    assert sphere_volume_liters(10.0) == pytest.approx(5.235987756e-4)


def test_reference_point_energy_and_mass_are_dimensionally_consistent():
    point = StorageAuditPoint(
        core_diameter_mm=10,
        battery_volume_fraction=0.30,
        battery_energy_density_Wh_L=1000,
        sleep_power_uW=100,
        active_power_mW=10,
        shadow_duration_h=12,
    )
    row = evaluate_storage_point(point, StorageAuditAssumptions())

    assert row["gross_battery_Wh"] == pytest.approx(0.1570796327)
    assert row["usable_battery_Wh"] == pytest.approx(0.1256637061)
    assert row["battery_mass_estimate_g"] == pytest.approx(0.3141592654)
    assert row["status"] == "PASS"
    assert row["charge_limited_fill_time_s"] > row["pv_fill_time_s"]


def test_full_default_sweep_has_expected_cartesian_size():
    rows = list(iter_storage_sweep(DEFAULT_SWEEP))
    assert len(rows) == 3 * 3 * 4 * 3 * 3 * 4
    assert {row["status"] for row in rows} == {"PASS", "FAIL"}


def test_survival_duration_and_pass_status_use_same_reserve_policy():
    assumptions = StorageAuditAssumptions()
    point = StorageAuditPoint(10, 0.15, 220, 1000, 100, 72)
    row = evaluate_storage_point(point, assumptions)

    assert row["status"] == ("PASS" if row["survival_duration_h"] >= 72 else "FAIL")
    assert math.isclose(
        row["storage_margin_Wh"],
        row["usable_battery_Wh"] - row["required_storage_Wh"],
    )


def test_audit_runner_writes_reproducible_artifacts(tmp_path):
    config_path = tmp_path / "audit.json"
    config_path.write_text(
        json.dumps(
            {
                "sweep": {
                    "core_diameter_mm": [10],
                    "battery_volume_fraction": [0.3],
                    "battery_energy_density_Wh_L": [450],
                    "sleep_power_uW": [100],
                    "active_power_mW": [10],
                    "shadow_duration_h": [2, 12],
                },
                "assumptions": {"active_duty_cycle": 0.01},
            }
        )
    )

    rows, summary = run_storage_geometry_audit(config_path, tmp_path / "out")

    assert len(rows) == 2
    assert summary["scenario_count"] == 2
    assert (tmp_path / "out" / "storage_geometry_sweep.csv").exists()
    assert (tmp_path / "out" / "summary.json").exists()
    assert (tmp_path / "out" / "active_duty_cycle_sensitivity.csv").exists()
    assert (tmp_path / "out" / "README.md").exists()


def test_checked_in_summary_matches_current_runner(tmp_path):
    _, expected = run_storage_geometry_audit(
        ROOT / "configs" / "storage_geometry_audit.json",
        tmp_path / "regenerated",
    )
    actual = json.loads((ROOT / "outputs" / "qst_stor_0001" / "summary.json").read_text())
    assert actual == expected
    assert "by_core_diameter" in actual
