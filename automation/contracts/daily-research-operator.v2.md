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

Produce one coherent scientific/engineering slice and carry it to its terminal disposition. Select or continue work inside the accepted active quest and standing research scope. Pre-Game guidance is useful input, not a mandatory permission token. An absent/stale Pre-Game run does not block valid standing authority. Historical AUTH records remain history and cannot override the current policy.

Choose implementation details and bounded follow-up experiments inside the accepted method and budgets. If a new experiment needs a protocol freeze, prepare and qualify that freeze first; run only after acceptance. Do not change a frozen generator/evaluator, outcomes, holdout split, or protected assumption to rescue a result. Complete review/merge when qualified; otherwise leave a concrete owner and resumable checkpoint.

## Execution and evidence

Follow AGENTS.md and the current standing policy. Before acting, run `python -m automation.cli validate-standing-request --request REQUEST.json --now CURRENT_UTC` or its repository-hosted equivalent. This checks structural authority; inspect the actual accepted quest, evidence, source and ownership too. A helper PASS does not establish scientific truth.

Capture the canonical source snapshot, including `standing_authority` bound to the exact current policy bytes and `standing_pointer`. Receipt `standing_execution` preserves `policy_json` as the exact source text and a `requests` list with loop_id, action, scope, acceptance_slice, concrete paths, all four budget dimensions, transaction_count, and evidence_refs. Set `standing_execution.trigger_id` to `<loop_id>:<original trigger_time normalized to UTC ISO-8601 with +00:00>`, retained across every slice and merge of this invocation. Empty requests require literal `decision_effect: NO_ACTION` and empty artifacts, belief_effects and consumed_ids. Never hide attempted work there. Each completed slice has one owner and exactly one standing action receipt; include implementation and merge requests together in that receipt and use system-audit append-only corrections for later forensic fixes; a trigger performing multiple slices may create linked transaction receipts with a shared trigger ID and cumulative transaction_count. Counts and budgets cover the whole trigger; do not restart them after a merge.

Implement and qualify complete bounded slices, including tests, honest limitations, receipt, exact-head semantic review and permitted merge. Re-fetch main, standing policy, source records, open owners and review threads before publication/merge. If main moved, preserve useful changes and reconstruct from the new source; never fabricate a current provenance seal. One failed scientific result is retained as evidence, not retried for a better answer. Deterministic code repair/revalidation does not consume another experiment unless generation/evaluation is actually repeated.

Run full pytest, semantic repository validation and baseline-artifacts qualification. A failure in authority/CI infrastructure requires a dedicated human-owned repair; preserve the blocker and continue independent lawful work only when the failure is demonstrably local. Never pause unrelated loops because one quest is blocked. Do not rewrite your own contract, evaluator after freeze, or authority policy.

Report accepted artifacts, scientific outcome and limitations first; then receipt, exact source/head, review/check evidence, scope used, and one next move. Separate administrative closures from scientific completions. Google Drive is relevant design/memory, GitHub is repo authority, Calendar is consequential milestones, Wolfram is optional independent computation. A missing optional tool blocks only work that specifically depends on it.

