# SNS Autonomous Loop Schema Reconciliation

**Status:** Canonical compatibility authority  
**Date:** 2026-07-20  
**Scope:** Automation record identity and field vocabulary only

## Decision

The executable transaction layer is the canonical authority for automation record shape.

For run receipts, evidence events, belief events, quest actions, and PR lifecycle records, use this order:

1. `automation/schemas/*.schema.json` for machine-readable structure;
2. the matching validator in `automation/` for semantic invariants;
3. the active loop contract in `automation/contracts/` for authority and behavior;
4. this reconciliation note and `automation/README.md` for copyable guidance;
5. older planning examples only as historical design context.

The examples in `docs/SNS_autonomous_loop_transaction_plan.md` that use lower-case identifiers such as `run_*`, `ev_*`, `be_*`, or `qa_*`, or use superseded field names, are non-normative. They describe the design intent that preceded the accepted implementation in PR #26. They must not be copied into new records.

This reconciliation changes no scientific conclusion, quest priority, ARCI weight, active queue, or hardware-readiness boundary.

## Canonical identity

All immutable automation IDs are generated through `automation.ids.new_event_id` or `automation.ids.new_run_id`.

```text
RUN-YYYYMMDDTHHMMSSffffffZ-namespace-20hex
EVID-YYYYMMDDTHHMMSSffffffZ-namespace-20hex
CLM-YYYYMMDDTHHMMSSffffffZ-namespace-20hex
BEL-YYYYMMDDTHHMMSSffffffZ-namespace-20hex
QA-YYYYMMDDTHHMMSSffffffZ-namespace-20hex
```

Do not invent sequential IDs, lower-case aliases, or shortened suffixes.

## Canonical weekly evidence records

### Evidence event

```json
{
  "schema": "sns.evidence-event.v1",
  "evidence_id": "EVID-20260719T145804000000Z-space-weather-margin-a1111111111111111111",
  "claim_cluster_id": "CLM-20260719T145804000000Z-space-weather-margin-b2222222222222222222",
  "claim": "Extreme solar-wind forcing may require wider environmental uncertainty margins.",
  "source_uri": "https://science.nasa.gov/example",
  "source_kind": "official_statement",
  "source_fingerprint": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "observed_at": "2026-07-19T14:58:04Z",
  "independence": "independent",
  "polarity": "context_only",
  "confidence": 0.62,
  "provenance": {
    "retrieved_by": "weekly-evidence-synthesis",
    "publication_date": "2026-07-15",
    "environment": "near-Earth-space",
    "limitations": ["Not a component degradation measurement."]
  },
  "artifacts": ["calendar/roundups/2026-07-19.md"]
}
```

Source title, publication date, directness, novelty, environment match, fact/inference/speculation separation, and limitations remain valuable. Store them inside `provenance` unless and until a versioned schema explicitly promotes them to top-level fields.

### Belief event

```json
{
  "schema": "sns.belief-event.v1",
  "belief_event_id": "BEL-20260719T145804000000Z-environmental-margin-c3333333333333333333",
  "belief_key": "STOR.environmental_margin",
  "evidence_ids": [
    "EVID-20260719T145804000000Z-space-weather-margin-a1111111111111111111"
  ],
  "magnitude": 0.2,
  "confidence": 0.62,
  "effect": "uncertainty_increase",
  "rationale": "The source increases uncertainty about assuming a hard upper bound on environmental forcing.",
  "recorded_at": "2026-07-19T15:10:00Z"
}
```

Magnitude and confidence remain separate. Weekly evidence proposes immutable raw events; monthly governance owns consolidation.

### Quest action

```json
{
  "schema": "sns.quest-action.v1",
  "quest_action_id": "QA-20260719T145804000000Z-refine-qst-stor-0002-d4444444444444444444",
  "action_type": "refine_existing",
  "quest_id": "QST-STOR-0002",
  "target_quest_ids": [],
  "proposed_by_loop": "weekly-evidence-synthesis",
  "authority": "proposal",
  "rationale": "Add vacuum, radiation, contamination, and thermal-cycling margins to the planned material/interface evidence checklist.",
  "recorded_at": "2026-07-19T15:12:00Z"
}
```

Artifact targets, dependencies, success metrics, evidence links, and proposed priority effects belong in `rationale` or a separate human-readable roundup until a versioned quest-action schema adds explicit fields.

### Run receipt

```json
{
  "schema": "sns.loop-run.v1",
  "run_id": "RUN-20260719T145804000000Z-weekly-evidence-synthesis-e5555555555555555555",
  "loop_id": "weekly-evidence-synthesis",
  "contract_version": "1.0.0",
  "trigger": "scheduled",
  "trigger_time": "2026-07-19T14:58:04Z",
  "source_commit": "25318716f1778f10a405273b4bd13c1d0b4dc419",
  "state_hash": "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
  "quest_context": {
    "quest_id": "QST-STOR-0002",
    "related_quest_ids": ["QST-SIM-0002", "QST-SIM-0003"],
    "question": "What recent evidence creates bounded refinements without displacing QST-STOR-0002?"
  },
  "pr_context": {
    "pr_number": 28,
    "lifecycle_state": "ready_for_review"
  },
  "consumed_ids": [],
  "artifacts": [
    "calendar/roundups/2026-07-19.md",
    "calendar/evidence/2026/07/EVID-20260719T145804000000Z-space-weather-margin-a1111111111111111111.json"
  ],
  "checks": [
    {
      "name": "repository semantic validation",
      "status": "passed",
      "evidence": "python -m automation.cli validate-repository"
    },
    {
      "name": "GitHub Actions",
      "status": "not_run",
      "evidence": ""
    }
  ],
  "belief_effects": [
    "BEL-20260719T145804000000Z-environmental-margin-c3333333333333333333"
  ],
  "terminal_state": "DONE_WITH_LIMITATIONS",
  "next_action": "Continue QST-STOR-0002 with the material/interface evidence checklist after human review.",
  "created_at": "2026-07-19T15:19:00Z"
}
```

## Publication gate

Before opening or updating an automation-created PR:

```bash
python -m pytest -q tests/test_automation_*.py
python -m automation.cli validate-repository
```

A weekly run must not describe manual comparison with an obsolete planning example as schema validation. It must validate against the executable repository contracts.

If validation fails, publish only as `VERIFICATION_FAILED` or keep the branch unpublished while correcting the new, still-unmerged records. Never rewrite a record that has already merged; use a linked correction event instead.

## July 19 diagnosis

The July 19 weekly agent followed the lower-case examples in the planning document. The accepted implementation expected the executable dialect above. The transaction workflow therefore failed closed during repository validation while ordinary tests and baseline artifacts remained green.

That failure is treated as a control-plane compatibility defect, not a scientific failure. The July 19 draft records should be converted before merge, and the regression suite must preserve this exact boundary for future weekly runs.
