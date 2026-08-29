from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from src.sim.beam_link import (
    SYNTHETIC_PARAMETERS,
    build_synthetic_sweep,
    evaluate_beam_link,
    falsifier_fixture,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs" / "qst_meta_0001" / "beam_link_sweep.json"


def test_beam_link_sweep_reproduces_versioned_artifact():
    expected = json.loads(OUTPUT.read_text(encoding="utf-8"))
    actual = build_synthetic_sweep()

    assert actual == expected
    assert actual["summary"] == {
        "point_count": 12,
        "useful_point_count": 4,
        "limited_point_count": 8,
        "minimum_net_delivered_fraction": -0.034937533525,
        "maximum_net_delivered_fraction": 0.392,
        "relay_losses_erase_modeled_benefit_on_declared_grid": False,
        "outcome": "BOUNDED_BENEFIT_WITH_LOSS_LIMITS",
    }
    assert any(
        point["net_delivered_energy_Wh"] < 0.0
        for point in actual["sweep"]["points"]
    )


def test_declared_falsifier_is_preserved_when_losses_erase_benefit():
    result = falsifier_fixture()

    assert result["summary"]["useful_point_count"] == 0
    assert result["summary"]["relay_losses_erase_modeled_benefit_on_declared_grid"] is True
    assert result["summary"]["outcome"] == "MODELED_BENEFIT_ERASED_ON_DECLARED_GRID"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("aperture_efficiency", 1.01),
        ("pointing_sigma_deg", 0.0),
        ("control_base_Wh", -0.1),
        ("receiver_coupling", float("nan")),
    ],
)
def test_beam_link_rejects_invalid_parameters(field, value):
    with pytest.raises(ValueError):
        build_synthetic_sweep(replace(SYNTHETIC_PARAMETERS, **{field: value}))


def test_beam_link_rejects_invalid_sweep_coordinates():
    with pytest.raises(ValueError, match="steering_angle_deg"):
        evaluate_beam_link(
            SYNTHETIC_PARAMETERS,
            steering_angle_deg=91.0,
            pointing_error_deg=0.0,
        )
    with pytest.raises(ValueError, match="pointing_error_deg"):
        evaluate_beam_link(
            SYNTHETIC_PARAMETERS,
            steering_angle_deg=0.0,
            pointing_error_deg=-1.0,
        )


def test_perpendicular_steering_endpoint_is_zero_before_fractional_exponent():
    result = evaluate_beam_link(
        replace(SYNTHETIC_PARAMETERS, steering_exponent=0.01),
        steering_angle_deg=90.0,
        pointing_error_deg=0.0,
    )

    assert result["steering_penalty"] == 0.0
    assert result["gross_delivered_energy_Wh"] == 0.0
    assert result["net_delivered_energy_Wh"] < 0.0
    assert result["useful_on_declared_synthetic_boundary"] is False
