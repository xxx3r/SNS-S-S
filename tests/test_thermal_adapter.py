from __future__ import annotations

import copy
import hashlib
import json
import shutil
from dataclasses import asdict
from pathlib import Path

import pytest

from src.sim.synthetic_worlds.common import ValidationError, stable_hash
from src.sim.synthetic_worlds.thermal_adapter import (
    derive_arm_policy,
    evaluate_development_record,
    load_adapter_spec,
    load_development_fixture,
    record_to_scenario,
    validate_adapter_spec,
    validate_world_record,
)

ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "configs" / "synthetic_worlds" / "thermal_adapter_r1.json"
FIXTURE_PATH = ROOT / "configs" / "synthetic_worlds" / "thermal_adapter_development_fixture.json"


def spec() -> dict:
    return load_adapter_spec(SPEC_PATH)


def fixture() -> dict:
    return load_development_fixture(FIXTURE_PATH)


def rehash(record: dict) -> None:
    record["record_hash"] = stable_hash({key: value for key, value in record.items() if key != "record_hash"})


def copy_validation_tree(tmp_path: Path) -> Path:
    sandbox = tmp_path / "repo"
    required = [
        "configs/synthetic_worlds/thermal_stress_protocol.json",
        "configs/synthetic_worlds/thermal_adapter_development_fixture.json",
        "src/sim/synthetic_worlds/recipe.py",
        "src/sim/thermal_storage.py",
        "src/sim/SYNTHETIC_WORLDS_IMPORT_MANIFEST.json",
    ]
    for relative in required:
        target = sandbox / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    return sandbox


def test_r1_spec_and_development_fixture_are_qualified_without_generation() -> None:
    frozen = spec()
    validate_adapter_spec(frozen, ROOT)
    development = fixture()
    validate_world_record(development["record"], frozen)

    assert development["split"] == "development"
    assert development["generated_worlds"] == 0
    assert frozen["state"] == "QUALIFIED_NO_GENERATION"


def test_record_mapping_resolves_every_scenario_field_explicitly() -> None:
    frozen = spec()
    scenario = record_to_scenario(fixture()["record"], frozen)

    assert asdict(scenario) == {
        **fixture()["record"]["parameters"],
        **frozen["declared_model_defaults"],
    }

    missing = copy.deepcopy(fixture()["record"])
    missing["parameters"].pop("base_load_W")
    rehash(missing)
    with pytest.raises(ValidationError, match="accepted R0 fields"):
        record_to_scenario(missing, frozen)


def test_record_hash_and_undeclared_parameter_fail_closed() -> None:
    frozen = spec()
    altered = copy.deepcopy(fixture()["record"])
    altered["parameters"]["nominal_battery_Wh"] = 0.25
    with pytest.raises(ValidationError, match="hash mismatch"):
        validate_world_record(altered, frozen)

    undeclared = copy.deepcopy(fixture()["record"])
    undeclared["parameters"]["discharge_efficiency"] = 0.99
    rehash(undeclared)
    with pytest.raises(ValidationError, match="accepted R0 fields"):
        validate_world_record(undeclared, frozen)

    outside = copy.deepcopy(fixture()["record"])
    outside["parameters"]["nominal_battery_Wh"] = 0.501
    rehash(outside)
    with pytest.raises(ValidationError, match="outside accepted R0 range"):
        validate_world_record(outside, frozen)


def test_policy_derivation_is_arm_bound_and_outcome_free() -> None:
    frozen = spec()
    scenario = record_to_scenario(fixture()["record"], frozen)
    policy = derive_arm_policy("fixed_handwritten", [scenario], frozen)

    assert policy == {
        "schema": "sns.thermal-arm-policy.v1",
        "interface": "derive_arm_policy_v1",
        "arm_id": "fixed_handwritten",
        "family_id": "thermal-shadow-fixed-thermostat-v1",
        "parameters": {
            "base_load_W": 0.01,
            "heater_threshold_K": 263.15,
            "heater_power_W": 0.08,
        },
        "outcome_feedback": False,
        "claim_boundary": "NO_POLICY_BENEFIT_IN_R1",
    }

    inconsistent = copy.deepcopy(asdict(scenario))
    inconsistent["heater_threshold_K"] = 260.0
    with pytest.raises(ValidationError, match="inconsistent policy parameters"):
        derive_arm_policy("fixed_handwritten", [scenario, type(scenario)(**inconsistent)], frozen)


def test_development_evaluation_exposes_only_supported_delivery_and_actions() -> None:
    frozen = spec()
    development = fixture()
    evaluated = evaluate_development_record(development, frozen, ROOT)

    assert evaluated["claim_boundary"] == "DEVELOPMENT_FIXTURE_INTERFACE_QUALIFICATION_ONLY"
    assert evaluated["useful_host_delivery_Wh"] == pytest.approx(0.02)
    assert evaluated["useful_delivery_state"] == "FULL_DEMAND_SUPPORTED"
    trace = evaluated["policy_action_trace"]
    assert trace["resolution"] == "AGGREGATE_MODEL_SUPPORTED"
    assert trace["step_timestamps_available"] is False
    assert [action["action"] for action in trace["actions"]] == [
        "constant_host_load",
        "threshold_heater",
    ]


def test_electrical_failure_does_not_invent_useful_delivery(tmp_path: Path) -> None:
    frozen = spec()
    failed = copy.deepcopy(fixture())
    failed["record"]["parameters"]["nominal_battery_Wh"] = 0.015
    rehash(failed["record"])
    sandbox = copy_validation_tree(tmp_path)
    fixture_path = sandbox / frozen["development_fixture"]["path"]
    payload = json.dumps(failed, indent=2) + "\n"
    fixture_path.write_text(payload, encoding="utf-8")
    frozen["development_fixture"]["sha256"] = hashlib.sha256(payload.encode()).hexdigest()

    evaluated = evaluate_development_record(failed, frozen, sandbox)

    assert evaluated["result"]["electrical_status"] == "FAIL"
    assert evaluated["useful_host_delivery_Wh"] is None
    assert evaluated["useful_delivery_state"] == "NOT_RESOLVED_BY_ACCEPTED_EVALUATOR"


def test_adapter_spec_rejects_hidden_defaults_and_holdout_fixture() -> None:
    hidden = copy.deepcopy(spec())
    hidden["declared_model_defaults"].pop("reserve_fraction")
    with pytest.raises(ValidationError, match="defaults must be explicit"):
        validate_adapter_spec(hidden, ROOT)

    holdout = copy.deepcopy(spec())
    holdout["development_fixture"]["split"] = "holdout"
    with pytest.raises(ValidationError, match="development-only"):
        validate_adapter_spec(holdout, ROOT)


def test_adapter_spec_rejects_pinned_evaluator_source_drift(tmp_path: Path) -> None:
    frozen = spec()
    sandbox = copy_validation_tree(tmp_path)

    evaluator = sandbox / "src/sim/thermal_storage.py"
    evaluator.write_text(evaluator.read_text(encoding="utf-8") + "\n# source drift\n", encoding="utf-8")

    with pytest.raises(ValidationError, match="pinned interface identity mismatch: thermal_evaluator"):
        validate_adapter_spec(frozen, sandbox)


def test_development_evaluation_rejects_unbound_or_relabelled_records() -> None:
    frozen = spec()
    development = fixture()

    with pytest.raises(ValidationError, match="pinned R1 fixture"):
        evaluate_development_record(development["record"], frozen, ROOT)

    relabelled = copy.deepcopy(development)
    relabelled["split"] = "holdout"
    with pytest.raises(ValidationError, match="pinned R1 fixture"):
        evaluate_development_record(relabelled, frozen, ROOT)

    protocol = json.loads((ROOT / "configs/synthetic_worlds/thermal_stress_protocol.json").read_text())
    disguised = copy.deepcopy(development)
    disguised["record"]["parameters"] = protocol["fixed_handwritten_scenarios"]["holdout"][0]["parameters"]
    rehash(disguised["record"])
    with pytest.raises(ValidationError, match="pinned R1 fixture"):
        evaluate_development_record(disguised, frozen, ROOT)
