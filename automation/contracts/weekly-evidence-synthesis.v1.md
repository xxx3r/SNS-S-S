---
schema: sns.loop-contract.v1
loop_id: weekly-evidence-synthesis
contract_version: 1.0.0
status: active
owner: SNS-S-S
allowed_triggers:
  - scheduled
  - explicit-human
reads:
  - AGENTS.md
  - automation/contracts/weekly-evidence-synthesis.v1.md
  - calendar/evidence/**
  - calendar/roundups/**
  - calendar/belief_events/**
  - quests/**
  - automation/runs/**
writes:
  - automation/runs/**
  - calendar/evidence/**
  - calendar/belief_events/**
  - calendar/roundups/**
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
retry_budget: 2
---
# Weekly Evidence Synthesis v1

## Goal

Translate current primary evidence into normalized evidence events, claim clusters, belief-event proposals, and bounded quest-action proposals without silently becoming the governance authority.

## Transaction

1. Record source commit, trigger time, and the last accepted weekly/monthly receipts consumed.
2. Normalize each source with provenance and a source fingerprint.
3. Group reports of one underlying event into one claim cluster while retaining source diversity and genuine independent replications.
4. Record supporting, weakening, falsifying, negative, and uncertainty-increasing evidence.
5. Emit belief events on the declared `[-1, 1]` magnitude and `[0, 1]` confidence scales.
6. Use semantic quest actions. Refinement is not creation.
7. Publish queue changes only as proposals. Monthly governance or explicit human authority enacts them.
8. Write one immutable receipt and terminate after the bounded synthesis slice.

## Emergency falsification

Evidence that materially falsifies an active quest produces an `emergency_escalation` proposal and `NEEDS_GOVERNANCE_REVIEW`. The weekly loop does not delete the active quest or its branch.
