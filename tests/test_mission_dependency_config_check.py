from experiments.mission_dependency_config_check import build_check, load_config_cases


def test_versioned_allocation_config_matches_accepted_inputs():
    cases = load_config_cases()
    result = build_check()

    assert [case["name"] for case in cases] == [
        "measured_fast_rotator_surface",
        "active_sunward_hosted",
    ]
    assert result["matches_accepted_inputs"] is True
    assert result["mismatches"] == []
