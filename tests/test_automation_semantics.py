from __future__ import annotations

from datetime import datetime, timezone

import pytest

from automation.ids import new_event_id, new_run_id
from automation.semantics import cluster_evidence_events, consolidate_belief_events, validate_pr_lifecycle, validate_quest_action

NOW = datetime(2026, 7, 15, tzinfo=timezone.utc)


def eid(prefix: str, namespace: str, token: str) -> str:
    return new_event_id(prefix, namespace, now=NOW, token_factory=lambda _: token * 20)


def evidence(evidence_id: str, cluster_id: str, fingerprint: str, independence: str) -> dict:
    return {
        "schema": "sns.evidence-event.v1",
        "evidence_id": evidence_id,
        "claim_cluster_id": cluster_id,
        "claim": "A demonstration occurred.",
        "source_uri": "https://example.invalid/source",
        "source_kind": "primary_report",
        "source_fingerprint": "sha256:" + fingerprint * 64,
        "observed_at": "2026-07-15T00:00:00Z",
        "independence": independence,
        "polarity": "supports",
        "confidence": 0.8,
        "provenance": {"retrieved_by": "weekly-evidence-synthesis"},
    }


def test_five_reports_of_one_event_form_one_cluster() -> None:
    cluster_id = eid("CLM", "demo", "a")
    events = [evidence(eid("EVID", f"source-{index}", str(index)), cluster_id, str(index), "shared_origin") for index in range(5)]
    clusters = cluster_evidence_events(events)
    assert len(clusters) == 1
    assert clusters[cluster_id]["source_count"] == 5
    assert clusters[cluster_id]["independent_source_count"] == 0


def test_belief_consolidation_preserves_raw_event_links() -> None:
    evidence_id = eid("EVID", "source", "b")
    first = {
        "schema": "sns.belief-event.v1",
        "belief_event_id": eid("BEL", "storage", "c"),
        "belief_key": "STOR.shadow_survival",
        "evidence_ids": [evidence_id],
        "magnitude": -0.4,
        "confidence": 0.75,
        "effect": "weaken",
        "rationale": "Geometry-derived thermal inertia is lower than assumed.",
        "recorded_at": "2026-07-15T00:00:00Z",
    }
    consolidated = consolidate_belief_events([first], evidence_ids={evidence_id})
    assert consolidated["STOR.shadow_survival"]["belief_event_ids"] == [first["belief_event_id"]]


def test_weekly_loop_cannot_enact_queue_governance() -> None:
    action = {
        "schema": "sns.quest-action.v1",
        "quest_action_id": eid("QA", "refine", "d"),
        "action_type": "refine_existing",
        "quest_id": "QST-STOR-0002",
        "target_quest_ids": [],
        "proposed_by_loop": "weekly-evidence-synthesis",
        "authority": "enacted",
        "rationale": "New evidence changes the sweep.",
        "recorded_at": "2026-07-15T00:00:00Z",
    }
    with pytest.raises(ValueError, match="may propose"):
        validate_quest_action(action, active_ids={"QST-STOR-0002"}, completed_ids=set(), proposed_ids=set(), blocked_ids=set())


def test_refinement_cannot_be_disguised_as_new_duplicate_quest() -> None:
    action = {
        "schema": "sns.quest-action.v1",
        "quest_action_id": eid("QA", "new", "e"),
        "action_type": "propose_new",
        "quest_id": "QST-STOR-0002",
        "target_quest_ids": [],
        "proposed_by_loop": "weekly-evidence-synthesis",
        "authority": "proposal",
        "rationale": "Duplicate proposal.",
        "recorded_at": "2026-07-15T00:00:00Z",
    }
    with pytest.raises(ValueError, match="reuses existing"):
        validate_quest_action(action, active_ids={"QST-STOR-0002"}, completed_ids=set(), proposed_ids=set(), blocked_ids=set())


def test_pr_lifecycle_requires_terminal_vocabulary() -> None:
    record = {
        "schema": "sns.pr-lifecycle.v1",
        "pr_number": 20,
        "quest_id": "QST-STOR-0001",
        "acceptance_slice": "repair generated summary drift",
        "state": "haunting_the_branch",
        "owner_run_id": new_run_id("daily-research-operator", now=NOW, token_factory=lambda _: "f" * 20),
        "source_commit": "a" * 40,
        "head_commit": "b" * 40,
        "updated_at": "2026-07-15T00:00:00Z",
        "next_review_after": "2026-07-16T00:00:00Z",
        "supersedes": [],
    }
    with pytest.raises(ValueError, match="lifecycle"):
        validate_pr_lifecycle(record)
