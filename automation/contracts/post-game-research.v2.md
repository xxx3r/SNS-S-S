---
schema: sns.loop-contract.v1
loop_id: post-game-research
contract_version: 2.0.0
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

Mission: make tomorrow scientifically better, not administratively prettier. Post-Game is the independent scientist in the Pre-Game→Daily→Post-Game→next Pre-Game wheel, not the Daily's approval officer. Start from fresh accepted main and resolve this active contract, standing policy, owner and repository graph independently. Inspect the most recent Daily accepted evidence or blocked run and the latest Weekly disposition. Identify what was measured, what remains UNKNOWN, and which distinct active research route is available.

Choose **one non-duplicative, individually owned, accepted-quest scientific or engineering acceptance slice** within the post-game-research standing scope. Possibilities include a reproducible counterexample, an independent measurement-appraisal, source-backed feasibility analysis, or a frozen bounded experiment on a separate accepted route. Complete an inspectable research artifact rather than copying status summaries. Do not compete with a live Daily owner or repeat consumed experimental worlds. The accepted SIM3 #134 single world must not be regenerated. New research candidates (#131/#132) can be appraised as noncanonical proposals; they are not themselves execution authority.

## Finish the independent scientific loop

Inspect the accepted Daily result (or stop) and other accepted observations. Challenge the mapping from [Formula] claim to [Mechanism] observable and any premature [Implementation] inference, or choose another unowned active quest. Prefer one reproducible non-generating counterexample, event-level data/metric audit, source-backed bounds analysis, or frozen protocol over repeating an interpretation in an issue thread. A result that invalidates a favorite claim is useful. Preserve the accepted source and do not rerun a consumed world.

An issue comment may communicate a source-derived finding and the next falsifier, but it is **not** a qualified acceptance slice. If the run cannot complete the standing preflight, reproducible docs/test artifact, immutable v2 receipt and required checks/review, report the comment as noncanonical and count zero accepted science. Do not report DONE merely because a critique was posted; explain the concrete missing gate. The next Pre-Game should receive the exact evidence reference, supported internal-confidence direction and limits, smallest discriminating test and independent fallback.

Before acting validate the concrete standing request using `python -m automation.cli validate-standing-request --request REQUEST.json --now CURRENT_UTC`, including source-bound Post-Game loop ID, action, path, owner and all four budgets. A valid preflight does not establish scientific truth. New experiments require a prospectively accepted protocol freeze and a falsifier. Post-Game may implement and merge one qualified independent slice; it may NOT activate/retire quests, change protected architecture, evaluator, holdout, authority policy, contracts, validator, runtime, schema, or scheduler. It has no authority to pause unrelated loops. A local blockage must trigger a documented lawful fallback search, not global shutdown.

Preserve immutable v2 receipts, source snapshots and all failed/unfavorable evidence. Run full pytest, semantic repository validation, baseline-artifacts, exact-head independent review, and expected-head merge on qualified work. Reobserve main before publication or merge. Report scientific measurement or null result first, with prior evidence that changed the choice, uncertainty, falsifier, and a concrete next Pre-Game handoff. Label unexecuted ideas, administrative closures and missing tools separately. Google Drive uses the canonical router when relevant; GitHub is authoritative, and Wolfram is optional.
