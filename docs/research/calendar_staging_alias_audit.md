# QST-CALENDAR-0001 | Proposal identity alias audit (2026-11-06)

**Classification:** [Mechanism] / source-level measurement-integrity counterexample; **zero worlds, zero experimental records**.
**Accepted source observed:** `23d3bf568116d42d7ae91d1f8b451c3956299bc3`.
**Quest:** `quests/active/QST-CALENDAR-0001-roundup-parser.md`.
**Independent test:** `tests/test_roundup_staging_whitespace_alias_audit.py`.

## One question

Does the staged proposal pipeline reject visually equivalent IDs for an already-active quest, or can a whitespace alias bypass its duplicate and existing-ID checks?

A negative result is meaningful because QST-CALENDAR-0001's own success criteria require deterministic proposed quests and no duplicate-ID drift. It does **not** claim that staging activates a quest.

## Reproducible source-level counterexample

`src/research/quest_engine.py` uses `str(action["id"])` without stripping or validating the ID before duplicate comparison, active-quest membership and all-quest membership. In a roundup containing the two strings:

| Input | Observed classification in the current source |
| --- | --- |
| `QST-CALENDAR-0001` | `refine_existing` |
| `QST-CALENDAR-0001 ` (trailing space) | `propose_new` |

Two precisely identical raw IDs correctly raise `ValueError`, supplying a positive control. The whitespace pair instead survives staging as two **proposal-only** actions. The focused test imports the actual repository functions and checks all three cases. A separate isolated reconstruction produced the same classifications before publication, but does not replace hosted test evidence.

This finding challenges **proposal identity integrity**, not operational sensing or physical validity. It is distinct from Daily's accepted SIM2 observation-eligibility audit (PR #149), and does not touch PR #140, the sealed SYNTH R2 holdout, an evaluator, or hardware architecture.

## Evidence and confidence

- **Internal confidence, source-semantic claim:** ⬆️ **only when the focused test passes against the exact published source**. A branch-independent source reading and isolated reproduction support the hypothesis; the final exact-head tests determine qualification.
- **Internal confidence, downstream duplicate enactment:** UNKNOWN. No enactment or authority write was attempted; the downstream validator may reject the whitespace ID.
- **External confidence:** UNKNOWN / ↔️. No new primary physical or external research evidence was assessed.
- **[Formula]:** String identity is an exact comparison, not a canonical quest identity invariant.
- **[Mechanism]:** The staging path admits the alias as a proposal.
- **[Implementation]:** No claim of automatic activation, accepted queue mutation, or operational readiness.

## Smallest next falsifier for Pre-Game

Under QST-CALENDAR-0001 and current standing research-tooling authority, test whether the production CLI accepts this same paired fixture into a temporary proposal-only directory, and separately whether downstream quest-action validation rejects the whitespace ID. Avoid actual quest activation. If the CLI already rejects it, this is a lower-level staging inconsistency rather than an end-to-end bypass.

If confirmed at CLI level, propose a subsequent bounded canonical-ID normalization/rejection guard with positive/negative tests, *without retroactively rewriting historical proposals*. The owner and preflight must be freshly checked.

**Independent fallback:** a zero-world, unowned QST-SIM-0002 event-telemetry *specification-only* appraisal that demonstrates which missing observation fields prevent sensing-eligibility and rotation-history claims, with no new world, policy, or evaluator change. If an experiment is wanted, freeze it prospectively and obtain fresh authority first.

**Not an accepted qualified result until:** exact-head full pytest, repository semantic validation, baseline-artifacts, immutable v2 provenance receipt, independent semantic review and expected-head merge all pass.
