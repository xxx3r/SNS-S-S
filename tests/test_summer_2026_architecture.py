"""Tests for the Summer 2026 mission-aware architecture."""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from src.agents.policies import CoordinatedPolicy, PolicyContext
from src.agents.sns_agent import AgentMode, AgentParameters, AgentRole, SNSAgent
from src.arci import ArciAssessment, ArciDimension
from src.host.host_collector import HostCollector
from src.research import parse_roundup, quests_from_roundup
from src.sim.config import SimulationConfig
from src.sim.simulation import Simulation
from src.world.asteroid_world import AsteroidWorld
from src.world.geo_ring_world import GEORingWorld


def test_q1_compatibility_energy_bounds():
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
    assert len(metrics.t_values) == 10
    assert all(0.0 <= agent.energy <= params.energy_max for agent in sim.agents)


def test_energy_flow_records_curtailment():
    params = AgentParameters(
        pv_area=1.0,
        pv_efficiency=1.0,
        energy_max=0.01,
        initial_energy=0.01,
        capacitor_max=0.0,
        max_battery_charge_power=0.001,
        power_idle=0.0,
        low_threshold=0.0,
        high_threshold=0.01,
    )
    agent = SNSAgent(0, 0.0, params, role=AgentRole.SCOUT)
    world = AsteroidWorld(rotation_rate=0.0, solar_flux=100.0)
    sample = world.sample(0.0, 0.0)
    context = PolicyContext(sunlit=True, host_deficit=0.0, sample=sample)
    result = agent.step(world, HostCollector(), 0.0, 60.0, CoordinatedPolicy(0.0, 1.0), context)
    assert result.harvested_Wh > 1.0
    assert result.curtailed_Wh > 0.0


def test_coordinated_relay_beams_when_host_has_deficit():
    params = AgentParameters(
        energy_max=5.0,
        initial_energy=4.5,
        high_threshold=3.0,
        low_threshold=0.5,
        beam_rate=1.0,
        beam_efficiency=0.8,
        role="relay",
    )
    agent = SNSAgent(0, 0.0, params)
    world = AsteroidWorld(rotation_rate=0.0, solar_flux=1000.0)
    host = HostCollector(demand_function=lambda _: 10.0)
    sample = world.sample(0.0, 0.0)
    context = PolicyContext(sunlit=True, host_deficit=5.0, sample=sample)
    result = agent.step(world, host, 0.0, 60.0, CoordinatedPolicy(0.5, 3.0), context)
    assert agent.mode is AgentMode.COMM_BEAM
    assert result.delivered_Wh > 0.0


def test_geo_ring_has_eclipse_and_sunlight():
    world = GEORingWorld(eclipse_fraction=0.1)
    assert not world.is_sunlit(math.pi, 0.0)
    assert world.is_sunlit(0.0, 0.0)


def test_arci_keeps_score_and_confidence_separate():
    dimensions = {
        name: ArciDimension(score=0.8, confidence=0.5, rationale="synthetic")
        for name in [
            "composition",
            "accessibility",
            "recoverability",
            "energy_environment",
            "surface_operations",
            "communications",
            "market_mission_value",
        ]
    }
    result = ArciAssessment(dimensions).evaluate()
    assert result.score == pytest.approx(0.8)
    assert result.confidence == pytest.approx(0.5)
    assert result.confidence_adjusted_score == pytest.approx(0.4)
    assert result.lower_bound < result.score < result.upper_bound


def test_roundup_to_quest_pipeline(tmp_path: Path):
    metadata = {
        "week": "2026-07-12",
        "research_paths": [3, 8],
        "weighted_belief_shifts": [
            {"subsystem": "STOR", "delta": 0.1, "confidence": 0.8, "rationale": "geometry audit"}
        ],
        "suggested_actions": [
            {
                "id": "QST-STOR-0002",
                "title": "Thermal derating",
                "objective": "Add temperature effects.",
                "artifact": "outputs/thermal.json",
                "success_metric": "One reproducible sweep."
            }
        ],
        "sns_awareness_update": {"summary": "Storage is architectural."}
    }
    path = tmp_path / "roundup.md"
    path.write_text(f"---\n{json.dumps(metadata)}\n---\n# Notes\nEvidence body.")
    roundup = parse_roundup(path)
    quests = quests_from_roundup(roundup)
    assert roundup.week == "2026-07-12"
    assert quests[0].quest_id == "QST-STOR-0002"
