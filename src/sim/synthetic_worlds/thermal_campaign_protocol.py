"""Fail-closed validator for the QST-SYNTH-0001 R0 protocol.

This module intentionally does not import or call ``generate_records`` or the
thermal evaluator.  R0 freezes a protocol and reports interface gaps; campaign
generation begins only after the protocol is accepted and the adapter exists.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

PROTOCOL_SCHEMA = "sns.synthetic-thermal-campaign-protocol.v1"
ARM_IDS = ("fixed_handwritten", "random_bounded", "agent_curriculum")
SPLIT_IDS = ("development", "holdout")
REQUIRED_INTERFACE_IDS = ("generator", "thermal_evaluator", "public_import_manifest")


class ProtocolError(ValueError):
    """Raised when a protocol is incomplete, mutable, or overclaims readiness."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _object(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ProtocolError(f"{label} must be an object")
    return value


def _finite_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ProtocolError(f"{label} must be numeric")
    number = float(value)
    if not (-float("inf") < number < float("inf")):
        raise ProtocolError(f"{label} must be finite")
    return number


def load_protocol(path: str | Path) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ProtocolError(f"invalid protocol JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ProtocolError("protocol root must be an object")
    return value


def validate_protocol(protocol: Mapping[str, Any], root: str | Path) -> dict[str, Any]:
    root = Path(root)
    required = {
        "schema",
        "quest_id",
        "phase",
        "campaign_state",
        "frozen_at_source",
        "interfaces",
        "arms",
        "generation_procedures",
        "fixed_handwritten_scenarios",
        "splits",
        "policy_family",
        "scenario_ranges",
        "anomaly_types",
        "exclusions",
        "budgets",
        "metrics",
        "criteria",
        "inference",
        "failure_accounting",
        "adapter",
        "reproduction",
        "falsifiers",
    }
    if set(protocol) != required:
        raise ProtocolError("protocol fields do not match the R0 schema")
    if protocol["schema"] != PROTOCOL_SCHEMA or protocol["quest_id"] != "QST-SYNTH-0001":
        raise ProtocolError("protocol schema or quest mismatch")
    if protocol["phase"] != "R0" or protocol["campaign_state"] != "FROZEN_NO_GENERATION":
        raise ProtocolError("R0 must remain a non-generating freeze")
    source = str(protocol["frozen_at_source"])
    if len(source) != 40 or any(character not in "0123456789abcdef" for character in source):
        raise ProtocolError("frozen_at_source must be a Git commit SHA")

    interfaces = _object(protocol["interfaces"], "interfaces")
    if tuple(sorted(interfaces)) != tuple(sorted(REQUIRED_INTERFACE_IDS)):
        raise ProtocolError("required generator/evaluator/import interfaces are not pinned")
    for interface_id in REQUIRED_INTERFACE_IDS:
        interface = _object(interfaces[interface_id], f"interfaces.{interface_id}")
        if set(interface) != {"path", "sha256", "symbols"}:
            raise ProtocolError(f"interfaces.{interface_id} fields are invalid")
        file_path = root / str(interface["path"])
        if not file_path.is_file() or _sha256(file_path) != interface["sha256"]:
            raise ProtocolError(f"pinned interface identity mismatch: {interface_id}")
        if not isinstance(interface["symbols"], list) or not interface["symbols"]:
            raise ProtocolError(f"interfaces.{interface_id}.symbols must be non-empty")

    arms = protocol["arms"]
    if not isinstance(arms, list) or tuple(arm.get("id") for arm in arms if isinstance(arm, Mapping)) != ARM_IDS:
        raise ProtocolError("the three arms must be present in canonical order")
    for arm in arms:
        if set(_object(arm, "arm")) != {"id", "procedure_id", "source", "freeze_rule"}:
            raise ProtocolError("arm fields are invalid")
        if not arm["procedure_id"] or not arm["source"] or not arm["freeze_rule"]:
            raise ProtocolError("arm source and freeze rule must be explicit")

    procedures = _object(protocol["generation_procedures"], "generation_procedures")
    expected_procedure_ids = {
        "literal_development_scenarios",
        "deterministic_uniform_development",
        "deterministic_maximin_development",
        "shared_holdout",
    }
    if set(procedures) != expected_procedure_ids:
        raise ProtocolError("all arm and shared-holdout generation procedures must be frozen")
    if {arm["procedure_id"] for arm in arms} != expected_procedure_ids - {"shared_holdout"}:
        raise ProtocolError("each arm must bind exactly one frozen generation procedure")
    literal = _object(procedures["literal_development_scenarios"], "literal procedure")
    if literal != {
        "method": "literal_scenarios",
        "source": "fixed_handwritten_scenarios.development",
        "selection_order": "array_order",
        "holdout_access": "forbidden",
    }:
        raise ProtocolError("literal arm procedure is not executable and frozen")
    uniform = _object(procedures["deterministic_uniform_development"], "uniform procedure")
    if uniform != {
        "method": "deterministic_uniform",
        "rng": "src.sim.synthetic_worlds.recipe.DeterministicRandom.uniform",
        "seed_source": "splits.development.seeds",
        "parameter_order": "lexicographic",
        "draws_per_parameter": 1,
        "round_decimal_places": 12,
        "holdout_access": "forbidden",
    }:
        raise ProtocolError("random arm procedure is not executable and frozen")
    curriculum = _object(procedures["deterministic_maximin_development"], "curriculum procedure")
    if curriculum != {
        "method": "deterministic_maximin_from_bounded_pool",
        "rng": "src.sim.synthetic_worlds.recipe.DeterministicRandom.uniform",
        "seed_source": "splits.development.seeds",
        "candidate_pool_per_world": 3,
        "parameter_order": "lexicographic",
        "normalization": "scenario_ranges_min_max_constant_dimensions_zero",
        "reference_set": "fixed_handwritten_scenarios.development",
        "selection": "greedy_maximize_minimum_l1_distance",
        "tie_break": "canonical_json_lexicographic",
        "outcome_feedback": False,
        "round_decimal_places": 12,
        "holdout_access": "forbidden",
    }:
        raise ProtocolError("agent-curriculum procedure is not executable and frozen")
    shared_holdout = _object(procedures["shared_holdout"], "shared holdout procedure")
    if shared_holdout != {
        "method": "literal_scenarios",
        "source": "fixed_handwritten_scenarios.holdout",
        "selection_order": "array_order",
        "shared_identical_world_bytes": True,
        "visibility": "sealed_until_R2",
    }:
        raise ProtocolError("holdout must be one frozen shared world set")

    splits = _object(protocol["splits"], "splits")
    if tuple(splits) != SPLIT_IDS:
        raise ProtocolError("development and holdout splits are required in canonical order")
    all_seeds: set[str] = set()
    total_worlds = 0
    for split_id in SPLIT_IDS:
        split = _object(splits[split_id], f"splits.{split_id}")
        expected_split_fields = (
            {"worlds_per_arm", "seeds", "replacement"}
            if split_id == "development"
            else {"shared_worlds", "seeds", "shared_identical_world_bytes", "replacement"}
        )
        if set(split) != expected_split_fields:
            raise ProtocolError(f"splits.{split_id} fields are invalid")
        count = split["worlds_per_arm"] if split_id == "development" else split["shared_worlds"]
        seeds = split["seeds"]
        if not isinstance(count, int) or isinstance(count, bool) or not 1 <= count <= 3:
            raise ProtocolError("each split must freeze one to three worlds per arm")
        if not isinstance(seeds, list) or len(seeds) != count or any(not isinstance(seed, str) or not seed for seed in seeds):
            raise ProtocolError("split seed count must match worlds_per_arm")
        if len(set(seeds)) != len(seeds):
            raise ProtocolError("seeds within each split must be unique")
        if all_seeds.intersection(seeds):
            raise ProtocolError("development and holdout seeds must not overlap")
        all_seeds.update(seeds)
        if split["replacement"] is not False:
            raise ProtocolError("post-freeze world replacement is forbidden")
        if split_id == "holdout" and split["shared_identical_world_bytes"] is not True:
            raise ProtocolError("holdout worlds must be shared identically across arms")
        total_worlds += count * len(ARM_IDS) if split_id == "development" else count

    budgets = _object(protocol["budgets"], "budgets")
    if set(budgets) != {"worlds", "records", "runtime_s", "disk_mb", "development_worlds_per_arm", "shared_holdout_worlds"}:
        raise ProtocolError("budget fields are invalid")
    for key in ("worlds", "records", "runtime_s", "disk_mb", "development_worlds_per_arm", "shared_holdout_worlds"):
        if not isinstance(budgets[key], int) or isinstance(budgets[key], bool) or budgets[key] < 1:
            raise ProtocolError(f"budgets.{key} must be a positive integer")
    if budgets["worlds"] != total_worlds or budgets["records"] != total_worlds:
        raise ProtocolError("world and record budgets must exactly match the frozen splits")
    if budgets["development_worlds_per_arm"] != splits["development"]["worlds_per_arm"]:
        raise ProtocolError("development arms must have matched world budgets")
    if budgets["shared_holdout_worlds"] != splits["holdout"]["shared_worlds"]:
        raise ProtocolError("shared holdout budget must match the frozen split")
    if budgets["worlds"] > 64 or budgets["records"] > 100_000 or budgets["runtime_s"] > 600 or budgets["disk_mb"] > 100:
        raise ProtocolError("protocol exceeds standing constitutional ceilings")

    ranges = _object(protocol["scenario_ranges"], "scenario_ranges")
    for name, spec_value in ranges.items():
        spec = _object(spec_value, f"scenario_ranges.{name}")
        if set(spec) != {"minimum", "maximum", "unit", "basis"}:
            raise ProtocolError(f"scenario range fields are invalid: {name}")
        low = _finite_number(spec["minimum"], f"{name}.minimum")
        high = _finite_number(spec["maximum"], f"{name}.maximum")
        if low > high or not spec["unit"] or not spec["basis"]:
            raise ProtocolError(f"invalid scenario range: {name}")

    fixed = _object(protocol["fixed_handwritten_scenarios"], "fixed_handwritten_scenarios")
    if tuple(fixed) != SPLIT_IDS:
        raise ProtocolError("fixed scenarios must be separated into development and holdout")
    scenario_names: set[str] = set()
    for split_id in SPLIT_IDS:
        scenarios = fixed[split_id]
        expected_count = splits[split_id]["worlds_per_arm"] if split_id == "development" else splits[split_id]["shared_worlds"]
        if not isinstance(scenarios, list) or len(scenarios) != expected_count:
            raise ProtocolError("fixed scenario count must match its split budget")
        for scenario in scenarios:
            if set(_object(scenario, "fixed scenario")) != {"name", "parameters"}:
                raise ProtocolError("fixed scenario fields are invalid")
            name = scenario["name"]
            parameters = _object(scenario["parameters"], f"fixed scenario {name}")
            if not isinstance(name, str) or not name or name in scenario_names:
                raise ProtocolError("fixed scenario names must be unique and non-empty")
            scenario_names.add(name)
            if set(parameters) != set(ranges):
                raise ProtocolError("fixed scenario parameters must exactly match scenario_ranges")
            for parameter, value in parameters.items():
                number = _finite_number(value, f"{name}.{parameter}")
                low = float(ranges[parameter]["minimum"])
                high = float(ranges[parameter]["maximum"])
                if not low <= number <= high:
                    raise ProtocolError(f"fixed scenario parameter outside range: {name}.{parameter}")

    metrics = _object(protocol["metrics"], "metrics")
    if set(metrics) != {"supported", "missing"}:
        raise ProtocolError("metric fields are invalid")
    if any(not isinstance(values, list) or not values or any(not isinstance(item, str) or not item for item in values) for values in metrics.values()):
        raise ProtocolError("supported and missing metrics must both be explicit")
    policy = _object(protocol["policy_family"], "policy_family")
    if set(policy) != {"id", "description", "state"} or policy["state"] != "EVALUATOR_PRESENT_POLICY_ADAPTER_MISSING":
        raise ProtocolError("policy family or adapter state is not frozen")
    anomalies = protocol["anomaly_types"]
    expected_anomalies = {
        "battery_capacity_shortfall": "SUPPORTED_BY_nominal_battery_Wh",
        "thermal_buffer_variation": "SUPPORTED_BY_pcm_mass_kg",
        "eclipse_duration_variation": "EXCLUDED_PENDING_ACCEPTED_RANGE",
        "degradation_trajectory": "MISSING_EVALUATOR_INTERFACE",
        "sensor_failure": "MISSING_EVALUATOR_INTERFACE",
    }
    if not isinstance(anomalies, list) or {
        item.get("id"): item.get("state") for item in anomalies if isinstance(item, Mapping) and set(item) == {"id", "state"}
    } != expected_anomalies:
        raise ProtocolError("anomaly coverage and interface states must be explicit")
    criteria = _object(protocol["criteria"], "criteria")
    if set(criteria) != {"survival", "curriculum_observation", "delivery_tolerance", "nontriviality", "coverage"}:
        raise ProtocolError("comparison criteria are incomplete")
    if any(not isinstance(value, str) or not value for value in criteria.values()):
        raise ProtocolError("comparison criteria must be non-empty text")
    inference = _object(protocol["inference"], "inference")
    if inference != {
        "claim_level": "EXPLORATORY_WORLD_GENERATION_QUALITY_ONLY",
        "survival_interval": "wilson_score_two_sided",
        "confidence_level": 0.95,
        "minimum_confirmatory_holdout_worlds": 30,
        "policy_benefit_claim_allowed": False,
        "small_sample_rule": "Report raw counts, fractions, and Wilson intervals; no ordering from three worlds is confirmatory or statistically demonstrated.",
    }:
        raise ProtocolError("small-sample inference and claim boundary must be frozen")
    adapter = _object(protocol["adapter"], "adapter")
    if set(adapter) != {"state", "missing_interfaces", "next_stage"} or adapter.get("state") != "REQUIRED_BEFORE_R1" or not adapter.get("missing_interfaces"):
        raise ProtocolError("R0 must fail closed on the missing adapter")
    if not isinstance(adapter["missing_interfaces"], list) or any(not isinstance(item, str) or not item for item in adapter["missing_interfaces"]):
        raise ProtocolError("missing adapter interfaces must be explicit")
    reproduction = _object(protocol["reproduction"], "reproduction")
    if set(reproduction) != {"command", "generates_worlds", "expected_status"} or reproduction.get("generates_worlds") is not False or " validate " not in f" {reproduction.get('command', '')} ":
        raise ProtocolError("reproduction must be a validation-only command")
    for field in ("falsifiers", "exclusions", "failure_accounting"):
        values = protocol[field]
        if not isinstance(values, list) or not values or any(not isinstance(item, str) or not item for item in values):
            raise ProtocolError(f"{field} must be non-empty explicit text")

    return {
        "status": "PROTOCOL_VALID_ADAPTER_REQUIRED",
        "quest_id": protocol["quest_id"],
        "world_budget": total_worlds,
        "arms": list(ARM_IDS),
        "generation_performed": False,
        "missing_interfaces": list(adapter["missing_interfaces"]),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate",))
    parser.add_argument("protocol")
    parser.add_argument("--root", default=".")
    args = parser.parse_args(argv)
    summary = validate_protocol(load_protocol(args.protocol), args.root)
    print(json.dumps(summary, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
