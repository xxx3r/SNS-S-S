import json
from pathlib import Path

import pytest

from experiments.fast_rotator_constraint_cost import (
    build_artifact,
    load_json,
    required_screen_count,
)


CONFIG_PATH = Path("configs/qst_stor_0002_fast_rotator_constraint_cost.json")
OUTPUT_PATH = Path("outputs/qst_stor_0002/fast_rotator_constraint_cost.json")


def test_fast_rotator_constraint_cost_is_reproducible_and_bounded():
    config = load_json(CONFIG_PATH)
    geometry_config = load_json(Path(config["geometry_config"]))
    built = build_artifact(config, geometry_config)
    committed = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))

    assert committed == built
    assert committed["measurement_only"] is True
    assert committed["rotation_constraint"] == {
        "maximum_rotation_period_h": 0.5,
        "inherited_maximum_shadow_h": 0.25,
    }

    availability = committed["target_availability_screen"]["cases"]
    assert [case["screened_targets_required"] for case in availability] == [
        2995,
        299,
        59,
        29,
    ]
    assert [case["status"] for case in availability] == [
        "EXCEEDS_SCREENING_BUDGET",
        "EXCEEDS_SCREENING_BUDGET",
        "WITHIN_SCREENING_BUDGET",
        "WITHIN_SCREENING_BUDGET",
    ]

    thermal = {
        case["effective_emissivity"]: case
        for case in committed["thermal_screen"]["cases"]
    }
    assert thermal[0.1]["shadow_status"] == "PASS"
    assert thermal[0.1]["dual_pass_count"] == 0
    assert thermal[0.1]["illuminated_radiative_rejection_budget_at_reference_W"] == pytest.approx(0.011450590081828837)
    assert thermal[0.15]["shadow_status"] == "PASS"
    assert thermal[0.15]["dual_pass_count"] == 0
    assert thermal[0.15]["illuminated_radiative_rejection_budget_at_reference_W"] == pytest.approx(0.01717588512274325)
    assert thermal[0.2]["shadow_status"] == "FAIL"
    assert thermal[0.25]["shadow_status"] == "FAIL"
    assert committed["falsifier"] == {
        "triggered": True,
        "status": "FALSIFIED_ON_DECLARED_GRID",
        "rule": config["falsifier"],
    }
    assert "No surface or hosted architecture is selected or recommended." in committed[
        "nonclaims"
    ]


@pytest.mark.parametrize("probability", [0.0, -0.1, 1.1])
def test_fast_rotator_target_availability_rejects_invalid_probability(probability):
    with pytest.raises(
        ValueError, match=r"target availability probability must be in \(0, 1\]"
    ):
        required_screen_count(probability, 0.95)
