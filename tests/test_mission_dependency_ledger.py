import json
from dataclasses import replace
from pathlib import Path

import pytest

from experiments.mission_dependency_ledger import build_artifact, build_cases
from src.sim.mission_dependency import compare_min_materials


LEDGER_PATH = Path("outputs/qst_stor_0002/mission_dependency_ledger.json")


def test_declared_dependency_ledger():
    surface, hosted = build_cases()
    artifact = build_artifact()
    committed = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))

    assert surface.geometry_status == "PASS_CONDITIONAL_TARGET"
    assert hosted.geometry_status == "PASS_CONDITIONAL_ACTIVE_HOST"
    assert surface.total_mass_kg < hosted.total_mass_kg
    assert surface.daily_energy_Wh < hosted.daily_energy_Wh
    assert artifact["comparison"]["winner_by_declared_total_mass"] == "fast_rotator_surface"
    assert committed["comparison"]["winner_by_declared_total_mass"] == artifact["comparison"]["winner_by_declared_total_mass"]
    assert committed["comparison"]["hosted_minus_surface_mass_kg"] == pytest.approx(artifact["comparison"]["hosted_minus_surface_mass_kg"])
    assert committed["comparison"]["hosted_minus_surface_daily_energy_Wh"] == pytest.approx(artifact["comparison"]["hosted_minus_surface_daily_energy_Wh"])
    assert committed["cases"][0]["total_mass_kg"] == pytest.approx(surface.total_mass_kg)
    assert committed["cases"][1]["total_mass_kg"] == pytest.approx(hosted.total_mass_kg)


def test_interpretation_tracks_configured_winner_and_geometry():
    surface, hosted = build_cases()

    lighter_hosted = replace(
        hosted,
        deployment_mass_kg=0.0,
        navigation_mass_kg=0.0,
        stationkeeping_mass_kg=0.0,
        resilience_mass_kg=0.0,
        host_service_mass_kg=0.0,
    )
    hosted_result = compare_min_materials(surface, lighter_hosted)
    assert hosted_result["winner_by_declared_total_mass"] == "active_sunward_hosted"
    assert "hosted route uses less" in hosted_result["interpretation"]

    failing_surface = replace(surface, target_rotation_period_h=1.0)
    failed_result = compare_min_materials(failing_surface, hosted)
    assert failed_result["winner_by_declared_total_mass"] == "NO_MATCHED_WINNER"
    assert "No matched winner" in failed_result["interpretation"]
