"""Tests for the QST-STOR-0002 mission-shadow feasibility slice."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from experiments.mission_shadow_feasibility import build_rows, summarize
from src.sim.mission_shadow import (
    circular_orbit_shadow,
    hosted_sunward_standoff_shadow,
    surface_fixed_shadow,
)


def test_surface_shadow_is_half_rotation_and_pins_15_min_boundary():
    boundary = surface_fixed_shadow(
        name="boundary", rotation_period_h=0.5, acceptance_limit_h=0.25
    )
    slower = surface_fixed_shadow(
        name="slower", rotation_period_h=1.0, acceptance_limit_h=0.25
    )
    assert boundary.maximum_shadow_h == pytest.approx(0.25)
    assert boundary.status == "PASS"
    assert slower.maximum_shadow_h == pytest.approx(0.5)
    assert slower.status == "FAIL"


def test_passive_circular_orbit_fails_15_min_limit_on_declared_baseline():
    result = circular_orbit_shadow(
        name="baseline",
        asteroid_density_kg_m3=2000.0,
        orbital_radius_ratio=1.2,
        acceptance_limit_h=0.25,
    )
    assert result.maximum_shadow_h > 0.9
    assert result.maximum_shadow_h < 1.1
    assert result.status == "FAIL"


def test_hosted_sunward_standoff_is_conditional_not_passive():
    maintained = hosted_sunward_standoff_shadow(
        name="maintained",
        sunward_constraint_maintained=True,
        acceptance_limit_h=0.25,
    )
    lost = hosted_sunward_standoff_shadow(
        name="lost",
        sunward_constraint_maintained=False,
        acceptance_limit_h=0.25,
    )
    assert maintained.maximum_shadow_h == 0.0
    assert maintained.status == "PASS"
    assert maintained.guarantee_class == "conditional_active_geometry_guarantee"
    assert lost.status == "FAIL"


def test_declared_experiment_rejects_passive_orbit_and_preserves_conditions():
    config = json.loads(
        Path("configs/qst_stor_0002_mission_shadow.json").read_text(encoding="utf-8")
    )
    rows = build_rows(config)
    summary = summarize(rows, config)

    assert summary["case_count"] == 12
    assert summary["acceptance_limit_min"] == pytest.approx(15.0)
    assert summary["by_architecture"]["passive_circular_equatorial_orbit"]["pass_count"] == 0
    assert summary["by_architecture"]["surface_fixed_equator"]["pass_count"] == 2
    assert summary["by_architecture"]["hosted_active_sunward_standoff"]["pass_count"] == 1
    assert summary["conclusions"]["passive_generic_asteroid_orbit_status"] == "REJECTED_ON_DECLARED_GRID"
