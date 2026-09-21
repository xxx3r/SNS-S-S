"""Run the bounded two-case QST-SIM-0003 receiver-availability diagnostic."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from experiments.sim3_eclipse_beam_sweep import ACCEPTED_FIXTURE_BINDING_SHA256
from src.sim.config import SimulationConfig
from src.sim.simulation import Simulation


ECLIPSE_GRID = (0.05, 0.1)
BEAM_EFFICIENCY = 0.8
BASELINE_VISIBILITY = 0.25
DIAGNOSTIC_VISIBILITY = 1.0
REPORTED_METRICS = (
    "delivered_total_Wh",
    "curtailed_total_Wh",
    "dead_agent_count",
    "coverage_fraction",
)


def _round(value: Any) -> Any:
    if isinstance(value, float):
        return round(value, 9)
    if isinstance(value, dict):
        return {key: _round(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_round(item) for item in value]
    return value


def _validate_spec(spec: dict, baseline_bytes: bytes) -> None:
    grid = spec["grid"]
    if tuple(grid["eclipse_fraction"]) != ECLIPSE_GRID:
        raise ValueError("eclipse_fraction must remain the accepted two-value grid")
    if grid["beam_efficiency"] != BEAM_EFFICIENCY:
        raise ValueError("beam_efficiency must remain fixed at 0.80")
    if grid["baseline_receiver_visibility_fraction"] != BASELINE_VISIBILITY:
        raise ValueError("baseline receiver visibility must remain 0.25")
    if grid["diagnostic_receiver_visibility_fraction"] != DIAGNOSTIC_VISIBILITY:
        raise ValueError("diagnostic receiver visibility must remain 1.0")
    if hashlib.sha256(baseline_bytes).hexdigest() != spec["baseline_artifact_sha256"]:
        raise ValueError("immutable baseline artifact hash mismatch")

    binding = json.dumps(
        {"fixture": spec["fixture"], "arm": spec["arm"]},
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    if hashlib.sha256(binding).hexdigest() != ACCEPTED_FIXTURE_BINDING_SHA256:
        raise ValueError("fixture and role mix must match the accepted binding")

def _config(spec: dict, eclipse_fraction: float) -> SimulationConfig:
    fixture = spec["fixture"]
    payload = dict(fixture)
    payload["environment"] = {
        **fixture["environment"],
        "eclipse_fraction": eclipse_fraction,
        "receiver_visibility_fraction": DIAGNOSTIC_VISIBILITY,
    }
    payload["agent_parameters"] = {
        **fixture["agent_parameters"],
        "beam_efficiency": BEAM_EFFICIENCY,
    }
    payload["policy"] = spec["arm"]["policy"]
    payload["agent_roles"] = list(spec["arm"]["agent_roles"])
    return SimulationConfig.from_dict(payload)


def run_diagnostic(spec: dict, baseline_bytes: bytes) -> dict:
    """Generate exactly two new cases and compare them to loaded baseline evidence."""

    _validate_spec(spec, baseline_bytes)
    baseline = json.loads(baseline_bytes)
    baseline_cases = {
        case["eclipse_fraction"]: case
        for case in baseline["cases"]
        if case["beam_efficiency"] == BEAM_EFFICIENCY
    }
    if set(baseline_cases) != set(ECLIPSE_GRID):
        raise ValueError("baseline artifact lacks the two accepted comparison cases")
    if any(
        baseline["fixture"]["environment"]["receiver_visibility_fraction"]
        != BASELINE_VISIBILITY
        for _case in baseline_cases.values()
    ):
        raise ValueError("baseline artifact is not the accepted 0.25-visibility evidence")

    cases = []
    for eclipse_fraction in ECLIPSE_GRID:
        metrics = Simulation(_config(spec, eclipse_fraction)).run().summary()
        new_metrics = {key: metrics[key] for key in REPORTED_METRICS}
        old_metrics = {
            key: baseline_cases[eclipse_fraction]["metrics"][key]
            for key in REPORTED_METRICS
        }
        old_delivery = old_metrics["delivered_total_Wh"]
        relative_increase = (
            (new_metrics["delivered_total_Wh"] - old_delivery) / old_delivery
        )
        cases.append(
            _round(
                {
                    "case_id": f"eclipse-{eclipse_fraction:.2f}_beam-0.80_visibility-1.00",
                    "eclipse_fraction": eclipse_fraction,
                    "beam_efficiency": BEAM_EFFICIENCY,
                    "baseline_receiver_visibility_fraction": BASELINE_VISIBILITY,
                    "diagnostic_receiver_visibility_fraction": DIAGNOSTIC_VISIBILITY,
                    "baseline_metrics": old_metrics,
                    "diagnostic_metrics": new_metrics,
                    "metric_deltas": {
                        key: new_metrics[key] - old_metrics[key]
                        for key in REPORTED_METRICS
                    },
                    "delivery_relative_increase": relative_increase,
                }
            )
        )

    return {
        "schema": "sns.qst-sim-0003.receiver-availability.v1",
        "quest_id": spec["quest_id"],
        "synthetic": True,
        "weekly_disposition": spec["weekly_disposition"],
        "baseline_artifact": spec["baseline_artifact"],
        "baseline_artifact_sha256": spec["baseline_artifact_sha256"],
        "accepted_fixture_binding_sha256": ACCEPTED_FIXTURE_BINDING_SHA256,
        "case_count": len(cases),
        "new_world_count": len(cases),
        "baseline_worlds_rerun": 0,
        "grid": spec["grid"],
        "cases": cases,
        "observation": "RECEIVER_AVAILABILITY_INCREASED_SYNTHETIC_DELIVERY",
        "materiality_classification": "NOT_DEFINED_BY_ACCEPTED_ROUTE",
        "interpretation_boundary": spec["claim_boundary"],
    }


def load_and_run(config_path: Path, root: Path | None = None) -> dict:
    root = root or config_path.resolve().parents[1]
    spec = json.loads(config_path.read_text(encoding="utf-8"))
    baseline_bytes = (root / spec["baseline_artifact"]).read_bytes()
    return run_diagnostic(spec, baseline_bytes)


if __name__ == "__main__":
    repository_root = Path(__file__).resolve().parents[1]
    result = load_and_run(
        repository_root / "configs" / "qst_sim_0003_receiver_availability.json",
        repository_root,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
