"""Appraise frozen QST-SIM-0003 receiver/eclipsing geometry without rerunning worlds."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

from src.world.geo_ring_world import GEORingWorld


INPUTS = {
    "config": (
        "configs/qst_sim_0003_receiver_phase_position.json",
        "466ab2cd208ce4d319568e3ebebe566fa45b9c93bed486b99438cea643fc979f",
    ),
    "phase": (
        "outputs/qst_sim_0003/receiver_phase_position.json",
        "b0ef8cf034d0d8c7d59731acfe0688e9d7b854fa9852ce6041c15562c9e037fa",
    ),
    "availability": (
        "outputs/qst_sim_0003/receiver_availability.json",
        "63770ec6a7dd551de010af54474d0c61e70e41e16f27bb7519231183bf81ae0d",
    ),
    "sweep": (
        "outputs/qst_sim_0003/eclipse_beam_sweep.json",
        "b94e88b06c4bdd92eb04a291cda2eb967108c4eced744b89e3945157b2f63565",
    ),
}
ELIGIBLE_ROLES = {"relay", "storage"}


def _rounded(value: Any) -> Any:
    if isinstance(value, float):
        return round(value, 9)
    if isinstance(value, dict):
        return {key: _rounded(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_rounded(item) for item in value]
    return value


def _load_bound_inputs(root: Path) -> dict[str, dict]:
    loaded: dict[str, dict] = {}
    for name, (path, expected_sha256) in INPUTS.items():
        payload = (root / path).read_bytes()
        if hashlib.sha256(payload).hexdigest() != expected_sha256:
            raise ValueError(f"accepted {name} input hash mismatch")
        loaded[name] = json.loads(payload)
    return loaded


def _opportunity_counts(spec: dict, *, eclipse_fraction: float, phase_center: float) -> dict:
    fixture = spec["fixture"]
    duration = float(fixture["duration"])
    dt = float(fixture["dt"])
    roles = list(spec["arm"]["agent_roles"])
    world = GEORingWorld(
        solar_flux=float(fixture["solar_flux"]),
        orbital_period_s=float(fixture["environment"]["orbital_period_s"]),
        eclipse_fraction=eclipse_fraction,
        coverage_bin_count=int(fixture["coverage_bin_count"]),
        receiver_phase_center_rad=phase_center,
        receiver_visibility_fraction=float(spec["grid"]["receiver_visibility_fraction"]),
    )
    counts = {
        "eligible_agent_step_count": 0,
        "receiver_visible_agent_step_count": 0,
        "receiver_visible_sunlit_agent_step_count": 0,
        "receiver_visible_eclipse_agent_step_count": 0,
        "receiver_visible_by_role": {"relay": 0, "storage": 0},
    }
    for step_index in range(int(duration // dt)):
        t = step_index * dt
        for index, role in enumerate(roles):
            if role not in ELIGIBLE_ROLES:
                continue
            counts["eligible_agent_step_count"] += 1
            theta = 2.0 * math.pi * index / len(roles)
            if not world.has_line_of_sight_to_host(theta, t):
                continue
            counts["receiver_visible_agent_step_count"] += 1
            counts["receiver_visible_by_role"][role] += 1
            if world.is_sunlit(theta, t):
                counts["receiver_visible_sunlit_agent_step_count"] += 1
            else:
                counts["receiver_visible_eclipse_agent_step_count"] += 1
    return counts


def build_appraisal(root: Path) -> dict:
    """Derive inspectable opportunity accounting from accepted immutable inputs."""

    inputs = _load_bound_inputs(root)
    spec = inputs["config"]
    phase = inputs["phase"]
    availability = inputs["availability"]
    if phase["materiality_classification"] != "NOT_DEFINED_BY_ACCEPTED_ROUTE":
        raise ValueError("accepted phase artifact must retain undefined materiality")
    if phase["baseline_worlds_rerun"] != 0 or availability["baseline_worlds_rerun"] != 0:
        raise ValueError("accepted diagnostic artifacts must not rerun their baselines")

    duration_h = float(spec["fixture"]["duration"]) / 3600.0
    host_demand_Wh = float(spec["fixture"]["host_demand_rate"]) * duration_h
    phase_cases = {case["eclipse_fraction"]: case for case in phase["cases"]}
    baseline_cases = {case["eclipse_fraction"]: case for case in phase["cases"]}

    cases = []
    for eclipse_fraction in spec["grid"]["eclipse_fraction"]:
        for label, phase_center, source_cases, metric_key in (
            ("baseline", 0.0, baseline_cases, "baseline_metrics"),
            ("antipodal", math.pi, phase_cases, "diagnostic_metrics"),
        ):
            source = source_cases[eclipse_fraction]
            delivered = float(source[metric_key]["delivered_total_Wh"])
            counts = _opportunity_counts(
                spec,
                eclipse_fraction=float(eclipse_fraction),
                phase_center=phase_center,
            )
            cases.append(
                _rounded(
                    {
                        "case_id": f"eclipse-{eclipse_fraction:.2f}_phase-{label}",
                        "eclipse_fraction": eclipse_fraction,
                        "receiver_phase_center_rad": phase_center,
                        **counts,
                        "accepted_delivered_total_Wh": delivered,
                        "host_demand_Wh": host_demand_Wh,
                        "accepted_host_service_fraction": delivered / host_demand_Wh,
                    }
                )
            )

    availability_service = [
        _rounded(
            {
                "case_id": case["case_id"],
                "eclipse_fraction": case["eclipse_fraction"],
                "receiver_visibility_fraction": case["diagnostic_receiver_visibility_fraction"],
                "accepted_delivered_total_Wh": case["diagnostic_metrics"]["delivered_total_Wh"],
                "host_demand_Wh": host_demand_Wh,
                "accepted_host_service_fraction": (
                    case["diagnostic_metrics"]["delivered_total_Wh"] / host_demand_Wh
                ),
            }
        )
        for case in availability["cases"]
    ]
    return {
        "schema": "sns.qst-sim-0003.receiver-overlap-appraisal.v1",
        "quest_id": "QST-SIM-0003",
        "synthetic": True,
        "source_files": {
            name: {"path": path, "sha256": sha256}
            for name, (path, sha256) in INPUTS.items()
        },
        "simulation_worlds_rerun": 0,
        "new_world_count": 0,
        "schedule_step_records_evaluated": 288,
        "cases": cases,
        "accepted_always_visible_service": availability_service,
        "observation": "RECEIVER_ECLIPSE_OVERLAP_COVARIES_WITH_SYNTHETIC_DELIVERY",
        "materiality_classification": "NOT_DEFINED_BY_ACCEPTED_ROUTE",
        "interpretation": (
            "The two phase centers have the same 115 receiver-visible relay/storage agent-steps. "
            "At phase zero all 115 are sunlit for both eclipse settings; at phase pi the sunlit "
            "subset falls to 87 and 58 while 28 and 57 visible opportunities occur in eclipse. "
            "Accepted delivery falls in the same direction. This is a model-internal overlap "
            "diagnostic, not proof that overlap alone causes the energy result; policy state, "
            "storage, timestep ordering, and the synthetic fixture remain mediators."
        ),
        "claim_boundary": (
            "Derived only from hash-bound accepted artifacts and deterministic GEORingWorld "
            "geometry. No simulation world, baseline, sweep, phase point, visibility point, role "
            "mix, or holdout was generated or rerun. No post-hoc materiality threshold, preferred "
            "architecture, real ephemeris, relay-performance, mission, or hardware claim is made."
        ),
        "next_measurement": (
            "Before any additional phase or visibility worlds, make host demand, unmet demand, "
            "service fraction, and role-conditioned receiver-visible sunlit/eclipse opportunities "
            "first-class deterministic telemetry with accounting-identity tests."
        ),
    }


if __name__ == "__main__":
    repository_root = Path(__file__).resolve().parents[1]
    print(json.dumps(build_appraisal(repository_root), indent=2, sort_keys=True))
