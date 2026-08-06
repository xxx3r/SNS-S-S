# August 2026 Backlog-Clearance Campaign

**Status:** Proposal-only until accepted by explicit human instruction or monthly governance  
**Tracking issue:** #38  
**Source snapshot:** `73225b9d09a43e0e3616250519ec908b7b723c14`  
**Companion inventory:** `docs/automation/august_2026_active_quest_inventory.md`

## 1. Purpose

Test whether a bounded, sequential cleanup campaign can increase the autonomous laboratory's information gain per run without weakening one-owner transactions, immutable receipts, scientific honesty, or monthly-governance authority.

The campaign removes only clerical and validation debris. It does not turn missing evidence, architecture choices, or unresolved scientific questions into administrative closure.

## 2. Frozen baseline

At the source snapshot immediately after merged PR #37:

- accepted `main`: `73225b9d09a43e0e3616250519ec908b7b723c14`;
- open implementation PRs: **0**;
- active quests: **8**;
- stale lifecycle records already identified: PR #22 and PR #23;
- missing lifecycle closure record already identified: PR #37;
- stale canonical next move age: approximately **3 days**, measured from merged PR #35 on August 3 to the August 6 snapshot;
- confirmed false environment blockers: **1**;
- confirmed pre-probe refusals: **1**;
- confirmed human recoveries caused by this incident: at least **1**, with exact counting deferred to the September audit;
- deterministic clerical or validation transactions proposed below: **6**;
- governance or approval handoffs proposed below: **2**.

Draft PR #39 is not included in the zero-open-PR baseline because it was created after the snapshot as the proposal vehicle.

## 3. Incident taxonomy

The August 6 event is a `FALSE_ENVIRONMENT_BLOCKER`, subclass `CONNECTOR_NOT_ATTEMPTED`.

| Class | Meaning | Required evidence | Allowed disposition |
|---|---|---|---|
| `FALSE_ENVIRONMENT_BLOCKER` | A blocker was emitted before the required connector probe | connector requirement, attempted flag, target, timestamp, and absence of provider failure | reject blocker and record recovery |
| `CONNECTOR_FAILURE` | A required connector operation was attempted and failed | connector, operation, target, timestamp, provider error | bounded retry or terminal blocker |
| `CONNECTOR_PERMISSION_FAILURE` | Provider returned deterministic authorization denial | permission context and provider response | stop without blind retry |
| `VALIDATION_FAILURE` | Artifact or record failed executable validation | check identity and concrete failure | `VERIFICATION_FAILED` |
| `MISSING_EVIDENCE` | Required scientific or operational evidence does not exist | named missing artifact or measurement | `BLOCKED_MISSING_EVIDENCE` |
| `GOVERNANCE_REQUIRED` | Next action changes queue, memory, beliefs, or authority | proposed mutation and owning authority | `NEEDS_GOVERNANCE_REVIEW` |

Generic prose such as “no live GitHub context” is never sufficient evidence for `BLOCKED_ENVIRONMENT`.

## 4. Connector-preflight design

Every connector-dependent run should record a preflight object before research or repository mutation:

```json
{
  "required_connector": "GitHub",
  "probe_operation": "get_repo",
  "probe_target": "xxx3r/SNS-S-S",
  "attempted": true,
  "succeeded": true,
  "attempted_at": "RFC3339 timestamp",
  "permission_snapshot": ["pull", "push", "maintain", "admin"],
  "error": null
}
```

A failed probe must preserve the provider-returned error:

```json
{
  "required_connector": "GitHub",
  "probe_operation": "get_repo",
  "probe_target": "xxx3r/SNS-S-S",
  "attempted": true,
  "succeeded": false,
  "attempted_at": "RFC3339 timestamp",
  "permission_snapshot": null,
  "error": {
    "code": "provider code",
    "message": "provider message"
  }
}
```

Semantic rules:

1. `BLOCKED_ENVIRONMENT` is invalid when a mandatory probe was not attempted.
2. A failed connector record must include connector, operation, target, timestamp, code, and message.
3. A successful probe must occur before research or mutation begins.
4. Missing local shell or clone is not evidence of missing GitHub authority.
5. One retry is allowed only for transient or ambiguous connector failures.
6. Permission denial, malformed target, and deterministic validation failure are not blindly retried.
7. Audit counters must count required, attempted, succeeded, failed, and pre-probe refusal states from structured fields.

Required regression fixtures:

- healthy GitHub connector plus unavailable local shell must probe and proceed;
- transient failed probe may retry once;
- deterministic permission denial must stop without blind retry;
- refusal before any probe must be rejected as an invalid blocker;
- valid connector-dependent receipt must expose preflight fields to audit metrics.

This design does not implement schema, validator, contract, or scheduled-prompt changes. Those require a separate reviewed implementation PR.

## 5. Authority and sequencing law

- Execute sequentially, never concurrently.
- Re-read accepted `main` after every merge.
- One bounded transaction has one current owner and exactly one new immutable receipt.
- Continue an existing valid owner before creating new work.
- Never create duplicate quest branches.
- Corrections create linked receipts; immutable records are never overwritten.
- Daily may update only its owned PR-lifecycle record.
- Monthly governance resolves stale, superseded, cross-PR, queue, belief, and canonical-memory state.
- System audit validates state but does not silently enact governance.
- Explicit human instructions may authorize a bounded exception, but the receipt must name the override and exact surface.

## 6. Sequential campaign queue

| Order | Transaction | Owner | Safe terminal outcome | Mandatory stop condition |
|---:|---|---|---|---|
| 1 | Create the missing terminal lifecycle record for merged PR #37, referencing merge commit `73225b9d...` and receipt `RUN-20260806T223500000000Z-daily-research-operator-a17c4e9b2d6f8031c5e7` | daily operator as the PR's existing owner, or explicit human | `DONE_WITH_LIMITATIONS` | schema conflict, missing receipt, or mismatch with live GitHub |
| 2 | Reconcile PR #22 from `draft_active` to its verified merged state | monthly governance or explicit human override | `DONE` | merge identity or ownership evidence is ambiguous |
| 3 | Reconcile PR #23 as closed and superseded by the accepted PR #34 recovery path | monthly governance or explicit human override | `DONE_WITH_LIMITATIONS` | supersession evidence is ambiguous |
| 4 | Produce a current open-PR and branch-ownership validation view without rewriting the historical July baseline | system audit | `DONE` | live connector state conflicts with repository records |
| 5 | Validate active queue IDs, README membership, cross-queue uniqueness, and no-duplicate-branch invariants | system audit | `DONE` or `VERIFICATION_FAILED` | duplicate ID, missing record, or mutation would be required |
| 6 | Validate recent receipt IDs, schema conformance, and referenced artifact existence | system audit | `DONE` or `VERIFICATION_FAILED` | missing artifact, duplicate receipt, or invalid immutable ID |
| 7 | Emit a proposal-only monthly handoff for the stale canonical next move; do not edit memory | monthly governance proposal | `NEEDS_GOVERNANCE_REVIEW` | request to rewrite memory without accepted authority |
| 8 | Decide whether the connector-preflight schema and validator implementation PR is authorized | human or monthly governance | `NEEDS_APPROVAL` or `NEEDS_GOVERNANCE_REVIEW` | implementation requested without authority |

The campaign may stop after transaction 6 when transactions 7 and 8 remain undecided. It never activates a new quest automatically.

## 7. Tomorrow bootstrap

The ordinary Daily Research Operator must not infer campaign activation from the existence of this draft alone.

Tomorrow's operator may select transaction 1 only when all of the following are true:

1. this plan is accepted and merged to `main`;
2. Issue #38 remains open and identifies the campaign as the active bounded handoff;
3. no newer monthly governance record supersedes the campaign;
4. no competing owner or implementation PR exists;
5. the operator probes GitHub successfully before claiming any blocker.

After transaction 1, the daily operator must not perform transactions 2 or 3 without monthly-governance authority or a new explicit human override. It may hand off to audit for transactions 4 through 6, but may not impersonate the audit loop.

If this plan remains draft, tomorrow's ordinary operator must treat it as a proposal only and follow accepted canonical state. Because `memory/mem_log_short.md` is currently stale, leaving the plan unaccepted creates a real risk of another low-information or duplicate selection.

## 8. Stop conditions

Stop and publish the current receipt when:

- a new measurement, model assumption, literature interpretation, or architecture choice is required;
- evidence is missing, contradictory, stale, or below the required package level;
- a queue, memory, belief, quest, or cross-PR ownership mutation needs monthly governance;
- validation fails or cannot be observed truthfully;
- the connector fails without a concrete provider error;
- a competing owner or duplicate branch appears;
- a contract, schema, scheduled prompt, or reserved authority would change;
- a human must choose between scientific routes.

The handoff must name the exact authority, unresolved question, evidence needed, and one next action.

## 9. September 1 scoreboard

Freeze the exact `main` commit at `2026-09-01T14:00:00Z` as `cutoff_commit`. Same-time, later, unresolved, or unmerged work is in-flight or excluded.

Track:

- connector-required runs;
- connector-attempt rate, target 100%;
- connector success rate by connector and loop;
- concrete-error completeness, target 100%;
- false environment blockers, target 0 after the baseline incident;
- pre-probe refusals, target 0;
- human recoveries and lost scheduled opportunities;
- blockers removed per run;
- receipt coverage, target 100%;
- one-owner compliance, target 100%;
- duplicate-work rate, target 0;
- validation pass rate, separating failure from not-run;
- stale-next-move age;
- PR turnaround median and outliers;
- human interventions per artifact;
- scientific-evidence fraction versus administrative movement;
- unauthorized quest activation, target 0;
- information inheritance between receipts;
- novelty and difficulty of post-campaign research.

Preserve denominators and exclusions. Administrative movement is not scientific progress.

## 10. Non-goals

This campaign does not:

- close, retire, reprioritize, or activate quests;
- rewrite consolidated beliefs or short memory;
- select a thermal architecture;
- transform missing evidence into a PASS;
- publish public scientific claims;
- modify unrelated repositories;
- implement connector-preflight code merely by accepting this plan;
- treat the absence of Drive files as missing repository evidence.

## 11. Acceptance criteria

The plan is accepted only when explicit human instruction or monthly governance confirms:

1. proposal-only boundary;
2. companion quest inventory and classifications;
3. exact transaction order and owner map;
4. connector-preflight design and fixtures;
5. September cutoff and scoreboard;
6. stop conditions and tomorrow bootstrap.

Acceptance authorizes only the bounded campaign transactions, not any scientific hypothesis or new research quest.