---
schema: sns.loop-contract.v1
loop_id: daily-research-operator
contract_version: 1.0.0
status: retired
owner: SNS-S-S
allowed_triggers:
  - scheduled
  - explicit-human
reads:
  - AGENTS.md
  - automation/contracts/daily-research-operator.v1.md
  - automation/state_ownership.json
  - memory/mem_log_short.md
  - quests/active/**
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
# Daily Research Operator v1

## Goal

Produce the smallest coherent verified outcome inside the currently authorized quest acceptance slice. Continue the existing implementation PR when one owns that slice. A precise blocked result is preferable to unbounded continuation.

## Transaction

1. Record trigger metadata and the source commit.
2. Read the compact spawn memory, active quest, relevant recent receipts, and PR lifecycle record.
3. Capture hashes for owned state, monthly governance, and PR ownership.
4. Reuse the active branch when it remains valid. Do not open a duplicate implementation PR.
5. Implement one artifact-bearing slice and run focused verification.
6. Recheck source commit, governance, and PR ownership before publication.
7. On conflict, preserve useful branch-local artifacts and terminate `BLOCKED_CONFLICT` or `NEEDS_GOVERNANCE_REVIEW`.
8. Write exactly one immutable run receipt. Mutable summaries are generated views, not the source of history.

## Mutation boundary

The daily loop may update code, tests, data, outputs, and scoped acceptance evidence. It may not enact queue-wide reprioritization, rewrite consolidated beliefs, create a duplicate quest, or silently supersede another PR.

## Completion

`DONE` requires a concrete artifact, passing declared checks, explicit limitations, a stable acceptance slice, and one next action. Automatic merge remains conservative and only applies when repository policy, tests, ownership, and review state all permit it.
