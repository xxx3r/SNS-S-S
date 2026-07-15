# AURORA: Evidence Compass

AURORA scores reality contact after the active loop contract has governed execution. It is not the transaction engine, queue authority, spawn procedure, or mutable history.

## Score

Record `A = r ∠ θ | w_ext = e` in the run receipt or accepted human-facing summary.

- `r` is evidence depth in `[0, 1]`:
  - `0.2`: idea or note;
  - `0.4`: specification with acceptance criteria;
  - `0.6`: runnable change;
  - `0.8`: runnable, tested, and documented;
  - `1.0`: reproducible comparison with explicit uncertainty.
- `θ` is direction:
  - `0°`: model validity and simulation correctness;
  - `45°`: ARCI and measurement language;
  - `90°`: evidence synthesis and hypothesis expansion;
  - `-45°`: system engineering and energy-chain architecture;
  - `-90°`: tooling, CI, calendar, and transaction infrastructure;
  - `180°`: public narrative and documentation.
- `w_ext` is the weight of external evidence actually consumed.

## Evidence gate

Before raising `r`, ask:

- What inspectable artifact changed?
- Which check, measurement, or normalized evidence event supports it?
- What remains placeholder, speculative, blocked, or unverified?
- What would falsify the current claim?
- Did a later run explicitly inherit this result?

## Four-axis audit

Optionally record 0–3 scores for Evidence, Coherence, Safety/Governance, and Usefulness.

AURORA rewards tested artifacts, explicit uncertainty, informative failure, and evidence that changes later decisions. It does not reward duplicated prose, queue sediment, branch churn, or unsupported certainty.
