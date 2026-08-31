"""Run one bounded synthetic QST-SIM-0003 role-mix comparison."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from src.sim.config import SimulationConfig
from src.sim.simulation import Simulation


METRIC_KEYS = (
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
)


def _round_floats(value: Any) -> Any:
    if isinstance(value, float):
        return round(value, 12)
    if isinstance(value, dict):
        return {key: _round_floats(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_round_floats(item) for item in value]
    return value


def _build_config(fixture: dict, arm: dict) -> SimulationConfig:
    payload = dict(fixture)
    payload["environment"] = dict(fixture["environment"])
    payload["agent_parameters"] = dict(fixture["agent_parameters"])
    payload["policy"] = arm["policy"]
    payload["agent_roles"] = list(arm["agent_roles"])
    return SimulationConfig.from_dict(payload)


def run_comparison(spec: dict) -> dict:
    """Execute the two declared arms without tuning or parameter sweeps."""

    arms = spec["arms"]
    if len(arms) != 2:
        raise ValueError("exactly two role-mix arms are required")
    if len({arm["arm_id"] for arm in arms}) != 2:
        raise ValueError("role-mix arm_id values must be unique")

    fixture = spec["fixture"]
    results = []
    for arm in arms:
        config = _build_config(fixture, arm)
        metrics = Simulation(config).run().summary()
        role_counts = Counter(arm["agent_roles"])
        result = {
            "arm_id": arm["arm_id"],
            "policy": arm["policy"],
            "agent_roles": list(arm["agent_roles"]),
            "storage_node_fraction": role_counts["storage"] / config.num_agents,
            "metrics": {key: metrics[key] for key in METRIC_KEYS},
        }
        results.append(_round_floats(result))

    baseline, coordinated = results
    delta_keys = (
        "E_host",
        "E_mean",
        "dead_agent_count",
        "delivered_total_Wh",
        "curtailed_total_Wh",
        "coverage_fraction",
    )
    deltas = {
        key: coordinated["metrics"][key] - baseline["metrics"][key]
        for key in delta_keys
    }
    if deltas["delivered_total_Wh"] > 1e-12:
        observation = "COORDINATED_HOST_DELIVERY_OBSERVED_ON_DECLARED_FIXTURE"
    elif abs(deltas["delivered_total_Wh"]) <= 1e-12:
        observation = "NEUTRAL_HOST_DELIVERY_ON_DECLARED_FIXTURE"
    else:
        observation = "COORDINATED_HOST_DELIVERY_LOWER_ON_DECLARED_FIXTURE"

    return _round_floats(
        {
            "schema": "sns.qst-sim-0003.role-mix-comparison.v1",
            "quest_id": spec["quest_id"],
            "synthetic": True,
            "fixture": fixture,
            "arms": results,
            "deltas_coordinated_minus_independent": deltas,
            "observation": observation,
            "interpretation_boundary": (
                "One synthetic fixture only; this is not architecture selection, "
                "storage-fraction optimization, relay-efficiency evidence, or a hardware-readiness claim."
            ),
        }
    )


def load_and_run(config_path: Path) -> dict:
    return run_comparison(json.loads(config_path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    payload = load_and_run(root / "configs" / "qst_sim_0003_role_mix.json")
    print(json.dumps(payload, indent=2, sort_keys=True))
