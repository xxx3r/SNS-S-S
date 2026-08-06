# Issue #38 Proposal: August Backlog-Clearance Campaign

**Status:** Proposal-only; no execution authority
**Date:** 2026-08-06
**Repository:** `xxx3r/SNS-S-S`
**Tracking issue:** [#38](https://github.com/xxx3r/SNS-S-S/issues/38)
**Source snapshot:** `73225b9d09a43e0e3616250519ec908b7b723c14` (main after merged PR #37)

## 0. Decision boundary

This document freezes a bounded design for the August incident response and backlog-clearance experiment. It is not an execution receipt and does not authorize any queue, belief, memory, contract, quest, or scientific-model mutation.

This proposal explicitly does not:

- create or activate a quest;
- create a duplicate quest branch or implementation PR;
- rewrite `memory/mem_log_short.md` or consolidated beliefs;
- enact monthly queue reprioritization, retirement, blocking, or promotion;
- implement a new connector contract or validator;
- merge any future cleanup PR automatically;
- convert a scientific or evidence gap into clerical work.

After human acceptance, only the sequential clerical and validation transactions in Section 6 may run. Each transaction has one owner, one immutable `RUN-` receipt, and one terminal outcome. The campaign stops immediately at the first scientific uncertainty, governance decision, missing evidence, failed validation, ownership conflict, or reserved-authority boundary.

## 1. Frozen inputs

The proposal is grounded in:

- `AGENTS.md` stable law and its authority order;
- the active daily, monthly, and system-audit contracts;
- `automation/state_ownership.json`;
- Issue #38 incident and campaign requirements;
- the merged PR #37 receipt `RUN-20260806T223500000000Z-daily-research-operator-a17c4e9b2d6f8031c5e7`;
- the active-quest index and all eight active quest records;
- the September cutoff decision at `2026-09-01T14:00:00Z`;
- live GitHub state checked through the GitHub connector on 2026-08-06.

The Google Drive search surface was also checked for SNS-S-S and autonomous-loop source artifacts; no matching Drive file was returned. The repository and the attached Summer 2026 progress report therefore remain the operative sources for this proposal.

## 2. Incident record and failure taxonomy

Issue #38 records a medium-severity, high-audit-value `FALSE_ENVIRONMENT_BLOCKER` with subclass `CONNECTOR_NOT_ATTEMPTED`. The failed response inferred that GitHub was unavailable from the absence of a local shell or clone, even though a healthy GitHub connector was present and returned repository authority.

The incident is classified as a routing failure, not a repository outage, permission failure, scientific failure, or missing-tool event.

Required taxonomy:

| Class | Meaning | Required evidence | Allowed disposition |
|---|---|---|---|
| `FALSE_ENVIRONMENT_BLOCKER` | A blocker was emitted before the required connector probe or without a valid failed operation | connector requirement, attempted flag, target, timestamp, and returned error payload | reject the blocker; record recovery |
| `CONNECTOR_FAILURE` | A required connector operation was attempted and failed | operation, target, provider error code/message, timestamp, retry decision | bounded retry or terminal environment blocker |
| `CONNECTOR_PERMISSION_FAILURE` | The connector responded with deterministic authorization denial | provider response and permission context | stop; do not blindly retry |
| `VALIDATION_FAILURE` | The operation ran but its artifact or record failed executable validation | command/check identity and concrete failure | stop with `VERIFICATION_FAILED` |
| `MISSING_EVIDENCE` | The operation is scientifically or operationally incomplete | named missing artifact, source, or measurement | stop with `BLOCKED_MISSING_EVIDENCE` |
| `GOVERNANCE_REQUIRED` | The next action changes queue, memory, belief, or authority | proposed action and owning authority | stop with `NEEDS_GOVERNANCE_REVIEW` |

A generic statement such as “no live GitHub context” is not a valid environment blocker.

## 3. Connector-preflight hardening design

### 3.1 Preflight record

Every connector-dependent loop should attach a small preflight object to its run receipt or to the versioned run schema proposed by a follow-up implementation PR:

```json
{
  "required_connector": "GitHub",
  "probe_operation": "get_repo",
  "probe_target": "xxx3r/SNS-S-S",
  "attempted": true,
  "succeeded": true,
  "attempted_at": "2026-08-06T22:12:00Z",
  "permission_snapshot": ["pull", "push", "maintain", "admin"],
  "error": null
}
```

A failed probe must preserve the provider response rather than replacing it with generic prose:

```json
{
  "required_connector": "GitHub",
  "probe_operation": "get_repo",
  "probe_target": "xxx3r/SNS-S-S",
  "attempted": true,
  "succeeded": false,
  "attempted_at": "2026-08-06T22:12:00Z",
  "permission_snapshot": null,
  "error": {
    "code": "PROVIDER_CODE",
    "message": "provider-returned message"
  }
}
```

### 3.2 Semantic rules

1. A `BLOCKED_ENVIRONMENT` receipt that requires GitHub is invalid when `attempted` is false.
2. A failed connector receipt must name the connector, operation, target, timestamp, and concrete returned error code/message.
3. A successful preflight must be recorded before research or repository mutation begins.
4. The absence of a local shell, local clone, or optional convenience surface is not evidence that the connector is unavailable.
5. A one-shot retry is permitted only for transient or ambiguous failures and remains inside the contract retry budget.
6. Permission-denied, malformed-target, or deterministic validation failures are not blindly retried.
7. The preflight object must be included in audit metrics so “required,” “attempted,” “succeeded,” and “failed” are countable rather than inferred from prose.

### 3.3 Execution-surface distinction

| Surface | Authority | Not implied by its absence |
|---|---|---|
| GitHub connector | repository, branch, PR, issue, review, and workflow metadata/actions exposed by the connector | local filesystem or shell |
| GitHub Actions | repository-hosted validation and logs | connector availability |
| local shell/clone | optional local inspection and execution convenience | GitHub repository authority |

### 3.4 Required regression fixtures

- Healthy GitHub connector plus an explicitly unavailable local shell: probe GitHub and proceed.
- Failed transient probe: retry once, then record the concrete failure.
- Deterministic permission denial: stop without blind retry.
- Refusal before any probe: reject the blocker record as invalid and count a pre-probe refusal.
- Connector-required run with a valid preflight: ensure the receipt carries the preflight and audit counters see it.

This section is a design freeze only. Schema, validator, contract, fixture, and scheduled-prompt changes require a separate reviewed implementation PR after governance accepts the design.

## 4. Complete active-quest blocker inventory

The active index contains eight canonical quests. QST-STOR-0002 has several evidence-slice files, but they remain one canonical quest and must not be split into duplicate quest branches.

| Canonical quest | Current state | Current blocker | Classification | Campaign disposition |
|---|---|---|---|---|
| `QST-STOR-0002` Thermal-Derated Shadow Survival | Active, P0; package propagation is complete with a thermal package FAIL | Complete-package emissivity and assembled-conductance evidence is missing/unknown; illuminated-state rejection and architecture consequences remain open | substantive scientific work + missing evidence | do not clear clerically; preserve as a scientific handoff |
| `QST-SIM-0002` Asteroid Illumination + Coverage Model | Active, P1; baseline implemented | irregular rotation, configurable shadows, stale-coverage windows, and coordinated-policy comparison remain | substantive scientific work | do not execute in campaign |
| `QST-SIM-0003` GEO Ring Power-Chain Model | Active, P1; baseline implemented | receiver/line-of-sight windows, role-mix/storage sweeps, and relay-loss boundary remain | substantive scientific work | do not execute in campaign |
| `QST-PV-0001` PV Degradation Parameter Sheet | Active, P1 | source-traceable ranges across radiation, thermal cycling, temperature, recovery, and damage conditions remain | scientific work + missing evidence | do not execute in campaign |
| `QST-META-0001` Metasurface Beam-Steering Abstraction | Active, P1 | pure loss model, pointing/error sweep, control-energy cost, and power-beam nonclaim boundary remain | substantive engineering/scientific work | do not execute in campaign |
| `QST-ARCI-0001` ARCI v0.1 Draft + Synthetic Target | Active, P0; scaffold implemented | synthetic target, evidence/missing-data flags, sensitivity, and next-measurement recommendation remain | scientific judgment + missing evidence | do not execute in campaign |
| `QST-CALENDAR-0001` Weekly Roundup → Quest Pipeline | Active, P1; parser implemented | staging CLI and duplicate-ID validation are potentially clerical/validation; belief append and a real Sunday roundup require evidence and governance | mixed: safe validation subset plus reserved evidence/governance | only deterministic validation may enter the campaign; stop before belief or queue mutation |
| `QST-FUND-0001` Summer 2026 Public Artifact | Active, P1 | claim labeling, reproducible figures/tables, technical synthesis, and expert-critique framing remain | substantive narrative/evidence work | do not execute in campaign except mechanical link/check validation |

QST-STOR-0002 sub-slice status:

- the architectural escape comparison is complete with limitations;
- mission-shadow feasibility is implementation-complete but its record still says full CI verification is pending;
- the mission-dependency configuration slice is now merged through PR #37 with the corrected comparator and immutable receipt;
- the thermal package evidence gate remains scientific and is not backlog debris.

## 5. Non-quest transaction debris

The live connector inventory found no open GitHub PRs after PR #37 merged. The repository’s historical lifecycle records nevertheless contain stale states that are safe candidates for a governed clerical campaign:

| Surface | Repository record | Live GitHub fact | Classification |
|---|---|---|---|
| PR #22 lifecycle | `automation/pr_lifecycle/22.json` says `draft_active` | PR #22 is closed and merged on 2026-07-31 | clerical lifecycle reconciliation |
| PR #23 lifecycle | `automation/pr_lifecycle/23.json` says `draft_active` | PR #23 is closed unmerged; its useful content was recovered through merged PR #34 | clerical lifecycle reconciliation / supersession evidence |
| PR #37 lifecycle | no current lifecycle record was found in the frozen inventory | PR #37 is merged on 2026-08-06; receipt exists, lifecycle closure record is still absent | clerical lifecycle record creation |
| `memory/mem_log_short.md` | canonical next move still says to add the matched dependency ledger | PRs #35, #36, and #37 already completed that slice | governance-owned stale-next-move reconciliation; not safe daily cleanup |
| open-PR ownership | historical baseline lists old owners | current live open-PR inventory is empty | validation/reporting cleanup; do not rewrite the historical baseline |

No quest is proposed for these observations. They are state-reconciliation targets only.

## 6. Frozen sequential clearance campaign

The campaign is intentionally sequential. The next transaction cannot begin until the previous transaction has a receipt and terminal state. “One owner” means one named authority owns the transaction; “one receipt” means exactly one new immutable run receipt for that bounded attempt. Corrections use a linked new receipt and never overwrite the original.

| Order | Bounded transaction | Owner | Safe terminal outcomes | Stop condition |
|---:|---|---|---|---|
| 1 | Record the merged terminal disposition of PR #37 in the PR-lifecycle surface, referencing its immutable receipt and merge commit | monthly governance / explicit human | `DONE` or `DONE_WITH_LIMITATIONS` | missing owner receipt, source conflict, or lifecycle schema failure |
| 2 | Reconcile PR #22 from `draft_active` to its verified merged terminal state without changing QST-STOR-0002 science | monthly governance | `DONE` | merge identity or owner evidence cannot be verified |
| 3 | Reconcile PR #23 as superseded/closed by the recovered PR #34 path, preserving the historical branch and no-op scientific state | monthly governance | `DONE_WITH_LIMITATIONS` | supersession relation or evidence is ambiguous |
| 4 | Produce a current open-PR/branch ownership validation view; do not edit the historical July baseline | system audit | `DONE` | connector inventory disagrees with repository state |
| 5 | Validate active-queue IDs, README membership, cross-queue uniqueness, and the no-duplicate-branch invariant | system audit | `DONE` or `VERIFICATION_FAILED` | duplicate ID, missing record, or queue authority mutation would be required |
| 6 | Validate that recent receipts cite existing artifacts and that receipt IDs are unique and schema-conformant | system audit | `DONE` or `VERIFICATION_FAILED` | missing artifact, duplicate receipt, or invalid immutable ID |
| 7 | Emit a proposal-only governance handoff for the stale canonical next move; do not edit short memory | monthly governance proposal | `NEEDS_GOVERNANCE_REVIEW` | any request to rewrite memory without accepted monthly authority |
| 8 | Review the connector-preflight design and decide whether a separate implementation PR is authorized | human / monthly governance | `NEEDS_APPROVAL` or `NEEDS_GOVERNANCE_REVIEW` | contract/schema or scheduled-prompt changes are requested without authority |

The campaign ends after transaction 6 if transactions 7–8 remain undecided. It does not automatically open new research quests, promote ARCI, activate synthetic-worlds work, or alter the monthly objective set.

## 7. Stop conditions and handoff protocol

Stop and publish the current receipt when any of the following occurs:

- a quest requires a new measurement, model assumption, literature interpretation, or architecture choice;
- evidence is absent, stale, contradictory, or not package-level where package-level evidence is required;
- a queue, memory, belief, active-quest, or PR-ownership mutation needs monthly governance;
- a validation command fails or its execution surface is unavailable;
- a connector probe fails without a concrete returned error payload;
- a second owner, duplicate branch, or conflicting PR appears;
- the next action would change a contract, schema, scheduled prompt, or reserved authority;
- a human must choose between scientific routes or approve a new research quest.

The handoff receipt must name the exact authority, unresolved question, evidence needed, and one concrete next action. It must never claim a repository outage merely because an optional local surface is absent.

## 8. September 1 audit scoreboard

At `2026-09-01T14:00:00Z`, record the exact `main` commit as `cutoff_commit`. Receipts before the cutoff count as completed; same-time, later, unresolved, or unmerged work is reported as in-flight/excluded.

| Metric | Definition | Source | Target or interpretation |
|---|---|---|---|
| Connector-required runs | Runs whose active contract/acceptance slice requires a connector | run receipts and preflight fields | denominator for connector-routing reliability |
| Connector-attempt rate | attempted required probes / connector-required runs | preflight receipts | target 100% |
| Connector success rate | successful probes / attempted probes | preflight receipts | report by connector and loop |
| Concrete-error completeness | failed probes with code, message, target, operation, and timestamp / failed probes | preflight receipts | target 100% |
| False environment blockers | `BLOCKED_ENVIRONMENT` claims with no attempted failed operation | receipts plus validator findings | target 0; August incident is baseline evidence |
| Pre-probe refusals | refusals emitted before first mandatory connector probe | receipt terminal state and preflight audit | target 0 |
| Human recoveries | runs requiring explicit human correction after routing failure | linked receipts and issue comments | report count and loop type |
| Lost scheduled opportunities | scheduled runs not reaching a valid probe or artifact | schedule/run reconciliation | report count; do not infer scientific loss |
| Blockers removed per run | newly terminal clerical/validation blockers divided by campaign receipts | campaign receipts | descriptive efficiency metric |
| Receipt coverage | bounded transactions with one valid immutable receipt / bounded transactions attempted | `automation/runs/**` | target 100% |
| One-owner compliance | transactions with one current owner and no overlapping owner / transactions | PR lifecycle and receipts | target 100% |
| Duplicate-work rate | duplicate quest branches, duplicate owners, or duplicate receipt IDs | validator and branch inventory | target 0 |
| Validation pass rate | executed validation checks passed / executed validation checks | receipt checks and Actions | report separately from not-run |
| Stale-next-move age | days between completed evidence and unchanged canonical move | memory, receipts, merge commits | report age; governance metric, not a failure of science |
| PR turnaround | time from branch/PR creation to terminal disposition | GitHub metadata and lifecycle records | report median and outliers |
| Human interventions per artifact | human interventions / artifact-bearing completed transactions | receipts and comments | report, do not optimize by suppressing handoffs |
| Scientific-evidence fraction | artifact-bearing transactions producing new evidence / all artifact-bearing transactions | receipt artifacts and evidence IDs | distinguish research from administration |
| Unauthorized quest activation | active quest promotions without monthly authority | quest actions and queue diff | target 0 |
| Information inheritance | later receipts explicitly citing an earlier receipt/evidence/quest-action ID and recording decision effect | receipts | report count and fraction |
| Subsequent quest novelty/difficulty | post-campaign quests’ new evidence dimensions and unresolved uncertainty | later monthly governance records | qualitative/quantitative follow-up, not a clearance target |

The scoreboard must preserve denominators, excluded work, and not-run checks. It must not convert administrative movement into scientific progress or treat a lower intervention count as inherently better.

## 9. Acceptance criteria for this plan PR

This plan is accepted only when a human or the authorized monthly-governance process confirms:

1. the proposal-only boundary;
2. the active-quest inventory and blocker classifications;
3. the exact sequential order and one-owner/one-receipt rule;
4. the connector-preflight design and regression matrix;
5. the September scoreboard definitions and cutoff handling;
6. the stop conditions and handoff protocol.

Acceptance of this plan does not itself accept any scientific hypothesis, activate any quest, rewrite memory, consolidate beliefs, or authorize implementation of the preflight schema. Those are separate decisions.
