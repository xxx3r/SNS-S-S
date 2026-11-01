"""Frozen QST-SIM-0002 policy-by-rotation comparison.

The protocol can be validated without generating worlds. Execution is a separate
standing-authorized action after this protocol is accepted on main.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from src.agents.policies import PolicyContext
from src.agents.sns_agent import AgentRole
from src.sim.config import SimulationConfig
from src.sim.simulation import Simulation


SCHEMA = "sns.qst-sim-0002.rotation-policy-protocol.v1"
EXPECTED_POLICIES = ["baseline", "survey"]
EXPECTED_ROTATION_PERIODS_S = [7200.0, 43200.0]
EXPECTED_COMMON_FIXTURE = {
    "duration_s": 7200.0,
    "dt_s": 60.0,
    "solar_flux_W_m2": 1000.0,
    "num_agents": 6,
    "coverage_bin_count": 12,
    "stale_after_s": 600.0,
    "warmup_s": 600.0,
    "host_demand_rate_Wh_per_h": 0.0,
    "agent_roles": ["scout", "scout", "relay", "storage", "sensor", "relay"],
    "agent_parameters": {
        "pv_area": 0.4,
        "pv_efficiency": 0.25,
        "energy_max": 4.0,
        "initial_energy": 1.0,
        "power_idle": 0.15,
        "power_idle_low": 0.05,
        "power_scout": 0.15,
        "power_comm": 0.15,
        "power_move": 0.2,
        "low_threshold": 0.4,
        "high_threshold": 3.5,
        "beam_efficiency": 0.6,
        "beam_rate": 0.4,
        "move_rate": 0.0005,
    },
}


def load_protocol(path: str | Path) -> dict[str, Any]:
    """Load and fail closed on changes to the frozen four-case matrix."""
    protocol = json.loads(Path(path).read_text(encoding="utf-8"))
    if protocol.get("schema") != SCHEMA or protocol.get("quest_id") != "QST-SIM-0002":
        raise ValueError("unexpected SIM2 protocol identity")
    if protocol.get("status") != "prospectively_frozen":
        raise ValueError("SIM2 protocol must be prospectively frozen")
    comparison = protocol.get("comparison", {})
    if comparison.get("policies") != EXPECTED_POLICIES:
        raise ValueError("protocol must contain exactly baseline and survey policies")
    if comparison.get("rotation_periods_s") != EXPECTED_ROTATION_PERIODS_S:
        raise ValueError("protocol must contain exactly the declared rotation regimes")
    fixture = protocol.get("common_fixture", {})
    for name, expected in EXPECTED_COMMON_FIXTURE.items():
        if fixture.get(name) != expected:
            raise ValueError(f"unexpected scientifically active frozen fixture value: {name}")
    if set(fixture) != set(EXPECTED_COMMON_FIXTURE):
        raise ValueError("unexpected scientifically active frozen fixture fields")
    budgets = protocol.get("budgets", {})
    expected_records = (
        len(EXPECTED_POLICIES)
        * len(EXPECTED_ROTATION_PERIODS_S)
        * int(fixture["duration_s"] / fixture["dt_s"])
        * fixture["num_agents"]
    )
    if budgets.get("max_worlds") != 4 or budgets.get("max_agent_step_records") != expected_records:
        raise ValueError("protocol budgets do not match the fixed matrix")
    if protocol.get("primary_endpoint") != "time_average_fresh_coverage_fraction_after_warmup":
        raise ValueError("primary endpoint changed after freeze")
    return protocol


def _simulation_config(protocol: dict[str, Any], policy: str, rotation_period_s: float) -> SimulationConfig:
    fixture = protocol["common_fixture"]
    return SimulationConfig.from_dict(
        {
            "duration": fixture["duration_s"],
            "dt": fixture["dt_s"],
            "scenario": "asteroid",
            "mission": "survey_intelligence",
            "rotation_rate": 2.0 * math.pi / rotation_period_s,
            "solar_flux": fixture["solar_flux_W_m2"],
            "num_agents": fixture["num_agents"],
            "policy": policy,
            "host_demand_rate": fixture["host_demand_rate_Wh_per_h"],
            "coverage_bin_count": fixture["coverage_bin_count"],
            "agent_roles": fixture["agent_roles"],
            "agent_parameters": fixture["agent_parameters"],
        }
    )


def run_case(protocol: dict[str, Any], policy: str, rotation_period_s: float) -> dict[str, Any]:
    """Run one frozen case and return only preregistered measurements."""
    config = _simulation_config(protocol, policy, rotation_period_s)
    sim = Simulation(config)
    fixture = protocol["common_fixture"]
    observations: list[tuple[int, float]] = []
    fresh_trace: list[float] = []
    minimum_energy = min(agent.energy for agent in sim.agents)
    steps = int(config.duration // config.dt)

    for step_index in range(steps):
        t = step_index * config.dt
        target_agent_id, target_theta = sim._largest_gap_target()
        for agent in sim.agents:
            sample = sim.world.sample(agent.theta, t)
            context = PolicyContext(
                sunlit=sample.sunlit,
                host_deficit=sim.host.get_deficit(t + config.dt),
                target_theta=target_theta if agent.id == target_agent_id else None,
                sample=sample,
                coverage_fraction=len(sim.covered_regions) / sim.world.coverage_bin_count,
            )
            result = agent.step(sim.world, sim.host, t=t, dt=config.dt, policy=sim.policy, context=context)
            minimum_energy = min(minimum_energy, result.battery_Wh)
            if agent.role in {AgentRole.SCOUT, AgentRole.SENSOR}:
                observations.append((result.region_id, t))
                sim.covered_regions.add(result.region_id)
        stale = sim.world.stale_coverage_fraction(
            observations,
            t=t,
            stale_after_s=fixture["stale_after_s"],
        )
        fresh_trace.append(1.0 - stale)

    warmup_steps = int(fixture["warmup_s"] / config.dt)
    evaluation_trace = fresh_trace[warmup_steps:]
    return {
        "policy": policy,
        "rotation_period_s": rotation_period_s,
        "rotation_rate_rad_s": config.rotation_rate,
        "world_count": 1,
        "agent_step_records": steps * config.num_agents,
        "time_average_fresh_coverage_fraction_after_warmup": sum(evaluation_trace) / len(evaluation_trace),
        "final_fresh_coverage_fraction": fresh_trace[-1],
        "dead_agent_count": sum(agent.health.value == "failed" for agent in sim.agents),
        "final_mean_agent_energy_Wh": sum(agent.energy for agent in sim.agents) / len(sim.agents),
        "minimum_agent_energy_Wh": minimum_energy,
    }


def run_comparison(protocol_path: str | Path) -> dict[str, Any]:
    """Execute exactly the accepted four-case matrix."""
    protocol = load_protocol(protocol_path)
    cases = [
        run_case(protocol, policy, period)
        for period in EXPECTED_ROTATION_PERIODS_S
        for policy in EXPECTED_POLICIES
    ]
    deltas = []
    endpoint = protocol["primary_endpoint"]
    for period in EXPECTED_ROTATION_PERIODS_S:
        by_policy = {case["policy"]: case for case in cases if case["rotation_period_s"] == period}
        deltas.append(
            {
                "rotation_period_s": period,
                "survey_minus_baseline_primary_delta": by_policy["survey"][endpoint] - by_policy["baseline"][endpoint],
                "survey_minus_baseline_dead_agent_delta": by_policy["survey"]["dead_agent_count"] - by_policy["baseline"]["dead_agent_count"],
            }
        )
    return {
        "schema": "sns.qst-sim-0002.rotation-policy-result.v1",
        "quest_id": "QST-SIM-0002",
        "synthetic": True,
        "protocol": str(protocol_path),
        "world_count": sum(case["world_count"] for case in cases),
        "agent_step_records": sum(case["agent_step_records"] for case in cases),
        "primary_endpoint": endpoint,
        "cases": cases,
        "contrasts": deltas,
        "claim_boundary": "Fixed synthetic four-case comparison only; no irregular rotation, optimized policy, real asteroid, mission value, or hardware claim.",
    }


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    protocol_path = root / "configs/qst_sim_0002_rotation_policy_comparison.json"
    output_path = root / "outputs/qst_sim_0002/rotation_policy_comparison.json"
    result = run_comparison(protocol_path.relative_to(root))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output_path), "world_count": result["world_count"], "records": result["agent_step_records"]}))


if __name__ == "__main__":
    main()
