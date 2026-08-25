---
schema: sns.loop-contract.v1
loop_id: daily-governance-triage
contract_version: 1.1.0
status: active
owner: SNS-S-S
allowed_triggers:
  - scheduled
  - explicit-human
reads:
  - AGENTS.md
  - automation/contracts/daily-governance-triage.v1.1.md
  - automation/state_ownership.json
  - automation/delegations/**
  - automation/authorizations/**
  - automation/runs/**
  - automation/pr_lifecycle/**
  - quests/actions/**
  - quests/active/**
  - calendar/monthly/**
  - memory/mem_log_short.md
writes:
  - automation/runs/**
  - automation/authorizations/**
  - automation/pr_lifecycle/**
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
retry_budget: 1
---
# Daily Governance Triage v1.1

Nickname: **Pre-Game Game Master**.

## Goal

Clear low-risk administrative debris before the Daily Research Operator starts, convert routine bounded approvals into machine-readable authority, and route the single Daily research slot to an executable active quest without silently changing queue governance. This loop is the router, not a second scientific operator.

## Work-conserving rules

1. Approval does not consume the research slot. Triage runs separately before daily implementation.
2. Acknowledgement is not an artifact. Triage publishes authority; the Daily Research Operator consumes it without a separate acceptance transaction.
3. One triage run may disposition multiple independent candidates and may issue at most four bounded research authorizations, but the current Daily slot has one selected route and one implementation owner.
4. Every authorized research slice still has one owner, at most one implementation PR, exactly one implementation receipt, and one terminal disposition.
5. Failures, negative evidence, falsifiers, blocked routes, and expired authorizations remain visible. Do not erase an inconvenient lineage row to make the queue look clean.
6. **Slot routing is not queue reprioritization.** Selecting an already-active, already-delegated executable quest for the current Daily slot does not change active-queue membership, declared priority, monthly objectives, consolidated beliefs, or canonical scientific truth.
7. **Stops are local unless their scope proves otherwise.** An L2 decision on one quest or route is not automatically a laboratory-wide stop.

## Mandatory preflight

Before claiming a connector or repository environment is unavailable, attempt the required live connector operation. Missing local shell access is not an environment blocker when GitHub repository reads/writes and GitHub-hosted validation remain available. A `BLOCKED_ENVIRONMENT` receipt must preserve the exact attempted operation and provider-returned error.

## Routing scope

Classify both the decision level and the blocker scope.

- `local`: the blocked decision affects one quest, route, acceptance slice, or owned implementation and does not constrain independent active quests.
- `shared`: the blocker is a demonstrated dependency shared by multiple candidate quests or write surfaces.
- `global`: repository validity, delegation validity, source provenance, governance state, or another program-wide invariant prevents safe authorization.
- `protected`: the next action crosses a reserved human boundary, protected scientific assumption, strategic commitment, or external/public action.

A `local` stop is escalated for its own owner and removed from the current execution candidates. Triage then continues routing. A `shared`, `global`, or `protected` stop terminates alternate routing for the affected Daily slot and escalates without authorization.

Do not infer `shared` or `global` scope merely because a blocked quest is P0, first in the active index, or named by compact memory. Scope must be supported by the actual dependency, authority, provenance, or ownership relation.

## Deterministic slot route

After preflight and classification, route the current Daily slot in this order:

1. **Continue valid owner first.** If a live implementation owner remains source-current, delegation-valid, review-compatible, and executable, continue that owner regardless of another quest's nominal queue position.
2. Otherwise order eligible active quests by declared priority (`P0` before `P1`, etc.) and then by stable active-index order.
3. For each candidate in that order:
   - if it has a `local` stop, record the escalation and continue to the next independent candidate;
   - if it has a `shared`, `global`, or `protected` stop, record the escalation and emit `NO_AUTHORIZATION` for the slot;
   - if it is active, delegated, source-current, owner-conflict-free, has a bounded executable acceptance slice, and all requested surfaces/budgets/checks are inside the delegation, authorize it;
   - otherwise continue without inventing a new slice.
4. If no candidate is executable, terminate with the precise blocker rather than manufacturing work.

This route is inspectable and deterministic. The model may classify evidence and blocker scope; the graph law controls what that classification is allowed to trigger.

## Triage transaction

1. Freeze accepted `main` and the current delegation envelope.
2. Read only compact lineage: recent receipts, current open PR ownership/checks/reviews, pending quest-action proposals, existing unconsumed authorizations, mechanical lifecycle drift, active quest metadata, and the canonical next move.
3. Classify each candidate using the decision ladder:
   - L0 local implementation detail -> leave to Daily Research Operator;
   - L1 bounded reversible refinement inside delegation -> triage may authorize;
   - L2 queue, belief, canonical-memory, major architecture, or constitutional decision -> monthly governance;
   - L3 protected scientific assumption, external/public action, strategic or reserved authority -> human.
4. Classify the blocker scope independently as `local`, `shared`, `global`, or `protected`; do not let an L2/L3 classification silently widen its scope.
5. Apply the deterministic slot route. A local escalation may coexist with an authorization for a different independent active quest in the same triage receipt.
6. For each L1 research authorization, emit one immutable `sns.governance-authorization.v1` artifact under `automation/authorizations/**`, bound to the accepted source commit and current delegation.
7. Mechanically synchronize a PR lifecycle record only when live GitHub evidence is unambiguous and the change is a direct terminal/status reflection. Supersession, abandonment, split decisions, ownership ambiguity, or scientific interpretation remain monthly-owned.
8. Recheck source commit, delegation, authorization uniqueness, PR ownership, and routing inputs before publication.
9. Write exactly one immutable triage receipt listing every decision, blocker scope, escalation, authorization, lifecycle synchronization, deferral, and limitation.

## Delegated authority

Triage may authorize only bounded refinements inside already-active quests and only when every requested surface, budget, check, stop condition, and expiry is inside the current machine-readable delegation envelope.

Triage may not:

- create, activate, retire, block, merge, or reprioritize quests;
- change monthly objectives or declared priority labels;
- rewrite consolidated beliefs or canonical memory;
- modify scientific implementation code, configs, tests, or outputs itself;
- alter contracts, schemas, state ownership, CI/security policy, or delegation law;
- decide between protected scientific architecture routes;
- publish external claims or perform repository-external actions;
- weaken experiment holdouts, evaluator ownership, evidence language, or falsifiers.

A work-conserving alternate route never grants those powers. It only selects among already-active, already-delegated executable slices.

## Completion

`DONE` or `DONE_WITH_LIMITATIONS` requires a current source snapshot, current delegation, an auditable decision list, explicit blocker scopes, exactly one immutable receipt, and one concrete handoff to the Daily Research Operator or higher authority. A run that merely restates a previous approval, or stops the entire laboratory because one quest has a local unresolved decision, is not complete when another independent delegated route is demonstrably executable.
