# AURORA: Evidence Compass

AURORA is the repo's session compass. It rewards reality contact, not volume of prose.

## Spawn

Read:

1. `memory/mem_log_short.md`
2. `quests/active/README.md`
3. latest weekly and monthly calendar entries
4. the relevant system or ARCI doc

## Score

Record:

`A = r ∠ θ | w_ext = e`

Where:

- `r` is evidence depth in `[0, 1]`
  - `0.2`: idea or note
  - `0.4`: specification with acceptance criteria
  - `0.6`: runnable change
  - `0.8`: runnable, tested, and documented
  - `1.0`: reproducible comparison with explicit uncertainty
- `θ` is direction
  - `0°`: model validity and simulation correctness
  - `45°`: ARCI / measurement language
  - `90°`: research synthesis and hypothesis expansion
  - `-45°`: system engineering and energy-chain architecture
  - `-90°`: tooling, packaging, CI, and calendar plumbing
  - `180°`: public narrative and documentation
- `w_ext` is the weight of external evidence used in the session

## Evidence gate

Before raising `r`, ask:

- What changed in the model or artifact?
- What measurement, test, or source supports it?
- What remains placeholder or speculative?
- What result would falsify the current belief?

## Four-axis audit

Optionally record scores from 0–3:

- Evidence
- Coherence
- Safety / governance
- Usefulness

## Next spawn point

Write one action only in `memory/mem_log_short.md`. It must produce a file, test, plot, table, metric, or documented decision.
