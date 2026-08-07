---
schema: sns.loop-contract.v1
loop_id: monthly-governance
contract_version: 1.0.0
status: retired
owner: SNS-S-S
allowed_triggers:
  - scheduled
  - explicit-human
reads:
  - AGENTS.md
  - automation/contracts/monthly-governance.v1.md
  - calendar/evidence/**
  - calendar/belief_events/**
  - calendar/consolidated_beliefs.json
  - calendar/roundups/**
  - quests/**
  - automation/pr_lifecycle/**
  - automation/runs/**
writes:
  - automation/runs/**
  - calendar/consolidated_beliefs.json
  - calendar/monthly/**
  - quests/**
  - automation/pr_lifecycle/**
  - memory/mem_log_short.md
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
# Monthly Governance v1

## Goal

Reconcile weekly proposals and completed implementation evidence into one authoritative bounded queue, consolidated belief view, PR disposition map, and canonical next move.

## Authority

Monthly governance owns queue-wide creation, merge, retirement, blocking, reprioritization, and canonical-move publication. It preserves raw evidence, belief events, receipts, historical quests, and useful branch artifacts rather than rewriting history.

## Transaction

1. Freeze a source snapshot and consume explicit weekly, daily, and prior monthly IDs.
2. Validate quest IDs across active, completed, proposed, and blocked queues.
3. Consolidate beliefs from immutable events with provenance intact.
4. Accept, reject, or defer each quest-action proposal.
5. Enforce 1–8 active quests and no more than three monthly objectives.
6. Classify each open automation PR as active, merge-ready, blocked, split-required, superseded, or abandoned.
7. Publish one canonical next move in compact memory.
8. Recheck state before publication and write one immutable receipt.
