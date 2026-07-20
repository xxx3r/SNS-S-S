from __future__ import annotations

import pytest

from automation.receipts import validate_run_receipt
from automation.semantics import (
    cluster_evidence_events,
    consolidate_belief_events,
    validate_quest_action,
)

EVIDENCE_ID = "EVID-20260719T145804000000Z-space-weather-margin-a1111111111111111111"
CLUSTER_ID = "CLM-20260719T145804000000Z-space-weather-margin-b2222222222222222222"
BELIEF_ID = "BEL-20260719T145804000000Z-environmental-margin-c3333333333333333333"
QUEST_ACTION_ID = "QA-20260719T145804000000Z-refine-qst-stor-0002-d4444444444444444444"
RUN_ID = "RUN-20260719T145804000000Z-weekly-evidence-synthesis-e5555555555555555555"


def canonical_evidence() -> dict[str, object]:
    return {
        "schema": "sns.evidence-event.v1",
        "evidence_id": EVIDENCE_ID,
        "claim_cluster_id": CLUSTER_ID,
        "claim": "Extreme solar-wind forcing may require wider environmental uncertainty margins.",
        "source_uri": "https://science.nasa.gov/example",
        "source_kind": "official_statement",
        "source_fingerprint": "sha256:" + "a" * 64,
        "observed_at": "2026-07-19T14:58:04Z",
        "independence": "independent",
        "polarity": "context_only",
        "confidence": 0.62,
        "provenance": {
            "retrieved_by": "weekly-evidence-synthesis",
            "publication_date": "2026-07-15",
            "environment": "near-Earth-space",
            "limitations": ["Not a component degradation measurement."],
        },
        "artifacts": ["calendar/roundups/2026-07-19.md"],
    }


def canonical_belief() -> dict[str, object]:
    return {
        "schema": "sns.belief-event.v1",
        "belief_event_id": BELIEF_ID,
        "belief_key": "STOR.environmental_margin",
        "evidence_ids": [EVIDENCE_ID],
        "magnitude": 0.2,
        "confidence": 0.62,
        "effect": "uncertainty_increase",
        "rationale": "The source increases uncertainty about assuming a hard upper bound on environmental forcing.",
        "recorded_at": "2026-07-19T15:10:00Z",
    }


def canonical_quest_action() -> dict[str, object]:
    return {
        "schema": "sns.quest-action.v1",
        "quest_action_id": QUEST_ACTION_ID,
        "action_type": "refine_existing",
        "quest_id": "QST-STOR-0002",
        "target_quest_ids": [],
        "proposed_by_loop": "weekly-evidence-synthesis",
        "authority": "proposal",
        "rationale": "Add environmental degradation margins to the material/interface evidence checklist.",
        "recorded_at": "2026-07-19T15:12:00Z",
    }


def canonical_receipt() -> dict[str, object]:
    return {
        "schema": "sns.loop-run.v1",
        "run_id": RUN_ID,
        "loop_id": "weekly-evidence-synthesis",
        "contract_version": "1.0.0",
        "trigger": "scheduled",
        "trigger_time": "2026-07-19T14:58:04Z",
        "source_commit": "25318716f1778f10a405273b4bd13c1d0b4dc419",
        "state_hash": "sha256:" + "b" * 64,
        "quest_context": {
            "quest_id": "QST-STOR-0002",
            "related_quest_ids": ["QST-SIM-0002", "QST-SIM-0003"],
        },
        "pr_context": {"pr_number": 28, "lifecycle_state": "ready_for_review"},
        "consumed_ids": [],
        "artifacts": ["calendar/roundups/2026-07-19.md"],
        "checks": [
            {
                "name": "repository semantic validation",
                "status": "passed",
                "evidence": "python -m automation.cli validate-repository",
            }
        ],
        "belief_effects": [BELIEF_ID],
        "terminal_state": "DONE_WITH_LIMITATIONS",
        "next_action": "Continue QST-STOR-0002 after human review.",
        "created_at": "2026-07-19T15:19:00Z",
    }


def test_canonical_weekly_record_bundle_validates() -> None:
    evidence = canonical_evidence()
    belief = canonical_belief()
    action = canonical_quest_action()
    receipt = canonical_receipt()

    clusters = cluster_evidence_events([evidence])
    consolidated = consolidate_belief_events([belief], evidence_ids={EVIDENCE_ID})
    validate_quest_action(
        action,
        active_ids={"QST-STOR-0002"},
        completed_ids=set(),
        proposed_ids=set(),
        blocked_ids=set(),
    )
    validate_run_receipt(receipt)

    assert clusters[CLUSTER_ID]["evidence_ids"] == [EVIDENCE_ID]
    assert consolidated["STOR.environmental_margin"]["belief_event_ids"] == [BELIEF_ID]


def test_historical_lowercase_weekly_dialect_is_not_canonical() -> None:
    receipt = canonical_receipt()
    receipt["run_id"] = "run_weekly_20260719T145804Z_c3a91e"
    with pytest.raises(ValueError, match="invalid immutable identifier"):
        validate_run_receipt(receipt)

    evidence = canonical_evidence()
    evidence["evidence_id"] = "ev_20260719_space_weather_margin"
    with pytest.raises(ValueError, match="invalid immutable identifier"):
        cluster_evidence_events([evidence])
