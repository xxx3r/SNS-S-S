"""Tests for coordinated policy and experiment helpers."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import pytest

pytest.importorskip("matplotlib")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from experiments.sweep_area_vs_count import run_area_vs_count  # noqa: E402
from experiments.sweep_eta_beam import run_eta_beam_sweep  # noqa: E402
from src.agents.policies import CoordinatedPolicy, PolicyContext  # noqa: E402
from src.agents.sns_agent import AgentMode, AgentParameters, SNSAgent  # noqa: E402
from src.host.host_collector import HostCollector  # noqa: E402
from src.world.asteroid_world import AsteroidWorld  # noqa: E402


def test_coordinated_policy_beams_when_deficit(tmp_path):
    params = AgentParameters(energy_max=5.0, initial_energy=4.5, high_threshold=3.0, beam_rate=1.0, beam_efficiency=0.8)
    agent = SNSAgent(agent_id=0, theta=0.0, params=params)
    world = AsteroidWorld(rotation_rate=0.0, solar_flux=1000.0)
    host = HostCollector(demand_function=lambda _: 10.0)
    policy = CoordinatedPolicy(low_threshold=params.low_threshold, high_threshold=params.high_threshold)
    context = PolicyContext(sunlit=True, host_deficit=5.0)

    agent.step(world, host, t=0.0, dt=60.0, policy=policy, context=context)

    assert agent.mode is AgentMode.COMM_BEAM
    assert host.energy > 0.0


def test_sweep_helpers_return_results(tmp_path):
    base_cfg = {
        "duration": 600.0,
        "dt": 60.0,
        "rotation_rate": 2 * math.pi / (2 * 3600.0),
        "solar_flux": 800.0,
        "num_agents": 3,
        "policy": "coordinated",
        "host_demand_rate": 0.2,
        "agent_parameters": {
            "pv_area": 0.3,
            "pv_efficiency": 0.25,
            "energy_max": 3.0,
            "initial_energy": 1.0,
            "power_idle": 0.1,
            "power_idle_low": 0.05,
            "low_threshold": 0.4,
            "high_threshold": 2.0,
            "beam_efficiency": 0.5,
            "beam_rate": 0.5,
            "power_comm": 0.1,
            "power_move": 0.2,
            "move_rate": 0.0005,
        },
        "total_pv_area": 1.2,
        "few_large_num_agents": 2,
        "many_small_num_agents": 4,
    }
    base_path = tmp_path / "base.json"
    base_path.write_text(json.dumps(base_cfg))

    eta_results = run_eta_beam_sweep(base_path, eta_values=[0.2, 0.6], output_dir=tmp_path / "eta_out")
    assert len(eta_results) == 2
    assert all("E_host_total" in row for row in eta_results)

    area_results = run_area_vs_count(base_path, output_dir=tmp_path / "area_out")
    assert {row["label"] for row in area_results} == {"few_large", "many_small"}
    assert (tmp_path / "eta_out" / "eta_beam_sweep.csv").exists()
    assert (tmp_path / "area_out" / "area_vs_count.csv").exists()
