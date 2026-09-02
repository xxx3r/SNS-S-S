---
schema: sns.loop-contract.v1
loop_id: monthly-governance
contract_version: 1.2.0
status: active
owner: SNS-S-S
allowed_triggers:
  - scheduled
  - explicit-human
reads:
  - AGENTS.md
  - automation/contracts/monthly-governance.v1.1.md
  - automation/delegations/**
  - automation/authorizations/**
  - calendar/evidence/**
  - calendar/belief_events/**
  - calendar/consolidated_beliefs.json
  - calendar/roundups/**
  - quests/**
  - automation/pr_lifecycle/**
  - automation/runs/**
writes:
  - automation/runs/**
  - automation/delegations/**
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
# Monthly Governance v1.2

## Goal

Reconcile weekly proposals and completed implementation evidence into one authoritative bounded queue, consolidated belief view, PR disposition map, canonical next move, and a narrow delegation envelope for routine same-month governance triage.

## Constitutional authority

Monthly governance owns queue-wide creation, merge, retirement, blocking, reprioritization, monthly objectives, consolidated beliefs, stale cross-PR reconciliation, and canonical-move publication. It preserves raw evidence, belief events, receipts, historical quests, and useful branch artifacts rather than rewriting history.

The existence of a daily triage loop does not shrink monthly authority. Triage is a delegated executor for Level-1 reversible decisions only; monthly governance remains the constitutional layer and may narrow, revoke, or replace its delegation envelope at any accepted governance transaction.

## Delegation envelope

Each accepted monthly governance transaction must publish or explicitly carry forward one machine-readable envelope under `automation/delegations/**`.

The envelope may delegate only bounded `refine_existing` authorization inside already-active quests. It must freeze:

- eligible active quest IDs;
- authorized implementation write surfaces;
- maximum authorizations per triage run;
- one-PR and one-receipt limits per authorization;
- required repository checks;
- protected surfaces that can never be delegated;
- expiry;
- escalation conditions.

Monthly governance may not delegate its own constitutional powers over quest membership/order, consolidated beliefs, canonical memory, major architecture decisions, contracts/schemas, or external publication/action.

## Transaction

1. Freeze a source snapshot and consume explicit weekly, daily, triage, and prior monthly IDs.
2. Validate quest IDs across active, completed, proposed, and blocked queues.
3. Consolidate beliefs from immutable events with provenance intact.
4. Accept, reject, or defer each quest-action proposal and review any triage authorization outcomes or expiries.
5. Enforce 1–8 active quests and no more than three monthly objectives.
6. Classify each open automation PR as active, merge-ready, blocked, split-required, superseded, or abandoned.
7. Publish one canonical next move in compact memory.
8. Publish or carry forward one bounded delegation envelope for `daily-governance-triage`.
9. Recheck state before publication and write one immutable receipt.

## Completion

A monthly transaction is complete only when queue state, belief consolidation, PR disposition, canonical next move, and delegation state are mutually consistent and traceable to accepted evidence. The scheduled monthly cadence is the regular constitutional review, not a rule that low-risk delegated decisions must wait until the next calendar month; explicit-human triggers remain lawful when a non-delegable decision genuinely requires earlier governance.


## September Organization v2.x duties

The v1.2 contract is the active constitutional surface for the September transition.

Every accepted v1.2 Monthly transaction must:

1. record the exact accepted source snapshot and typed inheritance references;
2. record a non-empty decision effect;
3. review every open automation PR and classify it as active, merge-ready, blocked, split-required, superseded, or abandoned;
4. perform an explicit quest-terminalization review without inventing a scientific conclusion or changing quest state outside accepted Monthly authority;
5. reconcile canonical memory once, append-only in meaning, by recording the accepted next move and preserving the prior transition as history;
6. publish or carry forward exactly one bounded triage delegation envelope;
7. expose unresolved lineage, proposal/authorization timing, and administrative-cost measurements;
8. recheck source, delegation, ownership, and artifact references before publication.

A stale or interchangeable-agent handoff is a machine-visible lineage gap when typed inheritance or an explicit independent-continuity declaration is absent. PR closure is a lifecycle disposition: it preserves the branch contents and review history and does not merge or reconstruct superseded work.
