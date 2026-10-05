"""Accounting identities for first-class QST-SIM-0003 telemetry."""

from __future__ import annotations

import pytest

from src.agents.sns_agent import AgentRole
from src.sim.config import SimulationConfig
from src.sim.simulation import Simulation


def _config() -> SimulationConfig:
    return SimulationConfig.from_dict(
        {
            "duration": 900.0,
            "dt": 300.0,
            "scenario": "geo_ring",
            "mission": "geo_ring_power_chain",
            "solar_flux": 1360.0,
            "num_agents": 5,
            "host_demand_rate": 0.2,
            "coverage_bin_count": 36,
            "environment": {
                "orbital_period_s": 86164.0,
                "eclipse_fraction": 0.1,
                "receiver_phase_center_rad": 0.0,
                "receiver_visibility_fraction": 0.25,
            },
            "policy": "coordinated",
            "agent_roles": ["scout", "scout", "sensor", "relay", "storage"],
            "agent_parameters": {
                "pv_area": 0.5,
                "pv_efficiency": 0.25,
                "energy_max": 0.1,
                "initial_energy": 0.05,
                "capacitor_max": 0.003,
                "initial_capacitor": 0.0,
                "max_battery_charge_power": 0.1,
                "max_capacitor_charge_power": 1.0,
                "charge_efficiency": 0.9,
                "discharge_efficiency": 0.9,
                "power_idle": 0.002,
                "power_idle_low": 0.0001,
                "power_scout": 0.005,
                "power_comm": 0.05,
                "power_move": 0.02,
                "low_threshold": 0.02,
                "high_threshold": 0.08,
                "beam_efficiency": 0.8,
                "beam_rate": 0.05,
                "move_rate": 0.0005,
                "orientation_factor": 1.0,
                "thermal_time_constant_s": 1800.0,
                "initial_temperature_K": 290.0,
                "min_operating_temperature_K": 240.0,
                "max_operating_temperature_K": 350.0,
            },
        }
    )


def test_host_accounting_identities_hold_at_every_step() -> None:
    metrics = Simulation(_config()).run()

    assert metrics.host_demand_total_Wh == pytest.approx([1 / 60, 1 / 30, 1 / 20])
    for demand, delivered, unmet, fraction in zip(
        metrics.host_demand_total_Wh,
        metrics.delivered_total_Wh,
        metrics.unmet_host_demand_Wh,
        metrics.host_service_fraction,
        strict=True,
    ):
        assert demand == pytest.approx(delivered + unmet)
        assert fraction == pytest.approx(delivered / demand)
        assert 0.0 <= fraction <= 1.0


def test_role_conditioned_receiver_opportunities_are_cumulative_and_partitioned() -> None:
    simulation = Simulation(_config())
    metrics = simulation.run()
    final = metrics.summary()["receiver_visible_opportunities_by_role"]

    expected = {
        role.value: {"sunlit": 0, "eclipse": 0}
        for role in (AgentRole.RELAY, AgentRole.STORAGE)
    }
    steps = int(simulation.config.duration // simulation.config.dt)
    for step_index in range(steps):
        t = step_index * simulation.config.dt
        for agent in simulation.agents:
            if agent.role not in {AgentRole.RELAY, AgentRole.STORAGE}:
                continue
            sample = simulation.world.sample(agent.theta, t)
            if sample.line_of_sight_to_host:
                expected[agent.role.value]["sunlit" if sample.sunlit else "eclipse"] += 1

    assert final == expected
    for role, counts in final.items():
        assert counts["sunlit"] + counts["eclipse"] == (
            expected[role]["sunlit"] + expected[role]["eclipse"]
        )
        cumulative_totals = [sum(step[role].values()) for step in metrics.receiver_visible_opportunities_by_role]
        assert cumulative_totals == sorted(cumulative_totals)


def test_legacy_summary_keys_and_empty_semantics_are_preserved() -> None:
    summary = Simulation(_config()).run().summary()
    legacy = {
        "E_host",
        "E_mean",
        "E_min",
        "E_max",
        "dead_agent_count",
        "harvested_total_Wh",
        "delivered_total_Wh",
        "curtailed_total_Wh",
        "load_total_Wh",
        "coverage_fraction",
        "mean_temperature_K",
        "mode_counts",
        "role_counts",
        "health_counts",
    }
    assert legacy <= summary.keys()
