"""Smoke tests for the SNS-S-S scaffold."""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.agents.sns_agent import AgentParameters  # noqa: E402
from src.sim.config import SimulationConfig  # noqa: E402
from src.sim.simulation import Simulation  # noqa: E402
from src.world.asteroid_world import AsteroidWorld  # noqa: E402


def test_asteroid_world_daylight_fraction():
    world = AsteroidWorld(rotation_rate=2 * math.pi / (4 * 3600))
    fraction = world.daylight_fraction()
    assert 0.45 < fraction < 0.55


def test_short_simulation_energy_bounds():
    params = AgentParameters(energy_max=2.0, initial_energy=0.5, pv_area=0.2, pv_efficiency=0.3)
    config = SimulationConfig(
        duration=600.0,
        dt=60.0,
        rotation_rate=2 * math.pi / (2 * 3600.0),
        solar_flux=800.0,
        num_agents=3,
        policy="baseline",
        agent_parameters=params,
    )
    sim = Simulation(config)
    metrics = sim.run()

    assert len(metrics.t_values) == int(config.duration // config.dt)
    for energy in [agent.energy for agent in sim.agents]:
        assert 0.0 <= energy <= params.energy_max + 1e-6
