# SNS Autonomous Loop Transaction Plan

**Status:** Proposed implementation authority  
**Date:** 2026-07-14  
**Repository:** `xxx3r/SNS-S-S`  
**Tracking issue:** [#24 Harden SNS autonomous research loops with transactional state and versioned contracts](https://github.com/xxx3r/SNS-S-S/issues/24)  
**Planning branch:** `agent/sns-loop-transaction-plan`  

---

## 0. Executive decision

SNS-S-S should preserve its scientific control plane and substantially strengthen its automation boundary.

The repository already has the essential properties of a credible autonomous research instrument:

- a narrow mission boundary;
- explicit distinction between research software and flight readiness;
- artifact-first quests;
- falsifiers and measurable acceptance criteria;
- bounded active work;
- compact spawn memory;
- evidence-aware AURORA scoring;
- daily implementation, weekly evidence, monthly governance, and scheduled audit loops;
- branch and pull-request discipline;
- truthful verification and scientific uncertainty language.

The remaining failure mode is not insufficient instruction. It is concurrent mutation of shared research state by multiple competent agents operating on different clocks.

The target system is therefore a transactional, multi-timescale research loop architecture:

```text
scheduled trigger
  -> versioned loop contract
  -> immutable state snapshot
  -> ownership and conflict check
  -> bounded scientific action
  -> evidence and artifact production
  -> verification
  -> terminal state
  -> immutable run receipt
  -> authorized state transition
  -> later-loop consumption
```

The system should make it impossible for two sensible loops to silently:

- allocate the same run identity;
- append incompatible entries to one shared log;
- create duplicate quests;
- overwrite the canonical next move;
- count repeated reporting as independent evidence;
- leave conflicting branches without a lifecycle state;
- produce work whose originating contract cannot be reconstructed;
- claim learning without showing which later decision consumed the earlier result.

---

## 1. Scope

This plan governs the repository infrastructure that coordinates scheduled autonomous research.

It covers:

1. `AGENTS.md` routing and authority;
2. repository-local loop contracts;
3. daily, weekly, monthly, and audit loop ownership;
4. immutable run receipts;
5. memory and state reconciliation;
6. quest actions and queue governance;
7. evidence and belief events;
8. branch and pull-request lifecycle;
9. optimistic concurrency and conflict handling;
10. automated validation;
11. September audit observability;
12. staged migration and representative-task evaluation.

It does not authorize changes to:

- core SNS physics assumptions;
- thermal/storage model conclusions;
- ARCI weights;
- mission architecture;
- swarm control algorithms;
- hardware-readiness claims;
- dependencies, security, or CI policy except where required to validate the loop infrastructure.

Those remain separate scientific or engineering decisions.

---

## 2. Current operating organism

SNS-S-S currently runs on four coupled scientific loops.

### 2.1 Physical loop

```text
solar input
  -> conversion
  -> storage
  -> control
  -> useful load / relay / sensing
  -> thermal and electrical losses
```

### 2.2 Swarm loop

```text
local state
  -> communication
  -> distributed allocation
  -> maneuver / sensing / relay action
  -> changed local and network state
```

### 2.3 Confidence loop

```text
measurement
  -> uncertainty model
  -> confidence update
  -> decision threshold
  -> further observation or action
```

### 2.4 Research loop

```text
literature or experiment
  -> evidence event
  -> belief effect
  -> quest decision
  -> artifact
  -> verification
  -> revised model and next move
```

The scheduled automation suite adds four clocks.

### 2.5 Daily research operator

Current cadence: Monday through Saturday.

Primary role:

- execute one smallest high-value unblocked quest slice;
- continue the active implementation PR when appropriate;
- produce a concrete artifact;
- run relevant checks;
- record limitations and the next step.

### 2.6 Weekly evidence synthesis

Current cadence: Sunday morning.

Primary role:

- search current primary evidence;
- create a dated roundup;
- identify evidence clusters and belief effects;
- propose quest refinements or new testable gaps;
- avoid duplicate quests;
- report what became more or less plausible.

### 2.7 Monthly governance synthesis

Current cadence: first Sunday of each month.

Primary role:

- synthesize completed weekly evidence;
- reconcile the belief system;
- close, archive, merge, or reprioritize quests;
- define no more than three monthly objectives;
- set one authoritative next canonical move.

### 2.8 System audit

Current planned trigger: 2026-09-01.

Primary role:

- evaluate the research organism rather than advance an ordinary quest;
- measure duplication, drift, artifact quality, throughput, information inheritance, governance failure, and useful wrongness;
- recommend the next automation architecture;
- never silently change the active automation suite.

---

## 3. Current strengths to preserve

The migration must not damage the following.

### 3.1 Mission honesty

SNS-S-S is a research instrument, not flight software.

Agents must continue to separate:

- demonstrated facts;
- model results;
- engineering inference;
- speculative architecture;
- hardware-readiness claims.

### 3.2 Engineering invariants

Preserve:

- explicit units;
- energy accounting and curtailment;
- configurable scenarios;
- score/confidence separation;
- intentional compatibility behavior;
- tests for new code or data logic;
- explicit assumptions and uncertainty;
- no conversion of preliminary modeling into hardware claims.

### 3.3 Artifact-first quests

Every active quest should continue to define:

- hypothesis or engineering question;
- acceptance criteria;
- required artifact;
- relevant verification;
- falsifier or invalidating evidence;
- bounded next step.

### 3.4 Bounded active queue

Keep the active quest queue intentionally small.

Recommended target:

- minimum: 1 active quest;
- ordinary range: 3 to 5 active quests;
- hard ceiling: 8 without explicit monthly governance justification.

### 3.5 AURORA evidence gate

AURORA should continue to reward:

- runnable work over prose-only motion;
- tested and reproducible work over unverified changes;
- explicit uncertainty over false certainty;
- evidence that changes later decisions;
- informative failure and falsification.

AURORA should not become the transaction engine. It remains a scoring and reflection layer.

---

## 4. Failure model

The design should assume that every individual agent is competent and locally compliant.

The dangerous failures are compositional.

### 4.1 Identity collision

Two branches start from the same `main` state and allocate the same sequential session ID.

Result:

- duplicate IDs;
- ambiguous chronology;
- merge conflict or silent overwrite;
- audit cannot uniquely address a run.

### 4.2 Shared-log collision

Daily and weekly loops both append to the same Markdown memory file.

Result:

- conflicts unrelated to scientific work;
- logging-only diffs;
- rebases that reorder or lose entries;
- pressure to merge mutable history instead of immutable facts.

### 4.3 Governance collision

Weekly evidence and monthly synthesis both mutate:

- active quest definitions;
- queue order;
- `next_canonical_move`;
- short memory;
- belief summaries.

Result:

- multiple authorities;
- priority oscillation;
- an implementation loop follows stale governance;
- a weekly evidence loop silently overrules monthly strategy.

### 4.4 Duplicate quest creation

A weekly action references an existing quest ID but changes its title or scope.

Result:

- tooling cannot distinguish refinement from creation;
- duplicate or contradictory active quests;
- two PRs claim the same conceptual work.

### 4.5 Evidence double counting

Several sources report the same underlying demonstration.

Result:

- one event appears as several independent belief updates;
- monthly synthesis overweights media density;
- confidence rises without independent replication.

### 4.6 Contract invisibility

The operative daily or weekly prompt changes in the platform layer but no repository artifact records the change.

Result:

- the audit cannot reconstruct behavior;
- two runs with the same loop name follow different rules;
- apparent drift cannot be assigned to model, prompt, repository state, or evidence.

### 4.7 Branch ghosting

A draft PR remains open after its hypothesis, base branch, or quest has been superseded.

Result:

- future operators repeatedly inspect stale work;
- duplicate branches form;
- unmergeable work appears active;
- no terminal reason exists.

### 4.8 Infinite draft continuation

One implementation PR absorbs successive hypotheses and validation regimes.

Result:

- the acceptance slice expands indefinitely;
- review becomes difficult;
- the loop cannot determine when the original outcome is complete;
- rollback boundaries become unclear.

### 4.9 Observer collision

The September audit runs near an ordinary daily operator trigger.

Result:

- audit metrics include in-flight work inconsistently;
- an unfinished branch is treated as abandoned or completed;
- the observer changes the state it is measuring.

---

## 5. Architectural principles

### 5.1 Stable law belongs in `AGENTS.md`

`AGENTS.md` should contain:

- repository mission boundary;
- hard scientific and engineering invariants;
- authority ordering;
- loop routing;
- mutation and approval boundaries;
- verification expectations;
- terminal-state vocabulary;
- pointers to versioned contracts.

It should not contain:

- chronological run history;
- the full platform schedule;
- current quest details;
- long duplicated task procedures;
- model-version-specific prompt tricks.

### 5.2 Behavior contracts belong in Git

Each scheduled loop must reference a versioned repository contract.

The platform schedule remains outside the repository.

The contract defines:

- trigger class;
- goal;
- required inputs;
- optional inputs;
- read and write permissions;
- artifact expectations;
- validation;
- retry budget;
- terminal states;
- escalation behavior;
- memory-write conditions;
- merge permissions.

### 5.3 Events should be immutable

Raw run, evidence, and belief events should be append-only immutable files or records with globally unique IDs.

Derived summaries may be regenerated.

### 5.4 One surface, one authority

Every mutable shared state surface must have:

- one authoritative loop;
- or an explicit compare-and-swap rule;
- or a proposal/reconciliation relationship.

### 5.5 Propose downward, govern upward

Daily loops execute within current governance.

Weekly loops propose evidence-driven changes.

Monthly loops reconcile and govern.

Audit loops observe and recommend.

Emergency falsification may interrupt this hierarchy only through an explicit escalation terminal state.

### 5.6 No invisible progress

A run is not complete because it produced prose or modified files.

It must expose:

- the question;
- artifact or blocker;
- checks;
- evidence effect;
- terminal state;
- next authorized transition.

### 5.7 Bounded continuation

A loop and a PR need stopping rules.

Persistent autonomy is not infinite continuation.

---

## 6. Target repository structure

```text
AGENTS.md
AURORA.md

automation/
  README.md
  contracts/
    daily-research-operator.v1.md
    weekly-evidence-synthesis.v1.md
    monthly-governance.v1.md
    system-audit.v1.md
  schemas/
    loop-run.schema.json
    evidence-event.schema.json
    belief-event.schema.json
    quest-action.schema.json
    pr-lifecycle.schema.json
  runs/
    2026/
      07/
        <run-id>.json
  reports/
    generated_long_log.md
    metrics/

calendar/
  evidence/
    2026/
      07/
        <evidence-id>.json
  roundups/
  monthly/
  belief_events.jsonl
  consolidated_beliefs.json

memory/
  mem_log_short.md

quests/
  active/
  completed/
  proposed/
  blocked/
```

The directory names may be adjusted to match existing repository conventions, but the conceptual separation is mandatory.

---

## 7. Authority order

When instructions conflict, use this order:

1. platform safety and explicit human instruction;
2. repository `AGENTS.md` stable law;
3. selected versioned loop contract;
4. active issue and PR acceptance slice;
5. active quest record;
6. monthly governance state;
7. latest accepted weekly evidence synthesis;
8. short spawn memory;
9. historical logs and older plans.

No lower layer may silently override a higher layer.

---

## 8. Versioned loop contracts

### 8.1 Common contract header

Every contract should declare:

```yaml
schema: sns.loop-contract.v1
loop_id: daily-research-operator
contract_version: 1.0.0
status: active
owner: SNS-S-S
allowed_triggers:
  - scheduled
  - explicit-human
writes:
  - automation/runs/**
  - artifacts/**
terminal_states:
  - DONE
  - DONE_WITH_LIMITATIONS
  - BLOCKED_ENVIRONMENT
  - BLOCKED_MISSING_EVIDENCE
  - BLOCKED_CONFLICT
  - VERIFICATION_FAILED
  - NEEDS_SCIENTIFIC_DECISION
  - NEEDS_GOVERNANCE_REVIEW
  - NEEDS_APPROVAL
```

### 8.2 Daily research operator contract

#### Goal

Produce one smallest coherent verified quest outcome or the most useful unblocker.

#### Required inputs

- `AGENTS.md`;
- daily contract;
- short memory;
- active quest record;
- active PR or branch state;
- recent run receipts for the same quest;
- relevant system and test files.

#### Conditional inputs

- README only when mission orientation is uncertain or changed;
- latest weekly evidence when it affects the active quest;
- monthly synthesis when governance changed since the last consumed run;
- AURORA scoring guidance before final scoring.

#### Authorized writes

- code, tests, data, plots, and technical artifacts within the active quest;
- the active implementation PR;
- one immutable run receipt;
- branch-local quest evidence or acceptance-progress fields;
- a proposal for governance change.

#### Unauthorized writes

The daily loop must not independently:

- create a new canonical program priority;
- close unrelated quests;
- change headline scientific claims;
- revise ARCI weights;
- rewrite consolidated belief state;
- merge unresolved scientific decisions;
- alter automation contracts.

#### Retry budget

- one correction cycle for ordinary verification failure;
- one environment repair cycle when dependencies are clearly safe and in scope;
- then terminate with an explicit blocker state.

#### Completion

A daily run ends when one of the common terminal states is reached and a receipt is written.

### 8.3 Weekly evidence synthesis contract

#### Goal

Convert recent external evidence into normalized evidence events, belief proposals, and bounded quest actions.

#### Authorized writes

- dated weekly roundup;
- normalized evidence events;
- belief events or belief proposals;
- quest-action proposals;
- one immutable weekly run receipt;
- comments or annotations on an active implementation PR when relevant.

#### Governance boundary

Weekly evidence may propose:

- refine an active quest;
- create a new quest;
- block or retire a quest;
- change priority;
- revise a belief.

It may not silently enact major queue governance except when evidence clearly falsifies a safety-critical or central assumption.

In that case it terminates `NEEDS_GOVERNANCE_REVIEW` and records the falsifying evidence.

### 8.4 Monthly governance contract

#### Goal

Reconcile evidence, beliefs, quest state, and strategic capacity for the completed month.

#### Authoritative writes

The monthly loop owns:

- consolidated belief state;
- quest creation, closure, merge, archival, and priority ordering;
- monthly objective selection;
- authoritative `next_canonical_move`;
- monthly short-memory reconciliation;
- retirement of stale proposals;
- one immutable monthly run receipt.

#### Limits

- no more than three primary objectives;
- active quest hard ceiling remains eight;
- unresolved headline scientific changes require human review;
- no automatic alteration of automation contracts.

### 8.5 System audit contract

#### Goal

Evaluate the autonomous research system without becoming an ordinary implementation loop.

#### Read scope

- run receipts;
- contracts and versions;
- commits and PRs;
- CI outcomes;
- artifacts and tests;
- weekly and monthly reports;
- evidence and belief events;
- quest creation and closure;
- branch lifecycle;
- memory changes;
- automation outcomes.

#### Writes

- one dated audit document;
- one audit run receipt;
- proposed architecture changes;
- no direct change to active automation behavior.

#### Merge rule

Always leave the audit as a draft PR for human review.

---

## 9. Loop ownership matrix

| State surface | Daily | Weekly | Monthly | Audit |
|---|---|---|---|---|
| Code and experiment implementation | Write | Read | Read | Read |
| Active implementation PR | Continue/update | Observe/comment | Govern/supersede | Measure |
| Technical artifacts | Write | Read | Read | Evaluate |
| Weekly roundup | Read | Authoritative write | Read | Evaluate |
| Raw evidence events | Read | Authoritative write | Read/reconcile | Evaluate |
| Belief-event proposals | Propose | Write | Reconcile | Evaluate |
| Consolidated belief state | Read | Propose only | Authoritative write | Evaluate |
| Active quest evidence fields | Write current quest | Propose refinement | Authoritative reconciliation | Evaluate |
| Quest creation/closure | Propose | Propose | Authoritative write | Recommend |
| Canonical next move | Advance within current move | Recommend | Authoritative write | Recommend |
| Short spawn memory | Branch-local proposal | No ordinary write | Authoritative reconciliation | Read |
| Immutable run receipt | Write own | Write own | Write own | Write own |
| Contract files | Read | Read | Read | Recommend only |
| Long report | Generated | Generated | Generated | Read |

Any implementation deviation from this matrix must be documented and tested.

---

## 10. Immutable run receipts

### 10.1 Identity

Do not allocate sequential IDs from mutable repository state.

Use collision-safe IDs derived from:

- loop ID;
- UTC trigger timestamp;
- short random or content-derived suffix.

Example:

```text
run_daily_20260714T190000Z_7f3c91
```

Filename example:

```text
automation/runs/2026/07/run_daily_20260714T190000Z_7f3c91.json
```

### 10.2 Required schema

```json
{
  "schema": "sns.loop-run.v1",
  "run_id": "run_daily_20260714T190000Z_7f3c91",
  "loop_id": "daily-research-operator",
  "contract_version": "1.0.0",
  "trigger_type": "scheduled",
  "triggered_at": "2026-07-14T19:00:00Z",
  "started_at": "2026-07-14T19:00:10Z",
  "completed_at": "2026-07-14T19:34:12Z",
  "source_commit": "<sha>",
  "source_branch": "main",
  "working_branch": "agent/qst-stor-0002-shadow-thermal",
  "quest_ids": ["QST-STOR-0002"],
  "pull_requests": [22],
  "consumed_run_ids": [],
  "consumed_evidence_ids": [],
  "question": "...",
  "success_criteria": ["..."],
  "artifacts": ["..."],
  "checks": [
    {
      "command": "pytest ...",
      "status": "passed",
      "evidence": "..."
    }
  ],
  "belief_events": [],
  "quest_actions": [],
  "assumptions_changed": [],
  "limitations": [],
  "terminal_state": "DONE_WITH_LIMITATIONS",
  "next_action": "...",
  "aurora_score": 4
}
```

### 10.3 Receipt invariants

A receipt must be:

- immutable after merge except for an explicit correction event;
- unique by `run_id`;
- schema-valid;
- linked to the contract version;
- linked to the source commit;
- honest about missing checks;
- explicit about consumed earlier runs;
- explicit about terminal state.

### 10.4 Corrections

Do not edit an old receipt to hide a mistake.

Create a correction event:

```json
{
  "schema": "sns.loop-run-correction.v1",
  "correction_id": "...",
  "corrects_run_id": "...",
  "reason": "...",
  "changed_fields": ["..."],
  "created_at": "..."
}
```

---

## 11. Optimistic concurrency protocol

### 11.1 Snapshot before action

Every run records:

- source commit;
- active quest revision or content hash;
- canonical-move revision or content hash;
- active PR head SHA;
- latest relevant run IDs.

### 11.2 Recheck before publishing

Before opening or updating a PR, the loop must re-read:

- default branch head;
- active quest state;
- canonical next move;
- relevant active PRs;
- newer run receipts for the same quest or state surface.

### 11.3 Conflict classes

#### Benign advancement

Another run added independent evidence or documentation that does not change the active acceptance slice.

Action:

- rebase or incorporate;
- cite the new run receipt;
- continue.

#### Quest ownership conflict

Another branch or PR now owns the same quest slice.

Action:

- prefer continuing the existing PR;
- do not create a second implementation branch;
- terminate `BLOCKED_CONFLICT` if safe continuation is unclear.

#### Governance conflict

Canonical move or quest priority changed after the run snapshot.

Action:

- do not publish stale governance mutations;
- preserve useful artifact work if still valid;
- terminate `NEEDS_GOVERNANCE_REVIEW` or re-scope with explicit evidence.

#### Scientific conflict

New evidence invalidates a core assumption of the run.

Action:

- stop implementation;
- record the falsifier;
- terminate `NEEDS_SCIENTIFIC_DECISION` or `NEEDS_GOVERNANCE_REVIEW`.

### 11.4 No blind force update

Scheduled loops must never force-push over another loop’s work or overwrite a shared state file without reconciliation.

---

## 12. Memory architecture

### 12.1 Short memory purpose

`memory/mem_log_short.md` should answer only:

- What program is active?
- What quest is active?
- What is the current accepted state?
- What blocks progress?
- What is the authoritative next move?
- Which PR owns the current implementation?
- Which monthly governance record established this state?

It should not be an append-only run chronology.

### 12.2 Short-memory authority

Monthly governance owns the canonical short-memory reconciliation.

Daily runs may propose a branch-local update when they complete the current move, but the proposal must not create competing canonical state across unmerged branches.

### 12.3 Long history

Generate long history from immutable receipts.

The generated report is disposable and reproducible.

No scheduled loop should need to append manually to one shared numbered Markdown ledger.

### 12.4 Migration of historical IDs

Existing historical session IDs should remain unchanged for provenance.

Add a migration note documenting known duplicate IDs.

Do not renumber historical records.

All new runs use collision-safe IDs.

---

## 13. Evidence-event model

### 13.1 Purpose

An evidence event records an observation or source claim before the repository interprets its belief impact.

### 13.2 Required fields

```json
{
  "schema": "sns.evidence-event.v1",
  "evidence_id": "ev_20260712_...",
  "recorded_at": "...",
  "source_title": "...",
  "source_url": "...",
  "source_type": "primary-paper",
  "publication_date": "...",
  "event_date": "...",
  "primary_or_secondary": "primary",
  "claim_cluster_id": "cluster_...",
  "environment": "LEO",
  "demonstrated_scale": "laboratory|component|orbital|system",
  "subsystems": ["STOR", "CTRL"],
  "mission_relevance": ["shadow-survival"],
  "evidence_tier": "A|B|C|D",
  "directness": 0.0,
  "novelty": 0.0,
  "limitations": ["..."],
  "fact_summary": "...",
  "inference_summary": "...",
  "speculation_summary": "..."
}
```

### 13.3 Claim clustering

Multiple sources about one underlying event share one `claim_cluster_id`.

Monthly synthesis must not count cluster members as independent demonstrations unless the evidence records explain genuine independence.

### 13.4 Negative evidence

The schema must support:

- null result;
- non-transferable terrestrial result;
- replication failure;
- category mismatch;
- unsupported claim;
- uncertainty increase.

Negative evidence is a valid artifact.

---

## 14. Belief-event model

### 14.1 Raw events versus consolidated state

`belief-event` is an immutable proposed update.

`consolidated_beliefs` is a derived monthly state.

Do not treat a stream of deltas as self-interpreting truth.

### 14.2 Declared scale

Use a normalized magnitude range:

```text
-1.0 <= magnitude <= 1.0
```

Interpretation:

- `-1.0`: strong evidence against;
- `0.0`: no directional change;
- `+1.0`: strong evidence for.

Magnitude is not confidence.

### 14.3 Required fields

```json
{
  "schema": "sns.belief-event.v1",
  "belief_event_id": "be_...",
  "belief_id": "SNS.STOR.AUX_POWER_SAFE_MODE",
  "evidence_ids": ["ev_..."],
  "claim_cluster_ids": ["cluster_..."],
  "direction": 1,
  "magnitude": 0.15,
  "confidence": 0.55,
  "source_quality": 0.45,
  "environment_match": 0.35,
  "novelty": 0.70,
  "status": "proposed",
  "reason": "...",
  "supersedes": [],
  "created_by_run_id": "run_weekly_..."
}
```

### 14.4 Monthly consolidation

Monthly governance should:

- group by belief ID and claim cluster;
- detect repeated evidence;
- consider source independence;
- reconcile conflicting events;
- record strengthened, weakened, retired, or newly uncertain assumptions;
- publish the resulting consolidated state and its source event IDs.

---

## 15. Quest-action model

### 15.1 Problem

A suggested action is not always a new quest.

### 15.2 Allowed action types

- `refine_existing`
- `propose_new`
- `block`
- `unblock`
- `retire`
- `merge_with`
- `reprioritize`
- `no_action`

### 15.3 Required fields

```json
{
  "schema": "sns.quest-action.v1",
  "quest_action_id": "qa_...",
  "action_type": "refine_existing",
  "quest_id": "QST-STOR-0002",
  "proposed_quest_id": null,
  "depends_on": ["PR-22"],
  "objective": "...",
  "artifact": "...",
  "success_metric": "...",
  "priority_effect": "none",
  "evidence_ids": ["ev_..."],
  "belief_event_ids": ["be_..."],
  "created_by_run_id": "run_weekly_...",
  "status": "proposed"
}
```

### 15.4 Validation

Tooling must check quest IDs across:

- active;
- completed;
- proposed;
- blocked;
- archived.

Rules:

- `propose_new` requires a unique proposed quest ID;
- `refine_existing` requires an existing active or blocked quest;
- `retire` requires evidence or governance rationale;
- `merge_with` requires two or more existing quest IDs;
- weekly actions remain proposed until governance accepts them;
- the daily loop may apply a refinement already authorized by the active acceptance slice.

---

## 16. Pull-request lifecycle

### 16.1 States

Every automation-created PR should expose one lifecycle state:

- `ACTIVE`
- `READY_FOR_REVIEW`
- `NEEDS_SCIENTIFIC_DECISION`
- `NEEDS_GOVERNANCE_REVIEW`
- `BLOCKED_ENVIRONMENT`
- `BLOCKED_CONFLICT`
- `VERIFICATION_FAILED`
- `SPLIT_REQUIRED`
- `SUPERSEDED`
- `MERGE_READY`

The state may be represented through PR body metadata, labels, or a machine-readable lifecycle file.

### 16.2 One implementation PR per quest slice

Ordinary rule:

- one open implementation PR per active quest acceptance slice;
- later runs continue the same PR when they pursue the same hypothesis and validation regime;
- a new hypothesis, system boundary, or validation regime should create a new slice or follow-up PR.

### 16.3 Review bounds

Trigger review when any condition is met:

- three scheduled operator cycles have modified the PR;
- seven calendar days have elapsed;
- the original acceptance slice is satisfied;
- the next action changes hypothesis or validation regime;
- changed files or scope exceed the plan-defined review threshold;
- scientific judgment remains unresolved.

### 16.4 Superseded work

A stale or superseded PR must be explicitly marked and closed with:

- superseding issue, PR, quest, or commit;
- reusable artifacts preserved;
- reason it is not being merged;
- no ambiguous generic draft state.

### 16.5 Automatic merge

Automatic merge remains conservative.

Allowed only when:

- all required checks pass;
- the change is conflict-free;
- the acceptance slice is satisfied;
- the change is small and reversible;
- no unresolved scientific or governance judgment remains;
- no core assumptions, dependencies, CI/security, or headline claims change.

---

## 17. Loop terminal states

### 17.1 Successful states

#### `DONE`

All success criteria are met and verified.

#### `DONE_WITH_LIMITATIONS`

The bounded outcome is complete, but declared limitations remain.

### 17.2 Blocked states

#### `BLOCKED_ENVIRONMENT`

Required tooling, permissions, service, compute, or dependency state prevents completion.

#### `BLOCKED_MISSING_EVIDENCE`

The question cannot be resolved without data or evidence not currently available.

#### `BLOCKED_CONFLICT`

Another branch, PR, or governance transition owns or invalidates the same state mutation.

### 17.3 Failure states

#### `VERIFICATION_FAILED`

The artifact exists but required checks failed after the bounded retry budget.

### 17.4 Escalation states

#### `NEEDS_SCIENTIFIC_DECISION`

Evidence or model behavior requires a human or governance decision about scientific interpretation.

#### `NEEDS_GOVERNANCE_REVIEW`

Queue priority, canonical move, quest lifecycle, or cross-loop authority requires reconciliation.

#### `NEEDS_APPROVAL`

The next action crosses an explicit approval boundary.

### 17.5 Terminal-state rule

A scheduled loop must not continue merely to avoid reporting a blocker.

A precise blocked state with evidence is a valid research result.

---

## 18. AGENTS and prompt simplification

### 18.1 Root `AGENTS.md`

Keep concise and durable.

Recommended sections:

1. mission and non-flight boundary;
2. authority order;
3. scientific invariants;
4. loop selection and contract pointers;
5. shared-state ownership summary;
6. verification and evidence rules;
7. terminal states;
8. approval and merge boundaries.

### 18.2 `AURORA.md`

Retain scoring semantics and evidence gate.

Remove duplicated spawn and mutation procedures when contracts become authoritative.

### 18.3 Ritual files

Reduce ritual documents to human-readable orientation and contract links.

Do not maintain a second executable copy of the loop procedure.

### 18.4 Platform prompts

After contracts exist, external scheduled prompts should become thin bootstraps.

Example:

```text
Execute the active repository contract `daily-research-operator.v1`
for `xxx3r/SNS-S-S`. Record the contract version, source commit,
and trigger metadata in the immutable run receipt. Platform safety and
explicit human instructions override the repository contract.
```

The platform prompt may still specify:

- repository identity;
- trigger context;
- notification behavior;
- temporary observation-period constraints.

It should not duplicate the whole operating constitution.

---

## 19. September audit protocol

### 19.1 Collision

The audit trigger occurs on a normal daily-operator date.

The system must avoid measuring partially completed same-day work as completed-period behavior.

### 19.2 Preferred solution

Create a frozen audit cutoff:

- cutoff time: immediately before the September 1 daily operator trigger;
- cutoff commit: recorded default-branch SHA;
- included runs: receipts completed before the cutoff;
- in-flight work: reported separately and excluded from completed-run rates.

### 19.3 Alternative solution

Temporarily suppress the September 1 daily operator run.

This requires an explicit automation-setting decision outside the repository and should be documented in the audit receipt.

### 19.4 Audit metrics

At minimum measure:

- total triggered runs;
- completed runs by terminal state;
- concrete-artifact rate;
- prose-only rate;
- verification pass rate;
- quest throughput;
- quest creation, refinement, merge, retirement, and closure counts;
- duplicate quest proposals;
- duplicate evidence clusters;
- active-PR continuation rate;
- stale or superseded PR count;
- median operator cycles per acceptance slice;
- canonical-move adherence;
- governance conflicts;
- logging-only merge conflicts;
- belief events accepted, rejected, reversed, or left unresolved;
- evidence that changed a later implementation decision;
- runs that consumed prior run receipts;
- abandoned branches;
- scientific claims strengthened, weakened, retired, or made more uncertain.

### 19.5 Information inheritance rate

Primary learning metric:

```text
information inheritance rate
  = runs whose evidence or artifact changed a later run
    / completed runs eligible for later consumption
```

A run counts as inherited only when a later receipt explicitly cites its run, evidence, belief, artifact, or quest-action ID and records the resulting decision effect.

### 19.6 Productive strangeness

The audit should distinguish:

- unusual but useful hypotheses;
- informative failed experiments;
- evidence-driven reversals;
- unexpected cross-subsystem connections;

from:

- duplicated prose;
- unconsumed reports;
- queue sediment;
- repeated unsupported speculation;
- artifact-free branch churn.

---

## 20. Validation and testing

### 20.1 Schema tests

Add tests that reject:

- duplicate run IDs;
- missing contract version;
- missing source commit;
- invalid terminal state;
- out-of-range belief magnitude or confidence;
- quest refinements targeting nonexistent quests;
- new quest proposals reusing existing IDs;
- belief events with missing evidence IDs;
- evidence records without source provenance;
- PR lifecycle records without a current state.

### 20.2 Repository semantic tests

Validate across the full repository, not only within one document.

Tests should detect:

- duplicate IDs across active/completed/proposed quests;
- multiple active implementation PR ownership records for one quest slice;
- canonical moves pointing to nonexistent or closed quests;
- consolidated beliefs citing missing events;
- run receipts citing missing artifacts;
- receipts claiming checks that lack result evidence;
- weekly actions enacted without monthly or explicit authority;
- stale receipts using retired contract versions without an allowed compatibility rule.

### 20.3 Concurrency simulations

Create representative fixtures for:

#### Scenario A: daily and weekly start from the same commit

Expected:

- unique run IDs;
- independent receipt files;
- no shared-log conflict;
- weekly quest refinement remains a proposal;
- daily artifact remains attributable.

#### Scenario B: daily continues a PR while monthly reprioritizes

Expected:

- daily recheck detects governance change;
- stale canonical mutation is not published;
- useful artifact is preserved or explicitly abandoned;
- terminal state is documented.

#### Scenario C: two daily triggers target the same quest

Expected:

- existing PR ownership is detected;
- second run continues or blocks;
- no duplicate implementation PR.

#### Scenario D: five sources report one demonstration

Expected:

- one claim cluster;
- source diversity retained;
- belief consolidation does not count five independent demonstrations.

#### Scenario E: evidence falsifies the active quest

Expected:

- weekly loop records evidence;
- active implementation is not silently deleted;
- governance escalation occurs;
- monthly or human review resolves the quest state.

#### Scenario F: September audit overlaps an in-flight run

Expected:

- frozen cutoff is honored;
- in-flight work is separately classified;
- audit metrics are reproducible.

### 20.4 Representative live evaluation

Before declaring migration complete, compare:

1. current architecture;
2. versioned contracts only;
3. contracts plus immutable receipts;
4. full ownership and semantic schema architecture.

Measure:

- task correctness;
- artifact quality;
- unnecessary reads;
- unnecessary writes;
- merge conflicts;
- duplicate work;
- verification rate;
- human clarification demand;
- branch and PR closure quality;
- information inheritance;
- token and execution cost when observable.

Do not assume the largest instruction system is best.

---

## 21. Migration phases

### Phase 0: freeze and inventory

Deliverables:

- state-surface inventory;
- current loop prompt archive or summary;
- known duplicate ID report;
- active branch and PR ownership map;
- current contract baseline;
- September cutoff decision.

No behavior changes yet.

### Phase 1: contracts and receipts

Deliverables:

- `automation/README.md`;
- four versioned loop contracts;
- loop-run JSON schema;
- receipt writer and validator;
- collision-safe IDs;
- generated long-report tool;
- initial compatibility path for existing memory.

This is the highest-priority implementation phase.

### Phase 2: ownership and concurrency

Deliverables:

- state ownership matrix encoded in docs and validation;
- source-commit and state-hash snapshot fields;
- pre-publication recheck procedure;
- conflict classification;
- tests for parallel loop scenarios;
- removal of mandatory shared-log appends.

### Phase 3: semantic evidence and beliefs

Deliverables:

- evidence-event schema;
- claim clustering;
- belief-event schema and normalized scale;
- consolidated-belief generator;
- provenance validation;
- duplicate-source handling;
- negative-evidence support.

### Phase 4: quest actions and governance

Deliverables:

- semantic quest-action schema;
- cross-queue ID validation;
- weekly proposal versus monthly governance rules;
- emergency falsification escalation;
- active queue checks;
- migration of roundup-to-quest tooling.

### Phase 5: PR lifecycle

Deliverables:

- lifecycle states;
- one-PR-per-quest-slice checks;
- stale/superseded policy;
- review bounds;
- split-required detection or guidance;
- migration/closure of branch ghosts.

### Phase 6: instruction deduplication

Deliverables:

- lean root `AGENTS.md`;
- AURORA focused on scoring;
- ritual documents reduced to orientation;
- scheduled platform prompts reduced to contract bootstraps;
- model-neutral wording.

This phase occurs after contracts are executable so no behavior is lost during simplification.

### Phase 7: audit instrumentation and evaluation

Deliverables:

- audit metric generator;
- information-inheritance tracking;
- frozen-cutoff implementation;
- representative concurrency evaluation;
- migration report;
- final issue acceptance review.

---

## 22. Recommended PR sequence

### PR 1: planning authority

- add this plan;
- link issue #24;
- no runtime or control-plane behavior change.

### PR 2: inventory and contract skeleton

- state-surface inventory;
- archived baseline prompt descriptions;
- `automation/` structure;
- four contract skeletons;
- no scheduled prompt changes yet.

### PR 3: immutable run receipts

- schema;
- unique ID generator;
- validator;
- generated long log;
- compatibility notes;
- tests for collision and corrections.

### PR 4: ownership and optimistic concurrency

- ownership matrix;
- snapshot/recheck implementation;
- conflict states;
- remove mandatory shared-log append behavior;
- concurrency fixtures.

### PR 5: evidence and belief semantics

- evidence schema;
- claim clusters;
- normalized belief events;
- consolidation logic;
- migration of existing ledger where possible without rewriting history.

### PR 6: quest-action semantics

- action types;
- cross-repository queue validation;
- roundup tooling update;
- weekly proposal and monthly acceptance flow.

### PR 7: PR lifecycle governance

- lifecycle metadata;
- review/split bounds;
- stale and superseded cleanup;
- one implementation owner per quest slice.

### PR 8: AGENTS and scheduled-prompt simplification

- route through contracts;
- remove duplicated procedures;
- preserve scientific law;
- update external automations only after repository behavior is merged and validated.

### PR 9: audit instrumentation

- frozen cutoff;
- metrics;
- information inheritance;
- system evaluation harness;
- September audit readiness report.

The sequence may be split further, but should not combine unrelated scientific changes.

---

## 23. Rollout and compatibility

### 23.1 Dual-write period

For a limited transition period, a scheduled run may:

- write the new immutable receipt;
- update existing required summaries;
- compare generated and historical views.

The dual-write period must have a declared end date or completion criterion.

### 23.2 Historical preservation

Do not erase:

- existing weekly roundups;
- monthly syntheses;
- belief ledger history;
- quest history;
- old session logs;
- prior contracts or prompts where preserved.

Add migration metadata rather than rewriting the past into a false clean history.

### 23.3 Contract activation

A contract becomes active only when:

- merged to `main`;
- schema-valid;
- required tooling exists;
- relevant scheduled prompt references it;
- compatibility behavior is documented.

### 23.4 Contract retirement

Retired contracts remain in Git.

New receipts may not cite a retired contract unless an explicit compatibility or replay mode permits it.

---

## 24. Risks and mitigations

### Risk: over-engineering a small repository

Mitigation:

- implement contracts and receipts first;
- measure actual conflicts;
- keep schemas minimal;
- generate human-readable views;
- stop adding infrastructure that does not improve correctness or auditability.

### Risk: scheduled agents spend all effort on governance

Mitigation:

- daily loop remains artifact-first;
- receipts are generated by tooling;
- ordinary runs should not manually edit multiple control surfaces;
- monthly loop owns reconciliation.

### Risk: JSON events reduce human readability

Mitigation:

- preserve Markdown roundups and monthly syntheses;
- generate readable reports from immutable records;
- keep machine records as substrate, not the only interface.

### Risk: monthly authority becomes a bottleneck

Mitigation:

- daily loop can advance within accepted quest scope;
- weekly loop can propose changes;
- emergency falsification has an escalation path;
- explicit human instruction may override monthly timing.

### Risk: source clustering hides genuine independent evidence

Mitigation:

- claim cluster groups shared underlying events, not all similar claims;
- record source independence and replication status;
- permit one cluster to contain genuinely independent measurements with explicit metadata.

### Risk: contract bootstrap prompts become too thin

Mitigation:

- platform prompt retains repository identity and trigger context;
- contract activation tests verify discoverability;
- September audit measures missed reads and contract adherence.

### Risk: old scheduled prompts and new contracts drift

Mitigation:

- receipt records both contract version and a platform-prompt revision marker when available;
- contract activation checklist includes automation update;
- audit flags runs that do not cite an active contract.

---

## 25. Definition of done

Issue #24 is complete only when all of the following are true.

### Contracts

- daily, weekly, monthly, and audit contracts are versioned in the repository;
- root `AGENTS.md` routes to them;
- platform prompts reference them without duplicating the full procedure;
- contract activation and retirement are documented.

### Run identity and receipts

- new runs use collision-safe IDs;
- every scheduled run writes one immutable schema-valid receipt;
- receipt links include source commit and contract version;
- correction events exist;
- manually allocated sequential IDs are retired for new runs.

### Shared state

- every shared state surface has an authority or reconciliation rule;
- daily, weekly, and monthly loops do not silently overwrite each other;
- shared append-only Markdown logging is no longer required;
- short memory is compact and authoritative.

### Evidence and beliefs

- evidence events have machine-readable provenance;
- duplicate underlying events can be clustered;
- belief magnitude and confidence scales are declared;
- consolidated beliefs trace to raw events;
- negative evidence and uncertainty increases are representable.

### Quests

- quest actions distinguish refinement, creation, block, retirement, merge, and no action;
- IDs are validated across all quest states;
- weekly proposals and monthly governance are distinct;
- active queue bounds are enforced;
- one canonical next move is authoritative.

### PR lifecycle

- automation-created PRs expose explicit lifecycle states;
- stale and superseded PRs are resolved;
- one implementation PR owns one quest acceptance slice;
- review and split rules are active;
- automatic merge remains conservative.

### Verification

- schema and semantic tests pass;
- representative concurrency simulations pass;
- no duplicate run IDs occur;
- no lost shared-state updates occur;
- no contradictory canonical moves are silently published;
- no duplicate active quest is created from a refinement;
- one underlying evidence cluster is not counted as multiple independent demonstrations.

### Audit readiness

- September cutoff behavior is decided and encoded;
- audit metrics can be generated from repository records;
- information inheritance can be measured;
- in-flight work is distinguishable from abandoned or completed work;
- an external reviewer can reconstruct why each major state transition occurred.

### Preservation

- scientific invariants remain intact;
- artifact-first quest execution remains intact;
- no-hardware-overclaiming boundary remains intact;
- historical records remain available;
- infrastructure burden is demonstrably lower than or justified by the conflicts it prevents.

---

## 26. First canonical implementation move

After this planning PR is reviewed and merged, the first implementation PR should be:

> Add repository-local loop contracts and immutable collision-safe run receipts without changing scientific behavior.

This first move should include:

1. `automation/README.md`;
2. four contract files with common headers;
3. `loop-run.schema.json`;
4. run-ID generation;
5. receipt validation;
6. correction-event support;
7. generated long-log proof of concept;
8. tests for duplicate IDs and missing source/contract metadata;
9. compatibility instructions for the current scheduled prompts;
10. no changes to active physics, quests, beliefs, or ARCI conclusions.

The key acceptance test is simple:

> A daily and weekly loop beginning from the same commit can both finish, produce uniquely addressable receipts, and merge without editing the same mutable run-history surface.

---

## 27. Closing principle

SNS-S-S should remain a place where scheduled agents can be proactive, curious, and scientifically useful.

The transaction layer is not intended to cage that intelligence. It exists so that intelligence operating on several clocks can compose.

The desired result is not more paperwork.

It is a research organism whose actions have:

- identity;
- provenance;
- ownership;
- evidence;
- boundedness;
- memory;
- and consequences visible to the next loop.

That is the bridge from several autonomous tasks to one learning laboratory.
