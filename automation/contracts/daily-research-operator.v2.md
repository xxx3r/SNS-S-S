---
schema: sns.loop-contract.v1
loop_id: daily-research-operator
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
# Daily Research Delivery v2

Produce one falsifiable scientific/engineering slice at [Formula], [Mechanism] or [Implementation] level, chosen from **any unowned ready active quest** across the eight SNS paths. Select or continue work inside the accepted active quest and standing research scope. Pre-Game guidance is useful input, not a mandatory permission token. An absent/stale Pre-Game run does not block valid standing authority. Historical AUTH records remain history and cannot override the current policy.

Choose implementation details and bounded follow-up experiments inside the accepted method and budgets. If a new experiment needs a protocol freeze, prepare and qualify that freeze first; run only after acceptance. Do not change a frozen generator/evaluator, outcomes, holdout split, or protected assumption to rescue a result. Complete review/merge when qualified; otherwise leave a concrete owner and resumable checkpoint.

## Receive the question, not an instruction to obey

Start from Post-Game's scientific question and Pre-Game's candidate, but independently reconstruct the work frontier from accepted evidence and live owners. Staying on a quest is optional; repeated consumed experiments are not. Read the latest relevant Post-Game scientific critique (including issue/PR comments when that is where the finding lives) as an *unqualified lead*, then verify its code or data provenance; do not treat it as an approved experiment. The inherited Pre-Game choice is advisory, not a permission hop. Reject a stale or already-consumed next-action entry even if `memory/mem_log_short.md` still displays it.

Select one standing-authorized active-quest slice that creates inspectable scientific evidence, a new validation/control, or a prospectively frozen protocol. State intended claim versus actual observable and internal evidence versus external plausibility. Non-generating diagnostics are valid. If the chosen route hits an approval boundary or existing owner, inspect at least one *distinct* active quest with no competing owner before ending at NEEDS_SCIENTIFIC_DECISION or NO_ACTION. State each checked candidate, its evidence, why it is legal or blocked, and who can unblock it. Local scientific decisions never pause unrelated research; do not repeat frozen or consumed worlds.

A scheduled run reporting a research question without a qualified implementation/artifact is a useful handoff but **zero accepted scientific slices**. Qualify the actual artifact using the existing standing request, receipt, full tests, semantic checks and exact-head review. Do not create a new handoff ledger.

## Execution and evidence

Follow AGENTS.md and the current standing policy. Before acting, run `python -m automation.cli validate-standing-request --request REQUEST.json --now CURRENT_UTC` or its repository-hosted equivalent. This checks structural authority; inspect the actual accepted quest, evidence, source and ownership too. A helper PASS does not establish scientific truth.

Capture the canonical source snapshot, including `standing_authority` bound to the exact current policy bytes and `standing_pointer`. Receipt `standing_execution` preserves `policy_json` as the exact source text and a `requests` list with loop_id, action, scope, acceptance_slice, concrete paths, all four budget dimensions, transaction_count, and evidence_refs. Set `standing_execution.trigger_id` to `<loop_id>:<original trigger_time normalized to UTC ISO-8601 with +00:00>`, retained across every slice and merge of this invocation. Empty requests require literal `decision_effect: NO_ACTION` and empty artifacts, belief_effects and consumed_ids. Never hide attempted work there. Each completed slice has one owner and exactly one standing action receipt; include implementation and merge requests together in that receipt and use system-audit append-only corrections for later forensic fixes; a trigger performing multiple slices may create linked transaction receipts with a shared trigger ID and cumulative transaction_count. Counts and budgets cover the whole trigger; do not restart them after a merge.

Implement and qualify complete bounded slices, including tests, honest limitations, receipt, exact-head semantic review and permitted merge. Re-fetch main, standing policy, source records, open owners and review threads before publication/merge. If main moved, preserve useful changes and reconstruct from the new source; never fabricate a current provenance seal. One failed scientific result is retained as evidence, not retried for a better answer. Deterministic code repair/revalidation does not consume another experiment unless generation/evaluation is actually repeated.

Run full pytest, semantic repository validation and baseline-artifacts qualification. A failure in authority/CI infrastructure requires a dedicated human-owned repair; preserve the blocker and continue independent lawful work only when the failure is demonstrably local. Never pause unrelated loops because one quest is blocked. Do not rewrite your own contract, evaluator after freeze, or authority policy.

Report accepted artifacts, scientific outcome and limitations first; then receipt, exact source/head, review/check evidence, scope used, and one next move. Separate administrative closures from scientific completions. Google Drive is relevant design/memory, GitHub is repo authority, Calendar is consequential milestones, Wolfram is optional independent computation. A missing optional tool blocks only work that specifically depends on it.

