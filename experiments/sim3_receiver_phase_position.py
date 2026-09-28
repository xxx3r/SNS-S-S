"""Run the bounded two-case QST-SIM-0003 receiver phase-position diagnostic."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

from experiments.sim3_eclipse_beam_sweep import ACCEPTED_FIXTURE_BINDING_SHA256
from src.sim.config import SimulationConfig
from src.sim.simulation import Simulation


ECLIPSE_GRID = (0.05, 0.1)
BEAM_EFFICIENCY = 0.8
RECEIVER_VISIBILITY = 0.25
BASELINE_PHASE_CENTER_RAD = 0.0
DIAGNOSTIC_PHASE_CENTER_RAD = math.pi
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
    if grid["receiver_visibility_fraction"] != RECEIVER_VISIBILITY:
        raise ValueError("receiver visibility must remain fixed at 0.25")
    if grid["baseline_receiver_phase_center_rad"] != BASELINE_PHASE_CENTER_RAD:
        raise ValueError("baseline receiver phase center must remain zero")
    if grid["diagnostic_receiver_phase_center_rad"] != DIAGNOSTIC_PHASE_CENTER_RAD:
        raise ValueError("diagnostic receiver phase center must remain pi")
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
        "receiver_phase_center_rad": DIAGNOSTIC_PHASE_CENTER_RAD,
        "receiver_visibility_fraction": RECEIVER_VISIBILITY,
    }
    payload["agent_parameters"] = {
        **fixture["agent_parameters"],
        "beam_efficiency": BEAM_EFFICIENCY,
    }
    payload["policy"] = spec["arm"]["policy"]
    payload["agent_roles"] = list(spec["arm"]["agent_roles"])
    return SimulationConfig.from_dict(payload)


def run_diagnostic(spec: dict, baseline_bytes: bytes) -> dict:
    """Generate exactly two antipodal cases and load, rather than rerun, baselines."""

    _validate_spec(spec, baseline_bytes)
    baseline = json.loads(baseline_bytes)
    baseline_cases = {
        case["eclipse_fraction"]: case
        for case in baseline["cases"]
        if case["beam_efficiency"] == BEAM_EFFICIENCY
    }
    if set(baseline_cases) != set(ECLIPSE_GRID):
        raise ValueError("baseline artifact lacks the two accepted comparison cases")
    baseline_environment = baseline["fixture"]["environment"]
    if (
        baseline_environment["receiver_phase_center_rad"] != BASELINE_PHASE_CENTER_RAD
        or baseline_environment["receiver_visibility_fraction"] != RECEIVER_VISIBILITY
    ):
        raise ValueError("baseline artifact is not the accepted phase-center-zero evidence")

    cases = []
    for eclipse_fraction in ECLIPSE_GRID:
        metrics = Simulation(_config(spec, eclipse_fraction)).run().summary()
        diagnostic_metrics = {key: metrics[key] for key in REPORTED_METRICS}
        baseline_metrics = {
            key: baseline_cases[eclipse_fraction]["metrics"][key]
            for key in REPORTED_METRICS
        }
        cases.append(
            _round(
                {
                    "case_id": f"eclipse-{eclipse_fraction:.2f}_beam-0.80_visibility-0.25_phase-pi",
                    "eclipse_fraction": eclipse_fraction,
                    "beam_efficiency": BEAM_EFFICIENCY,
                    "receiver_visibility_fraction": RECEIVER_VISIBILITY,
                    "baseline_receiver_phase_center_rad": BASELINE_PHASE_CENTER_RAD,
                    "diagnostic_receiver_phase_center_rad": DIAGNOSTIC_PHASE_CENTER_RAD,
                    "baseline_metrics": baseline_metrics,
                    "diagnostic_metrics": diagnostic_metrics,
                    "metric_deltas": {
                        key: diagnostic_metrics[key] - baseline_metrics[key]
                        for key in REPORTED_METRICS
                    },
                }
            )
        )

    return {
        "schema": "sns.qst-sim-0003.receiver-phase-position.v1",
        "quest_id": spec["quest_id"],
        "synthetic": True,
        "route_receipt": spec["route_receipt"],
        "baseline_artifact": spec["baseline_artifact"],
        "baseline_artifact_sha256": spec["baseline_artifact_sha256"],
        "accepted_fixture_binding_sha256": ACCEPTED_FIXTURE_BINDING_SHA256,
        "case_count": len(cases),
        "new_world_count": len(cases),
        "baseline_worlds_rerun": 0,
        "grid": spec["grid"],
        "cases": cases,
        "observation": "ANTIPODAL_RECEIVER_PHASE_POSITION_DIAGNOSTIC_COMPLETE",
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
        repository_root / "configs" / "qst_sim_0003_receiver_phase_position.json",
        repository_root,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
