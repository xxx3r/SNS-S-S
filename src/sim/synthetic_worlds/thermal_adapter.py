"""Qualified R1 adapter between synthetic-world records and the thermal model.

The adapter is intentionally narrow.  It consumes already-validated record
bytes, makes every ``ThermalShadowScenario`` input explicit, and exposes only
quantities supported by the accepted evaluator.  It does not generate worlds
or inspect the sealed holdout.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, fields
from pathlib import Path
from typing import Any, Mapping, Sequence

from src.sim.thermal_storage import ThermalShadowScenario, simulate_thermal_shadow

from .common import RECORD_SCHEMA, ValidationError, stable_hash

ADAPTER_SCHEMA = "sns.synthetic-thermal-adapter.v1"
FIXTURE_SCHEMA = "sns.synthetic-thermal-development-fixture.v1"
ARM_IDS = ("fixed_handwritten", "random_bounded", "agent_curriculum")
POLICY_FIELDS = ("base_load_W", "heater_threshold_K", "heater_power_W")
RECORD_KEYS = {"schema_version", "record_id", "parameters", "samples", "rng", "record_hash"}


def _object(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValidationError(f"{label} must be an object")
    return value


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_adapter_spec(path: str | Path) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValidationError(f"invalid thermal adapter specification: {exc}") from exc
    if not isinstance(value, dict):
        raise ValidationError("thermal adapter specification must be an object")
    return value


def validate_adapter_spec(spec: Mapping[str, Any], root: str | Path) -> None:
    required = {
        "schema",
        "quest_id",
        "phase",
        "state",
        "frozen_at_source",
        "protocol",
        "record_parameter_fields",
        "record_parameter_ranges",
        "declared_model_defaults",
        "policy_derivation",
        "useful_delivery",
        "action_trace",
        "development_fixture",
    }
    if set(spec) != required:
        raise ValidationError("thermal adapter specification fields are invalid")
    if (
        spec["schema"] != ADAPTER_SCHEMA
        or spec["quest_id"] != "QST-SYNTH-0001"
        or spec["phase"] != "R1"
        or spec["state"] != "QUALIFIED_NO_GENERATION"
    ):
        raise ValidationError("thermal adapter identity or state is invalid")
    source = spec["frozen_at_source"]
    if not isinstance(source, str) or len(source) != 40 or any(c not in "0123456789abcdef" for c in source):
        raise ValidationError("frozen_at_source must be a Git commit SHA")

    root = Path(root)
    protocol = _object(spec["protocol"], "protocol")
    if set(protocol) != {"path", "sha256"}:
        raise ValidationError("protocol binding fields are invalid")
    protocol_path = root / str(protocol["path"])
    if not protocol_path.is_file() or _file_sha256(protocol_path) != protocol["sha256"]:
        raise ValidationError("accepted R0 protocol identity mismatch")
    try:
        protocol_value = json.loads(protocol_path.read_text(encoding="utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValidationError(f"invalid accepted R0 protocol: {exc}") from exc

    record_fields = spec["record_parameter_fields"]
    expected_record_fields = sorted(protocol_value["scenario_ranges"])
    if record_fields != expected_record_fields:
        raise ValidationError("record parameter fields must match the accepted R0 ranges")
    record_ranges = _object(spec["record_parameter_ranges"], "record_parameter_ranges")
    expected_ranges = {
        name: {
            "minimum": protocol_value["scenario_ranges"][name]["minimum"],
            "maximum": protocol_value["scenario_ranges"][name]["maximum"],
        }
        for name in expected_record_fields
    }
    if dict(record_ranges) != expected_ranges:
        raise ValidationError("record parameter ranges must match the accepted R0 protocol")

    defaults = _object(spec["declared_model_defaults"], "declared_model_defaults")
    scenario_fields = {item.name: item for item in fields(ThermalShadowScenario)}
    expected_defaults = {
        name: scenario_fields[name].default
        for name in scenario_fields
        if name not in expected_record_fields
    }
    if dict(defaults) != expected_defaults:
        raise ValidationError("model defaults must be explicit and match the pinned evaluator")

    derivation = _object(spec["policy_derivation"], "policy_derivation")
    if derivation != {
        "interface": "derive_arm_policy_v1",
        "arms": list(ARM_IDS),
        "family_id": "thermal-shadow-fixed-thermostat-v1",
        "parameter_fields": list(POLICY_FIELDS),
        "outcome_feedback": False,
        "claim_boundary": "NO_POLICY_BENEFIT_IN_R1",
    }:
        raise ValidationError("arm-policy derivation interface is not frozen")

    delivery = _object(spec["useful_delivery"], "useful_delivery")
    if delivery != {
        "metric": "useful_host_delivery_Wh",
        "pass_rule": "base_load_W_times_eclipse_duration_h",
        "failure_value": None,
        "failure_state": "NOT_RESOLVED_BY_ACCEPTED_EVALUATOR",
    }:
        raise ValidationError("useful-delivery rule exceeds the accepted evaluator")
    trace = _object(spec["action_trace"], "action_trace")
    if trace != {
        "schema": "sns.thermal-policy-action-trace.v1",
        "resolution": "AGGREGATE_MODEL_SUPPORTED",
        "actions": ["constant_host_load", "threshold_heater"],
        "step_timestamps_available": False,
    }:
        raise ValidationError("policy-action trace boundary is not frozen")

    fixture = _object(spec["development_fixture"], "development_fixture")
    if set(fixture) != {"path", "sha256", "split", "generated_worlds"} or fixture["split"] != "development" or fixture["generated_worlds"] != 0:
        raise ValidationError("R1 fixture must be development-only and non-generating")
    fixture_path = root / str(fixture["path"])
    if not fixture_path.is_file() or _file_sha256(fixture_path) != fixture["sha256"]:
        raise ValidationError("development fixture identity mismatch")


def validate_world_record(record: Mapping[str, Any], spec: Mapping[str, Any]) -> None:
    if set(record) != RECORD_KEYS or record.get("schema_version") != RECORD_SCHEMA:
        raise ValidationError("synthetic-world record schema mismatch")
    record_id = record.get("record_id")
    if not isinstance(record_id, int) or isinstance(record_id, bool) or record_id < 0:
        raise ValidationError("record_id must be a non-negative integer")
    if record.get("record_hash") != stable_hash({key: value for key, value in record.items() if key != "record_hash"}):
        raise ValidationError("synthetic-world record hash mismatch")
    parameters = _object(record.get("parameters"), "record.parameters")
    if sorted(parameters) != list(spec["record_parameter_fields"]):
        raise ValidationError("record parameters do not match the accepted R0 fields")
    ranges = _object(spec["record_parameter_ranges"], "record_parameter_ranges")
    for name, value in parameters.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
            raise ValidationError(f"record parameter must be finite: {name}")
        bounds = _object(ranges[name], f"record_parameter_ranges.{name}")
        if not float(bounds["minimum"]) <= float(value) <= float(bounds["maximum"]):
            raise ValidationError(f"record parameter outside accepted R0 range: {name}")


def record_to_scenario(record: Mapping[str, Any], spec: Mapping[str, Any]) -> ThermalShadowScenario:
    """Map one validated record to a scenario with no implicit dataclass defaults."""

    validate_world_record(record, spec)
    parameters = dict(_object(record["parameters"], "record.parameters"))
    defaults = dict(_object(spec["declared_model_defaults"], "declared_model_defaults"))
    if set(parameters).intersection(defaults):
        raise ValidationError("record parameters may not override declared model defaults")
    values = {**parameters, **defaults}
    expected = {item.name for item in fields(ThermalShadowScenario)}
    if set(values) != expected:
        raise ValidationError("adapter did not resolve every scenario field explicitly")
    try:
        scenario = ThermalShadowScenario(**values)
        scenario.validate()
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"invalid thermal scenario: {exc}") from exc
    return scenario


def derive_arm_policy(
    arm_id: str,
    scenarios: Sequence[ThermalShadowScenario],
    spec: Mapping[str, Any],
) -> dict[str, Any]:
    """Derive the accepted fixed policy without consulting evaluator outcomes."""

    if arm_id not in ARM_IDS or not scenarios:
        raise ValidationError("policy derivation requires one accepted arm and scenario")
    reference = {name: getattr(scenarios[0], name) for name in POLICY_FIELDS}
    if any({name: getattr(scenario, name) for name in POLICY_FIELDS} != reference for scenario in scenarios[1:]):
        raise ValidationError("R1 cannot derive a policy from inconsistent policy parameters")
    derivation = _object(spec["policy_derivation"], "policy_derivation")
    return {
        "schema": "sns.thermal-arm-policy.v1",
        "interface": derivation["interface"],
        "arm_id": arm_id,
        "family_id": derivation["family_id"],
        "parameters": reference,
        "outcome_feedback": False,
        "claim_boundary": derivation["claim_boundary"],
    }


def evaluate_development_record(
    record: Mapping[str, Any],
    arm_id: str,
    spec: Mapping[str, Any],
) -> dict[str, Any]:
    """Evaluate one development fixture and expose only supported aggregates."""

    scenario = record_to_scenario(record, spec)
    policy = derive_arm_policy(arm_id, [scenario], spec)
    result = simulate_thermal_shadow(scenario)
    host_demand_Wh = scenario.base_load_W * scenario.eclipse_duration_h
    useful_delivery_Wh = host_demand_Wh if result.electrical_status == "PASS" else None
    heater_on_time_s = 0.0
    if scenario.heater_power_W > 0.0:
        heater_on_time_s = result.heater_energy_Wh * 3600.0 / scenario.heater_power_W
    return {
        "schema": "sns.synthetic-thermal-development-evaluation.v1",
        "record_id": record["record_id"],
        "record_hash": record["record_hash"],
        "arm_policy": policy,
        "result": asdict(result),
        "useful_host_delivery_Wh": useful_delivery_Wh,
        "useful_delivery_state": (
            "FULL_DEMAND_SUPPORTED"
            if useful_delivery_Wh is not None
            else spec["useful_delivery"]["failure_state"]
        ),
        "policy_action_trace": {
            "schema": spec["action_trace"]["schema"],
            "resolution": spec["action_trace"]["resolution"],
            "step_timestamps_available": False,
            "actions": [
                {
                    "action": "constant_host_load",
                    "power_W": scenario.base_load_W,
                    "requested_energy_Wh": host_demand_Wh,
                },
                {
                    "action": "threshold_heater",
                    "threshold_K": scenario.heater_threshold_K,
                    "rated_power_W": scenario.heater_power_W,
                    "aggregate_on_time_s": heater_on_time_s,
                    "energy_Wh": result.heater_energy_Wh,
                },
            ],
        },
        "claim_boundary": "DEVELOPMENT_FIXTURE_INTERFACE_QUALIFICATION_ONLY",
    }


def load_development_fixture(path: str | Path) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValidationError(f"invalid development fixture: {exc}") from exc
    if not isinstance(value, dict) or set(value) != {"schema", "quest_id", "split", "arm_id", "generated_worlds", "record"}:
        raise ValidationError("development fixture fields are invalid")
    if (
        value["schema"] != FIXTURE_SCHEMA
        or value["quest_id"] != "QST-SYNTH-0001"
        or value["split"] != "development"
        or value["arm_id"] not in ARM_IDS
        or value["generated_worlds"] != 0
    ):
        raise ValidationError("fixture must be a non-generated development record")
    return value
