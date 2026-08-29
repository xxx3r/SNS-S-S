# SNS Autonomous Loop Schema Reconciliation

**Status:** Canonical compatibility authority  
**Originally established:** 2026-07-20  
**Current receipt boundary:** 2026-08-29  
**Scope:** Automation record identity, field vocabulary, and receipt-provenance compatibility only

## Authority

The executable transaction layer is the canonical authority for automation record shape.

Use this order:

1. `automation/schemas/*.schema.json` for machine-readable structure;
2. the matching validator in `automation/` for semantic invariants;
3. `AGENTS.md` stable law;
4. the selected active loop contract for role authority and behavior;
5. this reconciliation note and `automation/README.md` for compatibility guidance;
6. older plans/examples only as historical design context.

This reconciliation changes no scientific conclusion, quest priority, ARCI weight, active queue, or hardware-readiness boundary.

## Canonical identity

Immutable automation IDs use the repository helpers in `automation.ids` and the accepted uppercase dialect:

```text
RUN-YYYYMMDDTHHMMSSffffffZ-namespace-20hex
EVID-YYYYMMDDTHHMMSSffffffZ-namespace-20hex
CLM-YYYYMMDDTHHMMSSffffffZ-namespace-20hex
BEL-YYYYMMDDTHHMMSSffffffZ-namespace-20hex
QA-YYYYMMDDTHHMMSSffffffZ-namespace-20hex
AUTH-...
DELEG-...
```

Lower-case historical examples such as `run_*`, `ev_*`, `be_*`, and `qa_*` are non-normative.

## Run-receipt compatibility boundary

### Accepted history: `sns.loop-run.v1`

All already-published v1 receipts remain immutable replay evidence. v1 required an opaque `state_hash` field. Historical v1 records are not rewritten merely because later governance discovered that many connector-authored runs used SHA-256(empty) as a placeholder rather than a captured state snapshot.

The August 2026 PR #55 review demonstrated why this was insufficient: a schema-valid placeholder digest did not prove which governance, delegation, quest, contract, memory, or PR-ownership state the run had actually observed. That is a control-plane provenance defect, not a change to the underlying scientific result.

### New records: `sns.loop-run.v2`

New loop receipts use `sns.loop-run.v2` and replace opaque state-hash claims with an inspectable `sns.state-snapshot.v1` object.

A v2 receipt contains the ordinary run fields plus:

```json
{
  "schema": "sns.loop-run.v2",
  "receipt_kind": "run",
  "state_snapshot": {
    "schema": "sns.state-snapshot.v1",
    "source_commit": "<40-hex accepted-main SHA>",
    "records": [
      {"role": "stable_law", "path": "AGENTS.md", "git_blob_sha": "<40-hex blob SHA>"},
      {"role": "active_contract", "path": "automation/contracts/<selected-active-contract>.md", "git_blob_sha": "<40-hex blob SHA>"},
      {"role": "state_ownership", "path": "automation/state_ownership.json", "git_blob_sha": "<40-hex blob SHA>"},
      {"role": "active_quest_index", "path": "quests/active/README.md", "git_blob_sha": "<40-hex blob SHA>"},
      {"role": "research_graph", "path": "quests/research_graph.json", "git_blob_sha": "<40-hex blob SHA>"},
      {"role": "runtime_manifest", "path": "automation/runtime_manifest.json", "git_blob_sha": "<40-hex blob SHA>"},
      {"role": "canonical_memory", "path": "memory/mem_log_short.md", "git_blob_sha": "<40-hex blob SHA>"}
    ],
    "open_prs": [
      {"number": 55, "head_sha": "<40-hex head SHA>", "draft": true, "state": "open"}
    ],
    "fingerprint": "sha256:<derivative digest of the canonical snapshot object>"
  }
}
```

The exact record list is inspectable and connector-friendly. A GitHub file read returns the blob SHA directly, so a scheduled agent does not need a local clone or shell to invent or compute a state digest. The fingerprint is a convenience integrity check over the explicit snapshot object; it is not a substitute for the component identities.

`automation.provenance.snapshot_from_connector_records()` defines the connector representation. `build_state_snapshot()` defines the equivalent local-checkout reference implementation. Both converge on the same state-snapshot schema.

## Append-only correction law

Published receipts are never edited. A provenance or record-shape repair is a new v2 receipt:

```json
{
  "schema": "sns.loop-run.v2",
  "receipt_kind": "correction",
  "correction_of": "RUN-..."
}
```

A correction may repair provenance, missing required metadata, or another control-plane defect. It may not introduce a new scientific experiment, result, belief effect, queue mutation, or weakened evaluator under cover of correction.

A correction receipt is non-consuming with respect to an authorization's scientific implementation-receipt budget. `automation.provenance.implementation_receipts_for_authorization()` counts the original implementation run but excludes v2 `receipt_kind: correction` records. This resolves the previous conflict between immutable history and authorizations that permit exactly one scientific implementation receipt.

## Weekly evidence records

The existing evidence/belief/quest-action dialect remains current:

- `sns.evidence-event.v1` for immutable evidence events;
- `sns.belief-event.v1` for raw belief proposals/events;
- `sns.quest-action.v1` for semantic quest-action proposals.

Source title, publication date, directness, novelty, environment match, fact/inference/speculation separation, and limitations belong in evidence provenance unless a future versioned schema promotes them. Belief magnitude and confidence remain separate. Weekly may propose governance effects; Monthly owns consolidated governance state.

## Graph and orchestration records

Two new machine-readable organization records are part of the executable control plane:

- `quests/research_graph.json` uses `sns.research-graph.v1`. Only `requires` edges impose hard execution dependencies; that subgraph must be acyclic. Other lineage edges may cycle.
- `automation/runtime_manifest.json` uses `sns.runtime-manifest.v1` and declares desired scheduler state. `automation.orchestration.compare_runtime_manifest()` reports drift against a normalized live task snapshot.

Neither record changes scientific truth merely by existing. Queue membership/priority remain monthly-owned, and live external scheduler state remains a platform fact that must be observed rather than invented.

## Publication gate

Before opening or updating an automation-created PR:

```bash
python -m pytest -q tests/test_automation_*.py
python -m automation.cli validate-repository
```

A run must not describe manual comparison with a prose example as schema validation. Hosted or local execution must validate against the executable repository.

If validation fails, fail closed or correct only still-unmerged records. Never rewrite an accepted immutable record; publish a linked correction under the law above.

## Historical diagnosis preserved

The July 19 weekly failure was a record-dialect compatibility defect: the agent followed lower-case examples from an older planning document while the executable repository expected the uppercase accepted schema. The August 27–28 PR #55 provenance failure was the next-generation version of the same lesson: a field can be syntactically valid while semantically empty.

The durable rule is therefore:

> Prompts choose a loop. Repository code defines the record. Inspectable provenance proves the state. Hosted validation decides whether the transaction is admissible.
