"""Run the fixed four-case QST-SIM-0003 eclipse/beam sweep once."""

from __future__ import annotations

import itertools
import json
from collections import Counter
from pathlib import Path
from typing import Any

from src.sim.config import SimulationConfig
from src.sim.simulation import Simulation


ECLIPSE_GRID = (0.05, 0.1)
BEAM_EFFICIENCY_GRID = (0.6, 0.8)
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
        return round(value, 9)
    if isinstance(value, dict):
        return {key: _round_floats(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_round_floats(item) for item in value]
    return value


def _validate_spec(spec: dict) -> None:
    grid = spec.get("grid", {})
    if tuple(grid.get("eclipse_fraction", ())) != ECLIPSE_GRID:
        raise ValueError("eclipse_fraction grid must remain the fixed two-value route")
    if tuple(grid.get("beam_efficiency", ())) != BEAM_EFFICIENCY_GRID:
        raise ValueError("beam_efficiency grid must remain the fixed two-value route")

    fixture = spec["fixture"]
    arm = spec["arm"]
    roles = list(arm["agent_roles"])
    role_counts = Counter(roles)
    if (
        arm.get("arm_id") != "fixed_coordinated_storage_mix"
        or arm.get("policy") != "coordinated"
        or len(roles) != fixture["num_agents"]
        or role_counts["storage"] / fixture["num_agents"] != 0.2
    ):
        raise ValueError("the accepted coordinated 20% storage-node role mix is required")


def _case_config(spec: dict, eclipse_fraction: float, beam_efficiency: float) -> SimulationConfig:
    fixture = spec["fixture"]
    payload = dict(fixture)
    payload["environment"] = {
        **fixture["environment"],
        "eclipse_fraction": eclipse_fraction,
    }
    payload["agent_parameters"] = {
        **fixture["agent_parameters"],
        "beam_efficiency": beam_efficiency,
    }
    payload["policy"] = spec["arm"]["policy"]
    payload["agent_roles"] = list(spec["arm"]["agent_roles"])
    return SimulationConfig.from_dict(payload)


def run_sweep(spec: dict) -> dict:
    """Execute exactly the frozen Cartesian grid without ranking or tuning."""

    _validate_spec(spec)
    cases = []
    for eclipse_fraction, beam_efficiency in itertools.product(
        ECLIPSE_GRID, BEAM_EFFICIENCY_GRID
    ):
        config = _case_config(spec, eclipse_fraction, beam_efficiency)
        metrics = Simulation(config).run().summary()
        cases.append(
            _round_floats(
                {
                    "case_id": f"eclipse-{eclipse_fraction:.2f}_beam-{beam_efficiency:.2f}",
                    "eclipse_fraction": eclipse_fraction,
                    "beam_efficiency": beam_efficiency,
                    "storage_node_fraction": 0.2,
                    "metrics": {key: metrics[key] for key in METRIC_KEYS},
                }
            )
        )

    by_coordinate = {
        (case["eclipse_fraction"], case["beam_efficiency"]): case["metrics"]
        for case in cases
    }

    def metric_deltas(later: dict, earlier: dict) -> dict:
        return _round_floats(
            {
                "delivered_total_Wh": later["delivered_total_Wh"]
                - earlier["delivered_total_Wh"],
                "curtailed_total_Wh": later["curtailed_total_Wh"]
                - earlier["curtailed_total_Wh"],
                "dead_agent_count": later["dead_agent_count"]
                - earlier["dead_agent_count"],
                "coverage_fraction": later["coverage_fraction"]
                - earlier["coverage_fraction"],
            }
        )

    observed_differences = {
        "beam_efficiency_0.80_minus_0.60": [
            {
                "eclipse_fraction": eclipse_fraction,
                "metric_deltas": metric_deltas(
                    by_coordinate[(eclipse_fraction, 0.8)],
                    by_coordinate[(eclipse_fraction, 0.6)],
                ),
            }
            for eclipse_fraction in ECLIPSE_GRID
        ],
        "eclipse_fraction_0.10_minus_0.05": [
            {
                "beam_efficiency": beam_efficiency,
                "metric_deltas": metric_deltas(
                    by_coordinate[(0.1, beam_efficiency)],
                    by_coordinate[(0.05, beam_efficiency)],
                ),
            }
            for beam_efficiency in BEAM_EFFICIENCY_GRID
        ],
    }

    return {
        "schema": "sns.qst-sim-0003.eclipse-beam-sweep.v1",
        "quest_id": spec["quest_id"],
        "synthetic": True,
        "route_receipt": spec["route_receipt"],
        "grid": spec["grid"],
        "case_count": len(cases),
        "fixture": spec["fixture"],
        "arm": spec["arm"],
        "cases": cases,
        "observed_differences": observed_differences,
        "observation": "FIXED_FOUR_CASE_SYNTHETIC_SWEEP_COMPLETE",
        "interpretation_boundary": spec["claim_boundary"],
    }


def load_and_run(config_path: Path) -> dict:
    return run_sweep(json.loads(config_path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    payload = load_and_run(root / "configs" / "qst_sim_0003_eclipse_beam_sweep.json")
    print(json.dumps(payload, indent=2, sort_keys=True))
