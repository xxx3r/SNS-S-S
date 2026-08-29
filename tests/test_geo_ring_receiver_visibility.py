"""Focused tests for the synthetic QST-SIM-0003 receiver window."""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from src.sim.config import SimulationConfig
from src.sim.simulation import Simulation
from src.world.geo_ring_world import GEORingWorld


OUTPUT_PATH = Path("outputs/qst_sim_0003/receiver_visibility_phase_sweep.json")


def test_default_preserves_always_visible_behavior() -> None:
    world = GEORingWorld()

    for phase in (0.0, math.pi / 2, math.pi, 3 * math.pi / 2):
        assert world.sample(theta=phase, t=0.0).line_of_sight_to_host is True


def test_configured_receiver_window_wraps_around_zero_phase() -> None:
    world = GEORingWorld(receiver_phase_center_rad=0.0, receiver_visibility_fraction=0.25)
    phases = (0.0, math.pi / 8, math.pi / 2, math.pi, 3 * math.pi / 2, 15 * math.pi / 8)

    assert [
        world.sample(theta=phase, t=0.0).line_of_sight_to_host for phase in phases
    ] == [True, True, False, False, False, True]


def test_simulation_configuration_forwards_receiver_window() -> None:
    config = SimulationConfig.from_dict(
        {
            "scenario": "geo_ring",
            "duration": 60.0,
            "dt": 60.0,
            "num_agents": 1,
            "environment": {
                "receiver_phase_center_rad": math.pi,
                "receiver_visibility_fraction": 0.25,
            },
        }
    )

    world = Simulation(config).world

    assert isinstance(world, GEORingWorld)
    assert world.sample(theta=math.pi, t=0.0).line_of_sight_to_host is True
    assert world.sample(theta=0.0, t=0.0).line_of_sight_to_host is False


def test_phase_sweep_output_is_reproducible() -> None:
    payload = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
    parameters = payload["synthetic_parameter_set"]
    world = GEORingWorld(
        receiver_phase_center_rad=parameters["receiver_phase_center_rad"],
        receiver_visibility_fraction=parameters["receiver_visibility_fraction"],
    )

    reproduced = [
        world.sample(theta=row["orbital_phase_rad"], t=0.0).line_of_sight_to_host
        for row in payload["samples"]
    ]

    assert reproduced == [row["line_of_sight_to_host"] for row in payload["samples"]]
    assert payload["summary"] == {
        "sample_count": 6,
        "visible_sample_count": 3,
        "default_always_visible_preserved": True,
    }


@pytest.mark.parametrize(
    ("parameter", "value"),
    (
        ("receiver_phase_center_rad", math.nan),
        ("receiver_phase_center_rad", math.inf),
        ("receiver_visibility_fraction", -0.01),
        ("receiver_visibility_fraction", 1.01),
        ("receiver_visibility_fraction", math.nan),
    ),
)
def test_receiver_window_rejects_invalid_parameters(parameter: str, value: float) -> None:
    with pytest.raises(ValueError):
        GEORingWorld(**{parameter: value})
