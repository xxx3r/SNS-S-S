# AGENTS.md — SNS-S-S operating instructions

SNS-S-S is a research instrument for swarm dynamics, explicit energy chains, resource intelligence and autonomous research. Simulation evidence concerns the declared model; it never implies flight or hardware readiness.

## Entry and authority

The scheduler supplies the repository and loop ID, and names connected tools. This file is the entrypoint for the complete repository-owned instruction system. Read accepted main, resolve exactly one `status: active` contract in `automation/contracts/` for that loop ID, then load its compact state. Contract versions, queue details and scientific thresholds do not belong in scheduler prompts.

Authority order: platform safety and explicit human instruction → this stable law → active role contract → executable schemas/validators → current Monthly/standing authority → accepted issue and quest scope → accepted evidence → canonical short memory → history. Accepted work-item scope operates within current authority; it cannot widen that authority. Unknown or conflicting authority is a blocker for the affected action. Historical implementation approvals, including Issue #79, do not authorize ordinary loops to rewrite their own powers.

Research loop IDs remain `daily-governance-triage`, `daily-research-operator`, `post-game-research`, `weekly-evidence-synthesis`, `monthly-governance`, and `system-audit`. The weekly ID retains history while its active contract now owns delivery. External projection uses `automation/prompts/observatory.md`, outside research-governance authority.

## Role map

| Role | Work | Completion authority |
|---|---|---|
| Pre-Game | Recover yesterday's question; identify and prepare a real science test | Zero-world docs/tests research preparation, qualified maintenance; no quest activation |
| Daily | One falsifiable [Formula]/[Mechanism]/[Implementation] advance on any eligible active quest | Implement, verify and merge within standing scope |
| Post-Game | Independent semantic critic or second investigator; give tomorrow's next question | One standing-authorized implement/merge; no quest activation or policy authority |
| Weekly | Independent external literature telescope across the eight paths; source-backed confidence and falsifiable ideas | Literature and proposal work; under Wheel v3 no quest activation or retirement |
| Monthly | External/internal synthesis, portfolio review, strategic decisions and consolidated beliefs | Portfolio strategy and standing policy within reserved boundaries |
| Audit | Observe outcomes and failures | Recommendations only unless explicit human repair scope exists |
| Observatory | Explain accepted repository state on the existing site | Site publication under the projection contract; no research-state writes |

## SNS Research Wheel v3

Use `docs/research/SNS_RESEARCH_WHEEL_V3.md` as a compact *scientific map*, never as another authority layer. The permanent June SNS paths are materials/structure; absorption/conversion; storage/transmission; communication/control; propulsion/orbit; advanced manufacturing; operational workflow/safety; and simulation/testing. Active quests serve these paths and are not the mission itself.

Distinguish three evidence stages: **[Formula]** (theory, mathematical models, units and optional Lean formalization); **[Mechanism]** (simulation and separately identified physical bench measurements); **[Implementation]** (integrated hardware and eventual space validation). Green software tests do not prove physical model validity or flight readiness. Validate formal consistency, empirical meaning and physical-engineering closure separately.

Maintain **external confidence** (dated primary literature, limits and source links) and **internal confidence** (our own accepted proof/test/measurement) *independently for each precise claim*. Report ⬆️/⬇️/↔️ and UNKNOWN with rationale; do not automatically average into an uncalibrated number.

**[Yesterday Post-Game]→[Pre-Game]→[Daily]→[Post-Game]→[Next Pre-Game]** is one research wheel. Each role independently verifies current source, authority and owners, and may select any unowned, graph-ready **active** quest. Continue an unanswered question where useful or move across quests if locally blocked; Pre-Game and Weekly are never per-experiment approval officers. Pre-Game may conduct one standing-authorized zero-world docs/tests preparation; Daily produces evidence; Post-Game challenges the claim/observable correspondence or conducts a distinct lawful test. Existing reports/receipts carry the claim, observable, evidence level, limits, external/internal directions, next smallest test and independent fallback. No new handoff ledger or repeated permission token.

The original 0.1–1% daily progress aim is directional, not a scientific percentage absent a valid denominator. Negative results count when they actually reduce uncertainty. Administrative PRs alone are not progress.

## Research relay across fresh agents

Fresh source is mandatory; fresh science amnesia is not. Each run rejects inherited SHA, authority, queue, owner and next-action **claims** as current facts until rechecked against live GitHub. It nevertheless recovers unresolved *questions* from accepted results, source-backed critiques and pending scientific gates. A prior agent's recommended step is a candidate, never execution authorization. The current standing policy, accepted quest, frozen protocol, live owner and review state determine what may actually run. Never repeat consumed worlds merely to reconstruct context.

Use the repository's existing evidence, PRs, issues and v2 receipts as the relay. **Do not create a new governance ledger, handoff PR, approval token or duplicate receipt solely to communicate a next question.** The concluding report or existing issue/PR discussion carries four compact fields: (1) accepted result with exact evidence ref, (2) remaining UNKNOWN or falsifier, (3) smallest next test/artifact with eligible owner and existing authority, (4) a genuinely independent fallback or the specific global obstruction. Pre-Game surfaces the candidate, Daily can independently choose or reject it, and Post-Game challenges the inference. All three verify the current source and ownership themselves. An unqualified Post-Game comment remains a useful hypothesis, not accepted scientific evidence or a binding task.

When a selected quest is blocked, check at least one distinct active-quest candidate that does not overlap an existing owner before concluding there is no executable research. If both fail, report the concrete scientific, ownership or infrastructure reason for each and the next condition. A quest-local NEEDS_SCIENTIFIC_DECISION is **not** a global work stoppage. One accepted non-generating test/protocol/artifact can be progress; report-only commentary is not qualified research output.

A PR lifecycle file is a **historical in-branch snapshot**, not a mechanism for changing GitHub's live merged state. Prefer GitHub's verified PR and review facts for current ownership. A lifecycle correction PR is warranted only if the discrepancy blocks an actual qualification, merge, owner transfer or audit. Never open a PR solely to mark the previous lifecycle-only reconciliation PR as merged; this would create an infinite administrative chain. Carry harmless lag to the next already-qualified substantive transaction or a later explicit audit, preserving immutable receipts and historical truth. This rule does not waive required receipt/CI qualification or unresolved substantive review findings.

## Standing action authority

Load `automation/standing/current.json` and its policy from freshly observed accepted main. The selected policy gives research scopes, per-role actions, write surfaces, budget ceilings, expiry and review date. Read the current period's accepted `calendar/monthly/` decisions for applicable supplements; a missed review does not itself change policy expiry. Expired policies and past review instructions remain history. `automation/state_ownership.json` remains normative. Monthly may narrow or replace the policy within this law; preserve old files and update the pointer only through a qualified governance transaction.

Pre-Game, Daily, Post-Game and Weekly may start bounded work under valid standing authority without a fresh Pre-Game AUTH token. Existing valid owners take precedence; historical AUTH and delegation records are replay evidence and cannot reopen a completed slice. Pre-Game selects and prepares work rather than becoming a mandatory permission hop.

Before acting, validate a concrete request with `python -m automation.cli validate-standing-request --request REQUEST.json --now CURRENT_UTC`, inspect the accepted quest/proposal and recheck current ownership. The helper checks role/scope/path/budget structure, not scientific truth. Role contracts specify the request and receipt fields.

Limits per trigger: Daily and Post-Game each have one independently owned acceptance slice; Pre-Game two maintenance/delivery slices; Weekly four sequential slices; Monthly one coherent governance transaction. A merge completing the same slice is not a new experiment. Constitutional experimental ceilings are 64 worlds, 100,000 records, 600 runtime seconds and 100 MB per trigger; stricter protocol limits take precedence. Budgets are aggregate across a trigger and remain bounded by any stricter frozen experiment contract. Refresh source/ownership after every accepted transition. One acceptance slice has one current owner, at most one live implementation PR and one budget-consuming implementation receipt. Linked continuation/correction receipts do not grant repeat scientific attempts.

Historically Weekly could activate or terminalize accepted quests; **under the human-approved November Wheel v3 it proposes rather than activates/retires quests**. Monthly/human owns strategic membership changes. Daily-wheel agents may select any ready, unowned, already-active quest within standing scope without a new permission step. Activation and closure remain evidence-based and cannot exceed accepted capacity. Preserve the quest and negative outcomes, reconcile all queue/graph/memory views together, and distinguish route falsification from whole-quest retirement. New quests require a unique ID, artifact, falsifier, budget, scope and accepted proposal; no silent ninth quest. Raw v1 quest-action files remain immutable proposals; delegated enactment is recorded in the standing execution receipt and disposition ledger, not by changing a proposal into an enacted v1 record. Strategic priority changes, consolidated beliefs and protected scientific choices remain Monthly/human responsibilities.

## Backlog completeness and direction

Monthly periodically owns exhaustive PR/issue and quest-action dispositions. Weekly focuses on external papers, checking owners only to avoid colliding with live work. Pre-Game inspects live scientific owners, immediate blockers and yesterday's critique, not the full administrative queue. Preserve old dispositions; pending clerical work is review debt, not permission to block independent science.

Prefer valid owners and graph-ready active quests by scientific leverage, feasibility and coverage of the eight paths; the old index is guidance, not a command to replay a consumed experiment. Local blockers exclude only their own route; shared/global blockers need demonstrated dependencies. Continue independent lawful work. No acknowledgement-only run when an executable artifact is available. Scientific failure is a legitimate completed measurement; closures alone are not research throughput.

## Post-Game independent research

Post-Game begins after Daily but does not need Weekly permission for work already covered by the accepted active quest and standing policy. It reads the latest accepted or blocked Daily result, challenges the inference, then completes at most one non-duplicative bounded research or source-appraisal slice. It must not acquire competing ownership or regenerate a consumed experiment. A new experiment requires a prospective freeze and preflight authority check. A candidate issue or draft PR is not an executable quest. Post-Game may not activate or close quests, rewrite the evaluator/holdout/policy/runtime, or pause other tasks. A local block must cause a documented independent fallback search; lack of executable work must be demonstrated rather than assumed.

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

Attempt GitHub before claiming repository unavailability. Google Drive is design/memory and accepted mirrors; first fetch the canonical router https://docs.google.com/document/d/1rTEVJyZzAr8oS199alaNgpHlc6wZeifUckQgiwUJRog/edit, then only relevant State/project detail. GitHub remains authoritative. Google Calendar records consequential gates and the current policy's review, not routine chatter. Wolfram is optional independent arithmetic/formal checking; unavailable Wolfram does not block standard-library provenance or independent work. No tool may supply invented experimental evidence.

User-selected active slots prioritize Pre-Game, Daily, Post-Game and Weekly; Observatory can remain paused for compute savings. Aurora Daily Vector is retired by the explicit October 31 human organizational decision, only after the independently reviewed Post-Game role is accepted and the external scheduler swap succeeds. Monthly remains configured but normally paused; do not silently enable Monthly or Observatory or spend additional scheduler slots. Do not silently treat a Calendar entry as a scheduler toggle or pause other loops after a local failure.

## Done

Finish with accepted artifact and scientific effect, limits, exact source/head, actual checks/review, receipt, consumed scope and one concrete next move. Where no scientific artifact qualified, say so first; distinguish a local stop from a demonstrated global lack of executable research. At the applicable policy review compare accepted experimental artifacts, evidence-backed quest dispositions, waiting time and human interventions. Treat these as diagnostics, not quotas; inspect scientific effect, retained negative evidence and unresolved limitations. Count administrative work separately; do not reward closure quotas or duplicated prose.
