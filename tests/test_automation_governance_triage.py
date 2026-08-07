from __future__ import annotations

import copy

import pytest

from automation.authorizations import validate_governance_authorization
from automation.governance import validate_delegation_envelope
from automation.receipts import validate_run_receipt

DELEGATION_ID = "DELEG-20260807-HUMAN-FAST-TRIAGE-V1"
AUTHORIZATION_ID = "AUTH-20260807T180000000000Z-qst-stor-subexperiment-aaaaaaaaaaaaaaaaaaaa"


def delegation() -> dict[str, object]:
    return {
        "schema": "sns.governance-delegation.v1",
        "delegation_id": DELEGATION_ID,
        "period": "2026-08",
        "authority": "explicit-human",
        "authorized_loop": "daily-governance-triage",
        "allowed_action_types": ["refine_existing"],
        "allowed_quest_ids": ["QST-STOR-0002"],
        "authorized_implementation_surfaces": ["src/**", "experiments/**", "configs/**", "tests/**", "outputs/**"],
        "forbidden_surfaces": ["automation/**", "calendar/**", "memory/**", "quests/**", ".github/**"],
        "max_authorizations_per_run": 4,
        "max_pull_requests_per_authorization": 1,
        "max_run_receipts_per_authorization": 1,
        "required_checks": [
            "python -m pytest -q tests/test_automation_*.py",
            "python -m automation.cli validate-repository",
        ],
        "recorded_at": "2026-08-07T17:34:44Z",
        "expires_at": "2026-09-01T14:00:00Z",
        "rationale": "Bounded August fast-governance experiment.",
    }


def authorization() -> dict[str, object]:
    return {
        "schema": "sns.governance-authorization.v1",
        "authorization_id": AUTHORIZATION_ID,
        "issued_by_loop": "daily-governance-triage",
        "action_type": "refine_existing",
        "quest_id": "QST-STOR-0002",
        "recorded_at": "2026-08-07T18:00:00Z",
        "authorization": {
            "delegation_id": DELEGATION_ID,
            "authorized_loop": "daily-research-operator",
            "acceptance_slice": "Freeze one tiny synthetic thermal-world experiment under the active storage quest.",
            "source_commit": "0" * 40,
            "expires_at": "2026-08-08T18:00:00Z",
            "allowed_write_surfaces": ["experiments/**", "configs/**", "tests/**", "outputs/**"],
            "budgets": {"max_worlds": 8, "max_retries": 1},
            "max_pull_requests": 1,
            "max_run_receipts": 1,
            "mandatory_checks": [
                "python -m pytest -q tests/test_automation_*.py",
                "python -m automation.cli validate-repository",
            ],
            "stop_conditions": [
                "missing evidence",
                "scientific route choice",
                "failed validation",
                "ownership conflict",
            ],
            "next_action": "Implement the first bounded experiment artifact without changing quest governance.",
        },
    }


def test_valid_fast_governance_authorization() -> None:
    envelope = delegation()
    record = authorization()
    validate_delegation_envelope(envelope)
    validate_governance_authorization(
        record,
        delegations={DELEGATION_ID: envelope},
        active_ids={"QST-STOR-0002"},
    )


def test_triage_cannot_authorize_new_quest() -> None:
    envelope = delegation()
    record = authorization()
    record["action_type"] = "propose_new"
    with pytest.raises(ValueError, match="refine_existing"):
        validate_governance_authorization(
            record,
            delegations={DELEGATION_ID: envelope},
            active_ids={"QST-STOR-0002"},
        )


def test_delegation_rejects_protected_implementation_surface() -> None:
    envelope = delegation()
    envelope["authorized_implementation_surfaces"] = ["memory/**"]
    with pytest.raises(ValueError, match="protected"):
        validate_delegation_envelope(envelope)


def test_authorization_must_be_source_bound_and_unexpired() -> None:
    envelope = delegation()
    bad_source = authorization()
    bad_source["authorization"]["source_commit"] = "not-a-sha"  # type: ignore[index]
    with pytest.raises(ValueError, match="source_commit"):
        validate_governance_authorization(
            bad_source,
            delegations={DELEGATION_ID: envelope},
            active_ids={"QST-STOR-0002"},
        )

    expired = authorization()
    expired["authorization"]["expires_at"] = "2026-08-07T17:59:59Z"  # type: ignore[index]
    with pytest.raises(ValueError, match="expiry"):
        validate_governance_authorization(
            expired,
            delegations={DELEGATION_ID: envelope},
            active_ids={"QST-STOR-0002"},
        )


def test_triage_receipt_is_a_canonical_loop_receipt() -> None:
    receipt = {
        "schema": "sns.loop-run.v1",
        "run_id": "RUN-20260807T180000000000Z-daily-governance-triage-bbbbbbbbbbbbbbbbbbbb",
        "loop_id": "daily-governance-triage",
        "contract_version": "1.0.0",
        "trigger": "scheduled",
        "trigger_time": "2026-08-07T18:00:00Z",
        "source_commit": "0" * 40,
        "state_hash": "sha256:" + "c" * 64,
        "quest_context": {"quest_id": "QST-STOR-0002"},
        "pr_context": {},
        "consumed_ids": [DELEGATION_ID],
        "artifacts": [f"automation/authorizations/2026/08/{AUTHORIZATION_ID}.json"],
        "checks": [{"name": "authorization validation", "status": "passed", "evidence": "validator"}],
        "belief_effects": [],
        "terminal_state": "DONE",
        "next_action": "Daily Research Operator consumes the bounded authorization.",
        "created_at": "2026-08-07T18:01:00Z",
    }
    validate_run_receipt(receipt)
