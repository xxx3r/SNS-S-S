---
schema: sns.loop-contract.v1
loop_id: monthly-governance
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
  - automation/standing/**
  - automation/delegations/**
  - calendar/**
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
retry_budget: 2
---
# Monthly Research and Governance v2

Own external research roundup and primary-paper appraisal, strategic decisions, at most three monthly objectives, consolidated beliefs and standing authority. Read every accepted Weekly delivery ledger and consequential Daily result, including failures. Review all open issues/PRs and pending quest-action proposals; every item must receive a disposition or explicit deferral condition, owner and next review date. A bounded transaction does not excuse leaving backlog requests invisible.

Monthly may enact queue-wide strategy and publish a new immutable standing policy plus current pointer within the ceilings and reserved boundaries in AGENTS.md. Preserve superseded policy/delegation records for replay. Do not narrow ordinary work to one named micro-experiment when a safe research scope can be delegated. Review how freedom was used: evidence preservation, experiment throughput, waiting time and human interventions. Narrow a problematic scope based on evidence; avoid stopping independent research.

Monthly is a governance role with a monthly review, not a mandatory monthly wait for all decisions. Weekly holds the delegated lifecycle authority in its contract. Literature collection may use source-grounded substeps, but strategic acceptance and belief consolidation are one coherent transaction. Prospective policy changes take effect only after qualified merge.

Under the five-slot scheduler arrangement, Monthly is normally paused between reviews. Follow the repo runtime slot policy for a scheduled review swap; a Calendar reminder is not evidence the scheduler was changed.

## Execution and evidence

Follow AGENTS.md and the current standing policy. Before acting, run `python -m automation.cli validate-standing-request --request REQUEST.json --now CURRENT_UTC` or its repository-hosted equivalent. This checks structural authority; inspect the actual accepted quest, evidence, source and ownership too. A helper PASS does not establish scientific truth.

Capture the canonical source snapshot, including `standing_authority` bound to the exact current policy bytes and `standing_pointer`. Receipt `standing_execution` preserves `policy_json` as the exact source text and a `requests` list with loop_id, action, scope, acceptance_slice, concrete paths, all four budget dimensions, transaction_count, and evidence_refs. Use an empty list only for a genuine no-action result; never hide attempted work there. Each completed slice has one owner and one budget-consuming receipt; a trigger performing multiple slices may create linked transaction receipts with a shared trigger ID and cumulative transaction_count. Counts and budgets cover the whole trigger; do not restart them after a merge.

Implement and qualify complete bounded slices, including tests, honest limitations, receipt, exact-head semantic review and permitted merge. Re-fetch main, standing policy, source records, open owners and review threads before publication/merge. If main moved, preserve useful changes and reconstruct from the new source; never fabricate a current provenance seal. One failed scientific result is retained as evidence, not retried for a better answer. Deterministic code repair/revalidation does not consume another experiment unless generation/evaluation is actually repeated.

Run full pytest, semantic repository validation and baseline-artifacts qualification. A failure in authority/CI infrastructure requires a dedicated human-owned repair; preserve the blocker and continue independent lawful work only when the failure is demonstrably local. Never pause unrelated loops because one quest is blocked. Do not rewrite your own contract, evaluator after freeze, or authority policy.

Report accepted artifacts, scientific outcome and limitations first; then receipt, exact source/head, review/check evidence, scope used, and one next move. Separate administrative closures from scientific completions. Google Drive is relevant design/memory, GitHub is repo authority, Calendar is consequential milestones, Wolfram is optional independent computation. A missing optional tool blocks only work that specifically depends on it.

