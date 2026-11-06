# SNS-S-S Research Relay repair | November 6, 2026

**Historical proposal, superseded by the human-authorized SNS Research Wheel v3.** See `docs/research/SNS_RESEARCH_WHEEL_V3.md` and the accepted current standing policy for live instructions. The original draft below is retained as the audit trail, not an active veto.

Status: **human-proposed, review-only**. This document does not itself grant runtime authority, accept an experiment, change a schedule or direct a merge.

## Mechanism

The agents are not meant to share conversational memory. They share **accepted GitHub evidence and its unresolved question**:

accepted measured result → independently appraised uncertainty → prospectively validated test or counterexample → accepted result → next question.

Fresh GitHub HEAD, policy and ownership are verified each run. Previous questions are *leads*, never authority. Do not confuse a current scientific question with an accepted result or with a permission token.

No new tracking infrastructure: use existing PR/issue discussions for unqualified leads, existing `docs/` or tests/outputs for qualified science, existing immutable v2 run receipts for implementation and the Weekly roundup / short memory for durable accepted direction. Agents must not edit another agent's live owned slice.

## Observed failures and repair levers

| November evidence | Root failure | Proposed response |
| --- | --- | --- |
| #146 synchronized earlier lifecycle rows; #147 synchronized #146; after #147 merged, its own row still says `merge_ready` | GitHub merge truth and a self-referential local lifecycle snapshot treated as identical | Do not create a reconciliation PR for a lifecycle-only reconciliation PR. Correct a discrepancy only if an actual handoff/merge/qualification is blocked. Leave harmless history lag inspectable. |
| Short memory still tells Daily to run the Nov 1 four-case SIM2 matrix | Next-action pointer can outlive completed work | Weekly repairs scientific next move at accepted transitions; every agent checks consumed IDs and live evidence instead of blindly following short memory. |
| Daily Nov 5 stopped at SYNTH A1, although independent non-generating SIM2/PV questions existed | Local blocker mistaken for global research stop | Test an independent current active quest candidate and document blockers before global NO_ACTION. |
| Post-Game Nov 2–5 produced source-derived findings only in issues #30 and #103 | Critical findings are communicated but never qualified as reproducible outputs | Issue comments remain hypotheses; Post-Game uses its existing implement authority to qualify a minimal docs/test artifact plus ordinary v2 receipt, or reports an explicit incomplete state. |
| Exact same scheduler instructions say to discard next-action state | Freshness interpreted as abandoning inquiry | Preserve fresh source binding while recovering unverified questions from cited accepted evidence. |

## First science acceptance test: SIM2 observation eligibility

Source: accepted four-case matrix in `outputs/qst_sim_0002/rotation_policy_comparison.json`, `experiments/sim2_rotation_policy_comparison.py`, `src/world/asteroid_world.py` and `src/agents/sns_agent.py`.

Hypothesis to test, **not an accepted result**: current observation credit is awarded for all scout/sensor steps regardless of requested operating mode, while region identity derives from the agent's `theta` and not directly from body rotation. The identical +10 fresh-bin-minute aggregate may therefore mask observation eligibility or weak sensitivity to rotation. Rotation still changes illumination and possibly energy; that does not establish real sensing.

Smallest lawful next slice: independently inspect and document the frozen observation/eligibility mapping and produce a non-generating, source-bound diagnostic or regression demonstrating which modes and timestamps contribute coverage. Freeze its expected behavior and falsifier *before* any new experimental comparison. Do not modify the accepted four-case outputs, retune the policy, or run a fifth world. Owner: next available Daily or Post-Game, not both. Prefer a separate interpretation appendix over silently rewriting frozen endpoints.

Falsifiers: if the code does gate observations by sensing-capable mode, reject the eligibility hypothesis. If two rotation regimes produce distinguishable event occupancy despite the same aggregate, reject the stronger identical-history hypothesis and record summary-metric information loss instead. Event-level traces must be reproduced before claiming either.

Fallback: prospectively review the SYNTH A1 exact-exhaustion versus first-unserved cutoff definition in development-only analytic fixtures, without accepting R2 semantics or opening the sealed holdout. Weekly-owned PV PR #140 must not be concurrently taken by Daily.

## Operational acceptance tests after review

1. **No infinite maintenance chain:** #147 is confirmed merged yet `automation/pr_lifecycle/147.json` says `merge_ready`. The next Pre-Game must not create #148 solely to repair that row. A substantive P1/P2 review/qualification blocker may still require a valid, separately scoped repair.
2. **No stale science replay:** no agent regenerates the consumed four SIM2 worlds, SIM3 #134 world, or sealed SYNTH holdout merely to regain context.
3. **Work-conserving fallback:** on a local SYNTH R2 stop, Daily either completes an independent lawful scientific artifact or cites at least one separately checked active-quest blocker.
4. **Post-Game qualification:** accepted independent contribution includes existing preflight, immutable v2 receipt, source-bound artifact and qualifying checks; an issue-only critique is explicitly noncanonical.
5. **Scientific honesty:** model energy conservation alone does not prove correct cutoff or physical thermostat timing; source-interpretation notes do not become flight claims.
6. **Publication discipline:** no reserved human authority, tests, security, experimental ceilings or historical receipts are weakened.
7. **Seven-day outcome:** count qualified scientific/protocol artifacts, non-generating falsifiers, active candidate-to-qualified-result latency, repeat worlds, admin-only PRs and human rescues. A green CI or a large PR count is not the success metric.
8. **Exit option:** if Pre-Game remains mainly an administrative PR generator and Daily still cannot turn inherited questions into qualified work, treat this repair as falsified. Propose an explicit human-approved one-week *two-agent* Daily + Post-Game pilot with Pre-Game paused, using Weekly for backlog work. Do not toggle tasks automatically.

## Rollout, not a silent switch

This PR deliberately remains **draft**. Changes to `AGENTS.md`, role contracts and the bootloader are reserved human-owned organization changes. Require exact-head hosted CI, semantic review, and human merge authorization. After acceptance, compare the generated bootloader prompts to all four saved automation prompts and update those prompts explicitly under human control; do not change task enablement, cadence, optional connector attachment or the user's planned Saturday manual Observatory update.

A live scheduled run before merge still follows the currently accepted main and existing prompts. PR #140 remains Weekly-owned and open with an unresolved receipt P1; PR #132 remains draft. Monthly may remain paused until needed. Review outcome at the November 15 scientific gate.
