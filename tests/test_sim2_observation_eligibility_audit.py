"""Regression tests for the non-generating SIM2 observation audit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

import pytest

from experiments.sim2_observation_eligibility_audit import audit_repository


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "outputs/qst_sim_0002/observation_eligibility_audit.json"
ACCEPTED_RESULT = ROOT / "outputs/qst_sim_0002/rotation_policy_comparison.json"
ACCEPTED_RESULT_SHA256 = "672be0348dd6f766db62e81dc2768b291ccd773a9089261c100b67a893d1bf08"
SOURCE_COMMIT = "bf51c46d39d3e7318fdeafe1f6ed020a4a45a92c"


def test_audit_reproduces_committed_artifact_without_simulation(monkeypatch: pytest.MonkeyPatch) -> None:
    from src.sim import simulation

    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("the source audit must not instantiate Simulation")

    monkeypatch.setattr(simulation.Simulation, "__init__", forbidden)
    def pinned_source(path: str) -> bytes:
        return subprocess.check_output(["git", "-C", str(ROOT), "show", f"{SOURCE_COMMIT}:{path}"])

    expected = json.loads(AUDIT.read_text(encoding="utf-8"))
    assert audit_repository(
        ROOT,
        accepted_source_commit=SOURCE_COMMIT,
        source_loader=pinned_source,
    ) == expected
    assert expected["generation"] == {"worlds": 0, "records": 0}


def test_current_source_still_has_role_only_credit() -> None:
    current = audit_repository(ROOT, accepted_source_commit="CURRENT_WORKTREE")
    assert current["findings"]["role_only_credit_confirmed"] is True
    assert current["implemented_credit_gate"]["checks_operating_mode"] is False


def test_role_only_credit_is_confirmed_but_physical_sensing_is_not() -> None:
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    assert audit["implemented_credit_gate"]["credited_roles"] == ["scout", "sensor"]
    assert audit["implemented_credit_gate"]["checks_operating_mode"] is False
    assert audit["findings"]["role_only_credit_confirmed"] is True
    assert audit["findings"]["operational_sensing_eligibility_demonstrated"] is False
    assert audit["confidence"]["internal"]["direction"] == "up"
    assert audit["confidence"]["external"]["direction"] == "unknown"


def test_region_identity_and_accepted_aggregate_do_not_supply_event_occupancy() -> None:
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    assert audit["region_identity"] == {
        "parameters": ["theta"],
        "directly_references_rotation_rate": False,
    }
    assert audit["accepted_result_event_fields"] == []
    assert audit["findings"]["event_level_occupancy_recoverable_from_accepted_result"] is False


def test_accepted_four_case_result_bytes_are_unchanged() -> None:
    assert hashlib.sha256(ACCEPTED_RESULT.read_bytes()).hexdigest() == ACCEPTED_RESULT_SHA256
