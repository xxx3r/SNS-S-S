from experiments.mission_dependency_ledger import build_artifact, build_cases


def test_declared_dependency_ledger():
    surface, hosted = build_cases()
    artifact = build_artifact()
    assert surface.geometry_status == "PASS_CONDITIONAL_TARGET"
    assert hosted.geometry_status == "PASS_CONDITIONAL_ACTIVE_HOST"
    assert surface.total_mass_kg < hosted.total_mass_kg
    assert surface.daily_energy_Wh < hosted.daily_energy_Wh
    assert artifact["comparison"]["winner_by_declared_total_mass"] == "fast_rotator_surface"
    assert len(artifact["limitations"]) == 3
