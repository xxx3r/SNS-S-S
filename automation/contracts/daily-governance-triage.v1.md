---
schema: sns.loop-contract.v1
loop_id: daily-governance-triage
contract_version: 1.0.0
status: active
owner: SNS-S-S
allowed_triggers:
  - scheduled
  - explicit-human
reads:
  - AGENTS.md
  - automation/contracts/daily-governance-triage.v1.md
  - automation/state_ownership.json
  - automation/delegations/**
  - automation/runs/**
  - automation/pr_lifecycle/**
  - quests/actions/**
  - quests/active/**
  - calendar/monthly/**
  - memory/mem_log_short.md
writes:
  - automation/runs/**
  - automation/pr_lifecycle/**
  - quests/actions/**
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
# Daily Governance Triage v1

Nickname: **Pre-Game Game Master**.

## Goal

Clear low-risk administrative debris before the Daily Research Operator starts, and convert routine bounded approvals into machine-readable authority that can be consumed immediately. This loop protects the research slot from approval echo; it is not a second scientific operator.

## Work-conserving rules

1. Approval does not consume the research slot. Triage runs separately before daily implementation.
2. Acknowledgement is not an artifact. Triage publishes authority; the Daily Research Operator consumes it without a separate acceptance transaction.
3. One triage run may disposition multiple independent administrative candidates, but may issue at most four new research authorizations and may not create implementation branches itself.
4. Every authorized research slice still has one owner, at most one implementation PR, exactly one implementation receipt, and one terminal disposition.
5. Failures, negative evidence, and expired authorizations remain visible. Do not erase an inconvenient lineage row to make the queue look clean.

## Mandatory preflight

Before claiming a connector or repository environment is unavailable, attempt the required live connector operation. Missing local shell access is not an environment blocker when GitHub repository reads/writes and GitHub-hosted validation remain available. A `BLOCKED_ENVIRONMENT` receipt must preserve the exact attempted operation and provider-returned error.

## Triage transaction

1. Freeze accepted `main` and the current delegation envelope.
2. Read only compact lineage: recent receipts, current open PR ownership/checks/reviews, pending quest-action proposals, mechanical lifecycle drift, and the canonical next move.
3. Classify each candidate using the decision ladder:
   - L0 local implementation detail -> leave to Daily Research Operator;
   - L1 bounded reversible refinement inside delegation -> triage may authorize;
   - L2 queue, belief, canonical-memory, major architecture, or constitutional decision -> monthly governance;
   - L3 protected scientific assumption, external/public action, strategic or reserved authority -> human.
4. For each L1 research authorization, emit an enacted `refine_existing` quest action with a machine-readable `authorization` object bound to the accepted source commit and current delegation.
5. Mechanically synchronize a PR lifecycle record only when live GitHub evidence is unambiguous and the change is a direct terminal/status reflection. Supersession, abandonment, split decisions, ownership ambiguity, or scientific interpretation remain monthly-owned.
6. Recheck source commit, delegation, and PR ownership before publication.
7. Write exactly one immutable triage receipt listing every decision, authorization, lifecycle synchronization, deferral, and limitation.

## Delegated authority

Triage may enact only `refine_existing` actions for already-active quests and only when every requested surface, budget, check, stop condition, and expiry is inside the current machine-readable delegation envelope.

Triage may not:

- create, activate, retire, block, merge, or reprioritize quests;
- change monthly objectives;
- rewrite consolidated beliefs or canonical memory;
- modify scientific implementation code, configs, tests, or outputs itself;
- alter contracts, schemas, state ownership, CI/security policy, or delegation law;
- decide between protected scientific architecture routes;
- publish external claims or perform repository-external actions;
- weaken experiment holdouts, evaluator ownership, evidence language, or falsifiers.

## Completion

`DONE` or `DONE_WITH_LIMITATIONS` requires a current source snapshot, current delegation, an auditable decision list, exactly one immutable receipt, and one concrete handoff to the Daily Research Operator or higher authority. A run that merely restates a previous approval without creating or validating authority is not complete.
