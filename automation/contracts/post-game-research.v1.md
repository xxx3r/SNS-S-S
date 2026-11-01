---
schema: sns.loop-contract.v1
loop_id: post-game-research
contract_version: 1.0.0
status: active
owner: SNS-S-S
allowed_triggers:
  - scheduled
  - explicit-human
reads:
  - AGENTS.md
  - automation/state_ownership.json
  - automation/standing/**
  - automation/schemas/**
  - automation/runtime_manifest.json
  - quests/**
  - automation/runs/**
  - automation/pr_lifecycle/**
  - memory/**
  - calendar/monthly/**
  - calendar/roundups/**
  - docs/research/**
writes:
  - automation/runs/**
  - automation/pr_lifecycle/**
  - code-and-tests-within-active-quest
  - outputs/**
  - docs/**
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
# Post-Game Independent Research v1

Mission: make tomorrow scientifically better, not administratively prettier. Start from fresh accepted main and resolve this active contract, standing policy, owner and repository graph independently. Inspect the most recent Daily accepted evidence or blocked run and the latest Weekly disposition. Identify what was measured, what remains UNKNOWN, and which distinct active research route is available.

Choose **one non-duplicative, individually owned, accepted-quest scientific or engineering acceptance slice** within the post-game-research standing scope. Possibilities include a reproducible counterexample, an independent measurement-appraisal, source-backed feasibility analysis, or a frozen bounded experiment on a separate accepted route. Complete an inspectable research artifact rather than copying status summaries. Do not compete with a live Daily owner or repeat consumed experimental worlds. The accepted SIM3 #134 single world must not be regenerated. New research candidates (#131/#132) can be appraised as noncanonical proposals; they are not themselves execution authority.

Before acting validate the concrete standing request using `python -m automation.cli validate-standing-request --request REQUEST.json --now CURRENT_UTC`, including source-bound Post-Game loop ID, action, path, owner and all four budgets. A valid preflight does not establish scientific truth. New experiments require a prospectively accepted protocol freeze and a falsifier. Post-Game may implement and merge one qualified independent slice; it may NOT activate/retire quests, change protected architecture, evaluator, holdout, authority policy, contracts, validator, runtime, schema, or scheduler. It has no authority to pause unrelated loops. A local blockage must trigger a documented lawful fallback search, not global shutdown.

Preserve immutable v2 receipts, source snapshots and all failed/unfavorable evidence. Run full pytest, semantic repository validation, baseline-artifacts, exact-head independent review, and expected-head merge on qualified work. Reobserve main before publication or merge. Report scientific measurement or null result first, with prior evidence that changed the choice, uncertainty, falsifier, and a concrete next Pre-Game handoff. Label unexecuted ideas, administrative closures and missing tools separately. Google Drive uses the canonical router when relevant; GitHub is authoritative, and Wolfram is optional.
