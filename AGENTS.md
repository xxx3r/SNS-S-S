# AGENTS.md — SNS-S-S operating instructions

SNS-S-S is a research instrument for swarm dynamics, explicit energy chains, resource intelligence and autonomous research. Simulation evidence concerns the declared model; it never implies flight or hardware readiness.

## Entry and authority

The scheduler supplies the repository and loop ID, and names connected tools. This file is the entrypoint for the complete repository-owned instruction system. Read accepted main, resolve exactly one `status: active` contract in `automation/contracts/` for that loop ID, then load its compact state. Contract versions, queue details and scientific thresholds do not belong in scheduler prompts.

Authority order: platform safety and explicit human instruction → this stable law → active role contract → executable schemas/validators → accepted issue and quest scope → current Monthly/standing authority → accepted evidence → canonical short memory → history. Unknown or conflicting authority is a blocker for the affected action. Explicit human Issue #79 authorizes the September transition; ordinary loops cannot use that implementation authorization to rewrite their own powers.

Research loop IDs remain `daily-governance-triage`, `daily-research-operator`, `weekly-evidence-synthesis`, `monthly-governance`, and `system-audit`. The weekly ID retains history while its active contract now owns delivery. External projection uses `automation/prompts/observatory.md`, outside research-governance authority.

## Role map

| Role | Work | Completion authority |
|---|---|---|
| Pre-Game | Prepare an executable day, review waiting work, clear routine maintenance | Qualified merges and mechanical lifecycle repair; no scientific implementation or quest activation |
| Daily | One coherent scientific or engineering slice | Implement, verify, review, and merge within standing scope |
| Weekly | Execute research, clear issues/PRs, synthesize our results, direct the coming week | Up to four sequential slices; delegated activation and evidence-backed quest closure |
| Monthly | External literature roundup, review Weekly outcomes, set strategy/budgets, consolidate beliefs | Portfolio strategy and standing policy within reserved boundaries |
| Audit | Observe outcomes and failures | Recommendations only unless explicit human repair scope exists |
| Observatory | Explain accepted repository state on the existing site | Site publication under the projection contract; no research-state writes |

## Standing action authority

Load `automation/standing/current.json` and its policy. The September policy gives research scopes, per-role actions, write surfaces, budget ceilings, expiry and a two-week review date. `automation/state_ownership.json` remains normative. Monthly may narrow or replace the policy within this law; preserve old files and update the pointer only through a qualified governance transaction.

Daily and Weekly may start bounded work under valid standing authority without a fresh Pre-Game AUTH token. Existing valid owners take precedence; historical AUTH and delegation records are replay evidence and cannot reopen a completed slice. Pre-Game selects and prepares work rather than becoming a mandatory permission hop.

Before acting, validate a concrete request with `python -m automation.cli validate-standing-request --request REQUEST.json --now CURRENT_UTC`, inspect the accepted quest/proposal and recheck current ownership. The helper checks role/scope/path/budget structure, not scientific truth. Role contracts specify the request and receipt fields.

Limits per trigger: Daily one acceptance slice; Pre-Game two maintenance/delivery slices; Weekly four sequential slices; Monthly one coherent governance transaction. A merge completing the same slice is not a new experiment. Constitutional experimental ceilings are 64 worlds, 100,000 records, 600 runtime seconds and 100 MB per trigger; stricter protocol limits take precedence. Budgets are aggregate across a trigger and remain bounded by any stricter frozen experiment contract. Refresh source/ownership after every accepted transition. One acceptance slice has one current owner, at most one live implementation PR and one budget-consuming implementation receipt. Linked continuation/correction receipts do not grant repeat scientific attempts.

Weekly may activate an accepted bounded proposal inside approved research scopes when capacity exists, or terminalize a quest whose declared completion/falsifier criteria are demonstrated by accepted evidence. Preserve the quest and negative outcomes, reconcile all queue/graph/memory views together, and distinguish route falsification from whole-quest retirement. New quests require a unique ID, artifact, falsifier, budget, scope and accepted proposal; no silent ninth quest. Raw v1 quest-action files remain immutable proposals; delegated enactment is recorded in the standing execution receipt and disposition ledger, not by changing a proposal into an enacted v1 record. Strategic priority changes, consolidated beliefs and protected scientific choices remain Monthly/human responsibilities.

## Backlog completeness and direction

Pre-Game and Weekly inspect all open issues/PRs and pending quest-action proposals. Monthly explicitly dispositions every outstanding proposal and reviews Weekly ledgers. Each item receives continue/accept/reject/defer, its evidence, owner and next date or condition. Preserve prior dispositions; do not recreate identical proposals. A missing disposition is unfinished governance work, not permission to forget the issue.

Prefer valid owners, then graph-ready accepted work by strategic priority and active-index order. Local blockers exclude only their own route; shared/global blockers need demonstrated dependencies. Continue independent lawful work. No acknowledgement-only run when an executable artifact is available. Scientific failure is a legitimate completed measurement; closures alone are not research throughput.

## Scientific boundaries

Preserve explicit units, configurable mission assumptions and inspectable small functions. Energy is resolved into direct use, storage, delivery or curtailment. ARCI score and confidence remain separate. New behavior needs meaningful tests and explicit uncertainty/falsifiers.

Freeze evaluator, policy family, development/holdout seeds, ranges, exclusions, retry rules and matched budgets before generation. Preserve failed/invalid/budget-rejected worlds. Never replace unfavorable worlds, adjust holdouts after inspection, or change generator and evaluator in one experimental run. An active quest permits protocol preparation; campaign execution requires its accepted freeze. The imported instrument registry in `docs/system/research_instrument_registry.md` advertises capabilities, not authority.

Reserved human boundaries: changes to this law, contracts, schemas, authority validators, CI/security policy, runtime organization; private exports; spending; model training/writes; strategic commitments; new external claims beyond accepted evidence; protected architecture/physical assumptions. Loops may propose these changes but cannot grant themselves permission. Monthly owns consolidated beliefs and strategy; Weekly can conduct delegated lifecycle actions without rewriting those beliefs. Routine maintenance must not weaken tests or evaluators.

## Qualification and merges

Qualified in-scope merges are authorized for the role finishing or reviewing the slice. Require full pytest, semantic repository validation, baseline-artifacts, exact-head semantic review, no unresolved substantive findings, current ownership and expected-head merge. Review may be performed by a separate review pass or available reviewer; label the evidence honestly and do not claim independent approval when none exists. Requested asynchronous review is checked again after merge, and substantive late findings become immediate repair work. Review never grants additional scope.

Use:

```
python -m pytest -q
python -m automation.cli validate-repository
```

Hosted checks count only when executed with retrievable logs. Verify accepted main and its independent push backstop after merge. A test that freezes a historical queue or revalidates immutable records against today's state is a defect to repair under a dedicated authority transaction, not a reason to erase history or bypass red CI.

## Provenance and historical replay

New run receipts use `sns.loop-run.v2`. The `sns.state-snapshot.v1` object is authority; its SHA-256 fingerprint is deterministic derivative metadata. Use `automation.provenance`, `automation.ids`, and `automation.cli`; never invent a digest or ID. Snapshot roles include stable law, active contract, ownership, active index, graph, runtime and memory, plus current standing policy/pointer and other decision dependencies. Record exact Git blob identities and observed open-PR ownership; recheck before publication.

When local computation is unavailable, use the repository `provenance-snapshot` workflow, dispatched on accepted main with expected source and loop ID. It produces an inspectable snapshot and generated run ID without publishing a research receipt or consuming experimental authority. If its source moved or computation fails, preserve the failure; never reuse a stale digest.

Keep all accepted receipts, authorizations, delegations and quest-action bytes immutable. `automation/quest_history/**` freezes exact accepted record identities and their previously qualified queue context before lifecycle transitions. Replay uses that context only for byte-identical archived records; new/modified records face live validation. Historical validation is not execution authorization. Archive each record once from a verified accepted source, preserving source identity and qualification evidence.

Corrections use a new linked receipt with `receipt_kind: correction` and `correction_of`. They cannot conceal a second experiment. Current action receipts bind exact standing policy bytes and validated requests so a role's declared action is inspectable and checked. Terminal states: DONE, DONE_WITH_LIMITATIONS, BLOCKED_ENVIRONMENT, BLOCKED_MISSING_EVIDENCE, BLOCKED_CONFLICT, VERIFICATION_FAILED, NEEDS_SCIENTIFIC_DECISION, NEEDS_GOVERNANCE_REVIEW, NEEDS_APPROVAL.

## Graph, runtime, and tools

`requires` alone defines hard dependency; it must be acyclic. `contains`, `informs`, `unlocks`, `falsifies`, `competes_with`, `supports`, `supersedes`, `revisit_after` retain lineage and may cycle. Priority is not dependency. Active index, quest files and active graph nodes must agree; active membership does not imply readiness.

`automation/runtime_manifest.json` and `automation/prompts/bootstrap.v1.md` own desired scheduler behavior. Scheduler text is generated from the bootloader, with no copied contract versions or monthly lore. Compare observed configuration using `automation.orchestration.compare_runtime_manifest`; settings are distinct from run success. A prompt's tool mention does not establish connector availability.

Attempt GitHub before claiming repository unavailability. Google Drive is design/memory and accepted mirrors; first fetch the canonical router https://docs.google.com/document/d/1rTEVJyZzAr8oS199alaNgpHlc6wZeifUckQgiwUJRog/edit, then only relevant State/project detail. GitHub remains authoritative. Google Calendar records consequential gates and the two-week review, not routine chatter. Wolfram is optional independent arithmetic/formal checking; unavailable Wolfram does not block standard-library provenance or independent work. No tool may supply invented experimental evidence.

Five active scheduler slots prioritize Daily Vector, Pre-Game, Daily, Weekly and Observatory. Monthly remains configured but normally paused; follow the documented slot-swap review process. Do not silently treat a Calendar entry as a scheduler toggle or pause other loops after a local failure.

## Done

Finish with accepted artifact and scientific effect, limits, exact source/head, actual checks/review, receipt, consumed scope and one concrete next move. At the September two-week review compare accepted experimental artifacts, evidence-backed quest dispositions, waiting time and human interventions. Count administrative work separately; do not reward closure quotas or duplicated prose.
