"""Run the bounded two-case QST-SIM-0003 host-demand sensitivity diagnostic."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from experiments.sim3_eclipse_beam_sweep import ACCEPTED_FIXTURE_BINDING_SHA256
from src.sim.config import SimulationConfig
from src.sim.simulation import Simulation


BASELINE_DEMAND_RATE = 0.2
DIAGNOSTIC_DEMAND_RATES = (0.1, 0.4)
ECLIPSE_FRACTION = 0.05
BEAM_EFFICIENCY = 0.8
RECEIVER_VISIBILITY = 0.25
RECEIVER_PHASE_CENTER = 0.0
ABSOLUTE_TOLERANCE_WH = 1e-9
REPORTED_METRICS = (
    "delivered_total_Wh",
    "host_demand_total_Wh",
    "unmet_host_demand_Wh",
    "host_service_fraction",
    "curtailed_total_Wh",
    "dead_agent_count",
    "coverage_fraction",
    "receiver_visible_opportunities_by_role",
)


def _rounded(value: Any) -> Any:
    if isinstance(value, float):
        return round(value, 9)
    if isinstance(value, dict):
        return {key: _rounded(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_rounded(item) for item in value]
    return value


def _validate_spec(spec: dict, baseline_bytes: bytes) -> None:
    grid = spec["grid"]
    if grid["baseline_host_demand_rate_Wh_per_h"] != BASELINE_DEMAND_RATE:
        raise ValueError("baseline host demand must remain the accepted 0.2 Wh/h")
    if tuple(grid["diagnostic_host_demand_rate_Wh_per_h"]) != DIAGNOSTIC_DEMAND_RATES:
        raise ValueError("diagnostic demand grid must remain exactly 0.1 and 0.4 Wh/h")
    if (
        grid["eclipse_fraction"] != ECLIPSE_FRACTION
        or grid["beam_efficiency"] != BEAM_EFFICIENCY
        or grid["receiver_visibility_fraction"] != RECEIVER_VISIBILITY
        or grid["receiver_phase_center_rad"] != RECEIVER_PHASE_CENTER
    ):
        raise ValueError("all non-demand coordinates must remain fixed")
    if hashlib.sha256(baseline_bytes).hexdigest() != spec["baseline_artifact_sha256"]:
        raise ValueError("immutable baseline artifact hash mismatch")

    binding = json.dumps(
        {"fixture": spec["fixture"], "arm": spec["arm"]},
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    if hashlib.sha256(binding).hexdigest() != ACCEPTED_FIXTURE_BINDING_SHA256:
        raise ValueError("fixture and role mix must match the accepted binding")


def _config(spec: dict, demand_rate: float) -> SimulationConfig:
    fixture = spec["fixture"]
    payload = dict(fixture)
    payload["host_demand_rate"] = demand_rate
    payload["environment"] = {
        **fixture["environment"],
        "eclipse_fraction": ECLIPSE_FRACTION,
        "receiver_visibility_fraction": RECEIVER_VISIBILITY,
        "receiver_phase_center_rad": RECEIVER_PHASE_CENTER,
    }
    payload["agent_parameters"] = {
        **fixture["agent_parameters"],
        "beam_efficiency": BEAM_EFFICIENCY,
    }
    payload["policy"] = spec["arm"]["policy"]
    payload["agent_roles"] = list(spec["arm"]["agent_roles"])
    return SimulationConfig.from_dict(payload)


def run_diagnostic(spec: dict, baseline_bytes: bytes) -> dict:
    """Generate two demand cases and compare them with loaded baseline evidence."""

    _validate_spec(spec, baseline_bytes)
    baseline = json.loads(baseline_bytes)
    matches = [
        case
        for case in baseline["cases"]
        if case["eclipse_fraction"] == ECLIPSE_FRACTION
        and case["beam_efficiency"] == BEAM_EFFICIENCY
    ]
    if len(matches) != 1:
        raise ValueError("baseline artifact must contain exactly one accepted comparison case")
    baseline_case = matches[0]
    baseline_delivered = float(baseline_case["metrics"]["delivered_total_Wh"])
    duration_h = float(spec["fixture"]["duration"]) / 3600.0
    baseline_demand = BASELINE_DEMAND_RATE * duration_h
    baseline_summary = _rounded(
        {
            "case_id": "accepted-eclipse-0.05_beam-0.80_demand-0.20",
            "host_demand_rate_Wh_per_h": BASELINE_DEMAND_RATE,
            "delivered_total_Wh": baseline_delivered,
            "host_demand_total_Wh": baseline_demand,
            "unmet_host_demand_Wh": baseline_demand - baseline_delivered,
            "host_service_fraction": baseline_delivered / baseline_demand,
            "source": spec["baseline_artifact"],
        }
    )

    cases = []
    for demand_rate in DIAGNOSTIC_DEMAND_RATES:
        metrics = Simulation(_config(spec, demand_rate)).run().summary()
        case_metrics = {key: metrics[key] for key in REPORTED_METRICS}
        delivered_delta = float(metrics["delivered_total_Wh"]) - baseline_delivered
        cases.append(
            _rounded(
                {
                    "case_id": f"eclipse-0.05_beam-0.80_demand-{demand_rate:.2f}",
                    "host_demand_rate_Wh_per_h": demand_rate,
                    "metrics": case_metrics,
                    "delivered_delta_from_accepted_baseline_Wh": delivered_delta,
                    "delivery_equal_to_baseline_within_tolerance": (
                        abs(delivered_delta) <= ABSOLUTE_TOLERANCE_WH
                    ),
                }
            )
        )

    invariant = all(case["delivery_equal_to_baseline_within_tolerance"] for case in cases)
    observation = (
        "DELIVERY_DEMAND_INSENSITIVE_ON_DECLARED_FIXTURE"
        if invariant
        else "DELIVERY_DEMAND_SENSITIVE_ON_DECLARED_FIXTURE"
    )
    return {
        "schema": "sns.qst-sim-0003.host-demand-sensitivity.v1",
        "quest_id": spec["quest_id"],
        "synthetic": True,
        "baseline_artifact": spec["baseline_artifact"],
        "baseline_artifact_sha256": spec["baseline_artifact_sha256"],
        "accepted_fixture_binding_sha256": ACCEPTED_FIXTURE_BINDING_SHA256,
        "baseline_worlds_rerun": 0,
        "new_world_count": len(cases),
        "absolute_delivery_tolerance_Wh": ABSOLUTE_TOLERANCE_WH,
        "fixed_coordinates": {
            "eclipse_fraction": ECLIPSE_FRACTION,
            "beam_efficiency": BEAM_EFFICIENCY,
            "receiver_visibility_fraction": RECEIVER_VISIBILITY,
            "receiver_phase_center_rad": RECEIVER_PHASE_CENTER,
        },
        "accepted_baseline": baseline_summary,
        "cases": cases,
        "observation": observation,
        "interpretation": (
            "Across the declared 0.1-0.4 Wh/h demand bracket, changing host demand changes "
            "unmet demand and service fraction but not delivered energy on this fixed synthetic "
            "fixture. Host demand is therefore not the active delivery cap inside this bracket; "
            "receiver opportunity, policy, beam rate, or another fixed power-chain element remains "
            "the model-internal bottleneck candidate."
        ),
        "claim_boundary": spec["claim_boundary"],
        "next_measurement": (
            "Instrument role-conditioned delivered energy and delivery opportunity state before "
            "another world so the next comparison can distinguish unused receiver opportunity from "
            "policy or beam-rate limitation."
        ),
    }


def load_and_run(config_path: Path, root: Path | None = None) -> dict:
    root = root or config_path.resolve().parents[1]
    spec = json.loads(config_path.read_text(encoding="utf-8"))
    baseline_bytes = (root / spec["baseline_artifact"]).read_bytes()
    return run_diagnostic(spec, baseline_bytes)


if __name__ == "__main__":
    repository_root = Path(__file__).resolve().parents[1]
    result = load_and_run(
        repository_root / "configs" / "qst_sim_0003_host_demand_sensitivity.json",
        repository_root,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
