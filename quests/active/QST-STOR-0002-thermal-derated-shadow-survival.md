# QST-STOR-0002: Thermal-Derated Shadow Survival

Status: Active  
Priority: P0  
Tags: [STOR, THERMAL, SIM]

## Hypothesis

A small SNS survival battery remains credible only when temperature-dependent capacity, heater load, eclipse duration, and phase-change buffering are modeled together.

## Method

- Extend the storage geometry audit with battery and core temperature.
- Add heater thresholds and load.
- Add a phase-change thermal buffer with explicit mass and latent heat.
- Sweep shadow duration, initial temperature, PCM mass, and duty cycle.

## Success criteria

- One reproducible parameter sweep.
- Electrical and thermal assumptions declared in config.
- PASS / FAIL distinguishes geometry survival from temperature survival.
- At least one case shows where PCM helps and where it cannot.

## Current evidence: minimal 2-hour slice

Implemented on `aurora/qst-stor-0002-minimal-thermal-shadow`:

- lumped thermal integration with explicit units;
- piecewise-linear battery-capacity derating;
- thermostatic heater load coupled into electrical consumption;
- finite PCM latent-energy buffering;
- separate thermal, electrical, and combined status;
- declared no-PCM, 2 g PCM, and undersized-battery cases;
- focused tests for PCM benefit and limitation.

This slice establishes model plumbing and acceptance semantics. Its thermal capacitance, conductance, environment temperature, and PCM properties remain placeholders rather than measured SNS values.

## Artifacts

- `src/sim/thermal_storage.py`
- `experiments/thermal_shadow_survival.py`
- `configs/thermal_shadow_survival.json`
- `tests/test_thermal_storage.py`
- `docs/system/thermal_shadow_survival.md`
- `outputs/qst_stor_0002/` after running the declared experiment

## Falsifier

If temperature support mass or heater demand eliminates the 10 mm survival margin across plausible cases, the seed envelope must grow or the mission duty cycle must change.

## Next step

Run the declared cases in CI/local execution, save the output artifacts, then replace placeholder thermal properties with geometry-derived ranges for the full sweep.
