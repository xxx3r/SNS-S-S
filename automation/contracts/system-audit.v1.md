---
schema: sns.loop-contract.v1
loop_id: system-audit
contract_version: 1.0.0
status: active
owner: SNS-S-S
allowed_triggers:
  - scheduled
  - explicit-human
reads:
  - AGENTS.md
  - automation/contracts/system-audit.v1.md
  - automation/runs/**
  - automation/pr_lifecycle/**
  - calendar/evidence/**
  - calendar/belief_events/**
  - quests/actions/**
  - quests/**
writes:
  - automation/runs/**
  - automation/reports/**
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
retry_budget: 0
---
# System Audit v1

## Goal

Observe and measure the autonomous research organism without silently changing ordinary scientific, quest, belief, PR, or scheduling state.

## Frozen cutoff

Declare the audit period and freeze its cutoff time and commit before analysis; record the exact default-branch commit observed at execution. Receipts completed before the cutoff are included; in-flight and later work are reported separately. For replay of the historical September audit, preserve its cutoff `2026-09-01T14:00:00Z`, immediately before that day's ordinary 08:00 America/Denver trigger. That historical cutoff is not the default for an October or later audit.

## Required metrics

Measure triggered runs, terminal states, artifact and prose-only rates, verification, quest actions, duplicate proposals and evidence clusters, PR continuation and stale states, governance conflicts, information inheritance, claim reversals, and work excluded by the cutoff.

## Information inheritance

A prior run counts as inherited only when a later receipt explicitly cites its run, evidence, belief, artifact, or quest-action ID and records the decision effect.

## Mutation boundary

The audit writes generated reports and one receipt. Recommendations remain recommendations until monthly governance or explicit human authority accepts them.
