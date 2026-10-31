"""Replay one accepted SIM3 baseline and expose the new delivery partition."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

from experiments.sim3_eclipse_beam_sweep import (
    ACCEPTED_FIXTURE_BINDING_SHA256,
    METRIC_KEYS,
)
from src.sim.config import SimulationConfig
from src.sim.simulation import Simulation


CASE_ID = "eclipse-0.05_beam-0.80"
ECLIPSE_FRACTION = 0.05
BEAM_EFFICIENCY = 0.8
HOST_DEMAND_RATE = 0.2
RECEIVER_VISIBILITY = 0.25
RECEIVER_PHASE_CENTER = 0.0


def _rounded(value: Any) -> Any:
    if isinstance(value, float):
        return round(value, 9)
    if isinstance(value, dict):
        return {key: _rounded(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_rounded(item) for item in value]
    return value


def _sha256_json(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _validate_spec(spec: dict, baseline_bytes: bytes) -> None:
    if spec["case_id"] != CASE_ID:
        raise ValueError("exactly the accepted eclipse-0.05_beam-0.80 case is required")
    if spec["max_worlds"] != 1 or spec["max_agent_step_records"] != 720:
        raise ValueError("replay budget must remain one world and 720 agent-step records")
    if hashlib.sha256(baseline_bytes).hexdigest() != spec["baseline_artifact_sha256"]:
        raise ValueError("immutable baseline artifact hash mismatch")

    fixture = spec["fixture"]
    environment = fixture["environment"]
    coordinates = spec["replay_coordinates"]
    if (
        fixture["duration"] != 21600.0
        or fixture["dt"] != 300.0
        or fixture["num_agents"] != 10
        or fixture["host_demand_rate"] != HOST_DEMAND_RATE
        or environment["eclipse_fraction"] != ECLIPSE_FRACTION
        or environment["receiver_visibility_fraction"] != RECEIVER_VISIBILITY
        or environment["receiver_phase_center_rad"] != RECEIVER_PHASE_CENTER
        or coordinates["host_demand_rate_Wh_per_h"] != HOST_DEMAND_RATE
        or coordinates["eclipse_fraction"] != ECLIPSE_FRACTION
        or coordinates["beam_efficiency"] != BEAM_EFFICIENCY
        or coordinates["receiver_visibility_fraction"] != RECEIVER_VISIBILITY
        or coordinates["receiver_phase_center_rad"] != RECEIVER_PHASE_CENTER
    ):
        raise ValueError("accepted replay coordinates and record budget must remain fixed")
    if int(fixture["duration"] // fixture["dt"]) * fixture["num_agents"] != 720:
        raise ValueError("fixture must produce exactly 720 agent-step records")

    binding = json.dumps(
        {"fixture": spec["fixture"], "arm": spec["arm"]},
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    if hashlib.sha256(binding).hexdigest() != ACCEPTED_FIXTURE_BINDING_SHA256:
        raise ValueError("fixture and role mix must match the accepted binding")


def _legacy_matches(accepted: object, replayed: object, tolerance: float) -> bool:
    if isinstance(accepted, (int, float)) and not isinstance(accepted, bool):
        return math.isclose(float(accepted), float(replayed), rel_tol=0.0, abs_tol=tolerance)
    return accepted == replayed


def run_replay(spec: dict, baseline_bytes: bytes) -> dict:
    """Run exactly one world and fail before interpretation on legacy drift."""

    _validate_spec(spec, baseline_bytes)
    baseline = json.loads(baseline_bytes)
    matches = [case for case in baseline["cases"] if case["case_id"] == CASE_ID]
    if len(matches) != 1:
        raise ValueError("baseline artifact must contain exactly one accepted case")
    accepted = matches[0]["metrics"]

    payload = dict(spec["fixture"])
    payload["environment"] = {
        **spec["fixture"]["environment"],
        "eclipse_fraction": ECLIPSE_FRACTION,
        "receiver_visibility_fraction": RECEIVER_VISIBILITY,
        "receiver_phase_center_rad": RECEIVER_PHASE_CENTER,
    }
    payload["agent_parameters"] = {
        **spec["fixture"]["agent_parameters"],
        "beam_efficiency": BEAM_EFFICIENCY,
    }
    payload["policy"] = spec["arm"]["policy"]
    payload["agent_roles"] = list(spec["arm"]["agent_roles"])
    summary = Simulation(SimulationConfig.from_dict(payload)).run().summary()
    replayed = _rounded({key: summary[key] for key in METRIC_KEYS})
    tolerance = float(spec["absolute_tolerance_Wh"])
    field_matches = {
        key: _legacy_matches(accepted[key], replayed[key], tolerance)
        for key in METRIC_KEYS
    }
    mismatches = [key for key, matched in field_matches.items() if not matched]
    if mismatches:
        raise ValueError("legacy summary mismatch invalidates attribution: " + ", ".join(mismatches))

    partition = _rounded(summary["delivered_energy_by_role_state_Wh"])
    partition_total = sum(
        amount for role_amounts in partition.values() for amount in role_amounts.values()
    )
    if not math.isclose(
        partition_total,
        float(summary["delivered_total_Wh"]),
        rel_tol=0.0,
        abs_tol=tolerance,
    ):
        raise ValueError("delivery partition does not conserve delivered energy")

    return {
        "schema": "sns.qst-sim-0003.attribution-baseline-replay.v1",
        "quest_id": spec["quest_id"],
        "synthetic": True,
        "baseline_artifact": spec["baseline_artifact"],
        "baseline_artifact_sha256": spec["baseline_artifact_sha256"],
        "accepted_fixture_binding_sha256": ACCEPTED_FIXTURE_BINDING_SHA256,
        "case_id": CASE_ID,
        "new_world_count": 1,
        "agent_step_records": 720,
        "fixed_coordinates": {
            "host_demand_rate_Wh_per_h": HOST_DEMAND_RATE,
            "eclipse_fraction": ECLIPSE_FRACTION,
            "beam_efficiency": BEAM_EFFICIENCY,
            "receiver_visibility_fraction": RECEIVER_VISIBILITY,
            "receiver_phase_center_rad": RECEIVER_PHASE_CENTER,
            "duration_s": 21600.0,
            "dt_s": 300.0,
        },
        "legacy_reproduction": {
            "status": "MATCH",
            "absolute_tolerance": tolerance,
            "field_matches": field_matches,
            "accepted_summary_sha256": _sha256_json(accepted),
            "replayed_summary_sha256": _sha256_json(replayed),
        },
        "measurement": {
            "delivered_total_Wh": _rounded(summary["delivered_total_Wh"]),
            "delivered_energy_by_role_state_Wh": partition,
            "receiver_visible_opportunities_by_role": summary[
                "receiver_visible_opportunities_by_role"
            ],
            "delivery_partition_identity_holds": True,
        },
        "observation": "LEGACY_SUMMARY_REPRODUCED_ATTRIBUTION_MEASURED",
        "claim_boundary": spec["claim_boundary"],
    }


def load_and_run(config_path: Path, root: Path | None = None) -> dict:
    root = root or config_path.resolve().parents[1]
    spec = json.loads(config_path.read_text(encoding="utf-8"))
    baseline_bytes = (root / spec["baseline_artifact"]).read_bytes()
    return run_replay(spec, baseline_bytes)


if __name__ == "__main__":
    repository_root = Path(__file__).resolve().parents[1]
    result = load_and_run(
        repository_root / "configs" / "qst_sim_0003_attribution_baseline_replay.json",
        repository_root,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
