# SIM2 observation-eligibility audit

Status: qualified candidate at **[Mechanism] / measurement-integrity** level. This is a zero-world source-semantics audit of the accepted QST-SIM-0002 comparison, not a new experiment.

## Question and falsifier

The accepted survey comparison reports a ten fresh-bin-minute advantage in each rotation regime. Does its credited observation stream demonstrate that sensing occurred only in a sensing-eligible operating mode?

The concern would be rejected if the implemented credit predicate tested an explicit valid sensing mode for every credited event. It is confirmed at source-semantics level if credit depends only on scout/sensor role.

## Result

The concern is **confirmed for the synthetic metric**:

- The prospectively frozen protocol explicitly declares that every simulated step from a scout or sensor is recorded.
- The comparison runner implements that role-only rule. Its credit predicate contains no operating-mode check.
- Baseline scout/sensor agents can be in HARVEST or SLEEP; the survey policy can return HARVEST, IDLE, MOVE, SCOUT, or SLEEP. Role-only credit does not distinguish those modes.
- AsteroidWorld.region_id(theta) maps agent angular position to a bin and does not directly use body rotation. Rotation still affects illumination, energy and policy conditions; this audit does not claim rotation is irrelevant to the simulation.
- The accepted result stores aggregate case metrics but no timestamped observation or occupancy trace. Equal endpoint deltas therefore cannot distinguish identical event histories from different histories collapsed by the summary.

The accepted +0.007575757575757569 survey advantage remains a valid result for the **declared role-only synthetic metric**. It is not evidence that all credited events represent operational sensing, nor a rotation-sensitive physical or mission outcome.

Machine-readable evidence: outputs/qst_sim_0002/observation_eligibility_audit.json.

## Confidence separation

| Claim | Internal confidence | External confidence |
| --- | --- | --- |
| Credit is role-only and mode-agnostic in the accepted implementation | **⬆️** — deterministic AST/source audit with byte hashes and reproduction test | **UNKNOWN** — no external sensing-performance source is involved |
| Credited events represent operational sensing | **⬇️ / not demonstrated** — eligibility is not modeled | **UNKNOWN** |
| The two rotation regimes had identical event occupancy | **UNKNOWN** — accepted output has no event trace | **UNKNOWN** |

These directions are not averaged into one score.

## Boundaries and next discriminating test

No world or record was generated. The frozen experiment, accepted four-case result, evaluator, policy parameters and endpoint are unchanged. This audit makes no hardware, asteroid, mission-value or statistical-significance claim.

Before any future non-repeated SIM2 comparison, prospectively freeze event telemetry containing timestamp, role, operating mode, sampled region and an explicit sensing-eligibility predicate. A separately authorized result can then distinguish:

1. identical event occupancy across regimes, which would show the fixture is non-discriminating for this question; from
2. distinct occupancy with the same aggregate, which would show information loss in the summary endpoint.

Independent fallback: the active QST-CALENDAR-0001 deterministic proposal-staging and duplicate-rejection route. Weekly-owned PR #140 remains untouched.
