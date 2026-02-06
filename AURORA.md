# AURORA — Spawn Compass + Scoring

## Spawn Compass
Read these before any work session:
1. `memory/mem_log_short.md`
2. `quests/active/README.md`
3. Latest `calendar/roundups/` entry + `calendar/monthly/` (if available)
4. This file (`AURORA.md`)

## Aurora Score
Write one line after each session using polar complex form:

`A = r ∠ θ`

Where:
- `r ∈ [0, 1]` measures how real the progress was.
  - 0.0 = ideas only
  - 0.3 = spec + acceptance criteria
  - 0.6 = runnable change + logs
  - 0.8 = runnable + test + plot
  - 1.0 = reproducible + compared baseline + documented
- `θ` encodes direction (what kind of work moved forward).
  - 0° = simulation correctness (models, math, validity)
  - 90° = theory expansion (speculative physics scaffolding)
  - -90° = engineering plumbing (CLI, configs, tests, packaging)
  - 180°/-180° = narrative/docs/public artifact polish

Optional external context weight (calendar-informed):
- `w_ext ∈ [0, 1]` expresses how much external signals influenced the session.
- Suggested source: average `weight` from the latest belief ledger entries.
- Include it inline when relevant: `A = r ∠ θ | w_ext = 0.3`.

Optional tiny vector beneath the score:
- Evidence (0–3)
- Coherence (0–3)
- Ethics/Safety (0–3)
- Resonance (0–3)

## Next Spawn Point
Record the next concrete move in `memory/mem_log_short.md` under **Next Move (one shot)**.
