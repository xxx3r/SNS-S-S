from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from src.sim.synthetic_worlds.thermal_campaign_protocol import (
    ProtocolError,
    load_protocol,
    main,
    validate_protocol,
)

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_PATH = ROOT / "configs" / "synthetic_worlds" / "thermal_stress_protocol.json"


def protocol() -> dict:
    return load_protocol(PROTOCOL_PATH)


def test_r0_protocol_is_valid_but_adapter_blocked() -> None:
    summary = validate_protocol(protocol(), ROOT)

    assert summary == {
        "status": "PROTOCOL_VALID_ADAPTER_REQUIRED",
        "quest_id": "QST-SYNTH-0001",
        "world_budget": 12,
        "arms": ["fixed_handwritten", "random_bounded", "agent_curriculum"],
        "generation_performed": False,
        "missing_interfaces": protocol()["adapter"]["missing_interfaces"],
    }


def test_protocol_pins_actual_generator_evaluator_and_import_bytes() -> None:
    frozen = protocol()
    for interface in frozen["interfaces"].values():
        path = ROOT / interface["path"]
        assert path.is_file()

    mismatched = copy.deepcopy(frozen)
    mismatched["interfaces"]["generator"]["sha256"] = "0" * 64
    with pytest.raises(ProtocolError, match="pinned interface identity mismatch"):
        validate_protocol(mismatched, ROOT)


def test_holdout_overlap_and_replacement_fail_closed() -> None:
    overlapping = copy.deepcopy(protocol())
    overlapping["splits"]["holdout"]["seeds"][0] = overlapping["splits"]["development"]["seeds"][0]
    with pytest.raises(ProtocolError, match="must not overlap"):
        validate_protocol(overlapping, ROOT)

    replacing = copy.deepcopy(protocol())
    replacing["splits"]["holdout"]["replacement"] = True
    with pytest.raises(ProtocolError, match="replacement is forbidden"):
        validate_protocol(replacing, ROOT)

    duplicate = copy.deepcopy(protocol())
    duplicate["splits"]["development"]["seeds"][1] = duplicate["splits"]["development"]["seeds"][0]
    with pytest.raises(ProtocolError, match="within each split must be unique"):
        validate_protocol(duplicate, ROOT)


def test_generation_procedures_and_shared_holdout_are_frozen() -> None:
    changed_recipe = copy.deepcopy(protocol())
    changed_recipe["generation_procedures"]["deterministic_uniform_development"]["parameter_order"] = "insertion"
    with pytest.raises(ProtocolError, match="random arm procedure"):
        validate_protocol(changed_recipe, ROOT)

    outcome_tuned = copy.deepcopy(protocol())
    outcome_tuned["generation_procedures"]["deterministic_maximin_development"]["outcome_feedback"] = True
    with pytest.raises(ProtocolError, match="agent-curriculum procedure"):
        validate_protocol(outcome_tuned, ROOT)

    private_holdout = copy.deepcopy(protocol())
    private_holdout["splits"]["holdout"]["shared_identical_world_bytes"] = False
    with pytest.raises(ProtocolError, match="shared identically"):
        validate_protocol(private_holdout, ROOT)


def test_fixed_scenarios_are_complete_separate_and_bounded() -> None:
    frozen = protocol()
    development = frozen["fixed_handwritten_scenarios"]["development"]
    holdout = frozen["fixed_handwritten_scenarios"]["holdout"]
    assert {row["name"] for row in development}.isdisjoint(row["name"] for row in holdout)

    incomplete = copy.deepcopy(frozen)
    incomplete["fixed_handwritten_scenarios"]["holdout"][0]["parameters"].pop("base_load_W")
    with pytest.raises(ProtocolError, match="exactly match"):
        validate_protocol(incomplete, ROOT)

    outside = copy.deepcopy(frozen)
    outside["fixed_handwritten_scenarios"]["holdout"][0]["parameters"]["nominal_battery_Wh"] = 1.0
    with pytest.raises(ProtocolError, match="outside range"):
        validate_protocol(outside, ROOT)


def test_metric_criteria_and_anomaly_gaps_cannot_be_erased() -> None:
    missing_metric = copy.deepcopy(protocol())
    missing_metric["metrics"]["missing"] = []
    with pytest.raises(ProtocolError, match="must both be explicit"):
        validate_protocol(missing_metric, ROOT)

    missing_criterion = copy.deepcopy(protocol())
    missing_criterion["criteria"].pop("delivery_tolerance")
    with pytest.raises(ProtocolError, match="criteria are incomplete"):
        validate_protocol(missing_criterion, ROOT)

    hidden_anomaly = copy.deepcopy(protocol())
    hidden_anomaly["anomaly_types"][-1]["state"] = "SUPPORTED"
    with pytest.raises(ProtocolError, match="anomaly coverage"):
        validate_protocol(hidden_anomaly, ROOT)

    overclaim = copy.deepcopy(protocol())
    overclaim["inference"]["policy_benefit_claim_allowed"] = True
    with pytest.raises(ProtocolError, match="claim boundary"):
        validate_protocol(overclaim, ROOT)


def test_budget_and_missing_adapter_cannot_be_hidden() -> None:
    over_budget = copy.deepcopy(protocol())
    over_budget["budgets"]["worlds"] = 65
    with pytest.raises(ProtocolError, match="exactly match"):
        validate_protocol(over_budget, ROOT)

    over_budget = copy.deepcopy(protocol())
    over_budget["splits"]["development"]["worlds_per_arm"] = 22
    with pytest.raises(ProtocolError, match="one to three"):
        validate_protocol(over_budget, ROOT)

    false_ready = copy.deepcopy(protocol())
    false_ready["adapter"]["state"] = "READY"
    with pytest.raises(ProtocolError, match="fail closed"):
        validate_protocol(false_ready, ROOT)


def test_cli_is_validation_only(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["validate", str(PROTOCOL_PATH), "--root", str(ROOT)]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["generation_performed"] is False
    assert result["status"] == "PROTOCOL_VALID_ADAPTER_REQUIRED"
