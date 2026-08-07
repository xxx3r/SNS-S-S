---
schema: sns.loop-contract.v1
loop_id: daily-research-operator
contract_version: 1.1.0
status: active
owner: SNS-S-S
allowed_triggers:
  - scheduled
  - explicit-human
reads:
  - AGENTS.md
  - automation/contracts/daily-research-operator.v1.1.md
  - automation/state_ownership.json
  - automation/delegations/**
  - automation/authorizations/**
  - memory/mem_log_short.md
  - quests/active/**
  - quests/actions/**
  - automation/pr_lifecycle/**
  - automation/runs/**
writes:
  - automation/runs/**
  - automation/pr_lifecycle/**
  - outputs/**
  - code-and-tests-within-active-quest
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
retry_budget: 2
---
# Daily Research Operator v1.1

## Goal

Produce the smallest coherent verified scientific or engineering outcome inside the currently authorized quest acceptance slice. Continue the existing implementation PR when one owns that slice. A precise blocked result is preferable to unbounded continuation.

## Pre-game authorization rule

Before selecting a fresh slice, inspect current unexpired `sns.governance-authorization.v1` artifacts issued by `daily-governance-triage` and bound to the accepted source/delegation state.

- If exactly one valid authorization owns the next executable slice and no competing implementation owner exists, consume it and begin the authorized work in this run.
- If several valid authorizations exist, choose the highest-priority one consistent with accepted monthly objectives and one-owner law; leave the others unconsumed.
- If an authorization is expired, source-stale, outside delegation, already consumed by an implementation receipt, or conflicts with a live PR owner, do not execute it.
- **Acknowledging an approval is not an artifact and is not a valid daily outcome.** A valid bounded authorization must lead directly to the first implementation artifact or to a concrete new blocker discovered while attempting it.

## Transaction

1. Record trigger metadata and the source commit.
2. Read the compact spawn memory, active quest, current delegation, relevant triage authorization, recent receipts, and PR lifecycle record.
3. Capture hashes for owned state, monthly governance, delegation, and PR ownership.
4. Reuse the active branch when it remains valid. Do not open a duplicate implementation PR.
5. Implement one artifact-bearing slice and run focused verification.
6. Recheck source commit, delegation, governance, authorization, and PR ownership before publication.
7. On conflict, preserve useful branch-local artifacts and terminate `BLOCKED_CONFLICT` or `NEEDS_GOVERNANCE_REVIEW`.
8. Write exactly one immutable run receipt. Include the consumed authorization ID in `consumed_ids` when an authorization was used. Mutable summaries are generated views, not the source of history.

## Mutation boundary

The daily loop may update code, tests, data, outputs, and scoped acceptance evidence. It may update only the PR lifecycle record it owns. It may not enact queue-wide reprioritization, rewrite consolidated beliefs, change canonical memory, create a duplicate quest, or silently supersede another PR.

A triage authorization delegates scope, not scientific truth. If implementation reveals missing evidence, a protected assumption, a route choice, a failed holdout/evaluator, or a request beyond the authorized write surfaces or budgets, stop at the appropriate terminal state rather than widening the authorization.

## Completion

`DONE` requires a concrete artifact, passing declared checks, explicit limitations, a stable acceptance slice, and one next action. Automatic merge remains conservative and only applies when repository policy, tests, ownership, review state, and any consumed authorization all permit it.
