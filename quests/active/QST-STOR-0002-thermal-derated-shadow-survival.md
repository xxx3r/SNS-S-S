# QST-STOR-0002: Thermal-Derated Shadow Survival

Status: Active  
Priority: P0  
Tags: [STOR, THERMAL, SIM]

## Hypothesis

A small SNS survival battery remains credible only when temperature-dependent capacity, heater load, eclipse duration, phase-change buffering, and geometry-derived thermal properties are modeled together.

## Method

- Extend the storage geometry audit with battery and core temperature.
- Add heater thresholds and load.
- Add a phase-change thermal buffer with explicit mass and latent heat.
- Derive heat capacity and conductance from explicit 10 mm geometry.
- Sweep shadow duration, initial temperature, PCM mass, and duty cycle.

## Success criteria

- One reproducible parameter sweep.
- Electrical and thermal assumptions declared in config.
- PASS / FAIL distinguishes geometry survival from temperature survival.
- At least one case shows where PCM helps and where it cannot.
- Placeholder thermal properties are replaced by traceable geometry-derived ranges.

## Current evidence

The geometry-derived properties are now propagated through a 243-case Cartesian sweep spanning three conductance cases, eclipse durations of 0.5/1/2 h, initial temperatures of 263.15/273.15/283.15 K, PCM masses of 0/0.5/2 g, and duty cycles of 0.25/0.5/1.0.

Observed aggregate result:

- low-emissivity/no-parasitic: 81/81 combined PASS;
- baseline surface: 6/81 combined PASS, all at 0.5 h;
- high-emissivity/high-parasitic: 0/81 combined PASS;
- electrical margin remains positive in every declared case, while thermal survival collapses as conductance increases.

This makes surface emissivity and parasitic heat paths the dominant uncertainty in the current model. The result is sensitivity evidence only. It does not establish a flight-feasible coating, internal architecture, heater, battery, or PCM package.

## Artifacts

- `src/sim/thermal_storage.py`
- `src/sim/thermal_geometry.py`
- `experiments/thermal_shadow_survival.py`
- `experiments/derive_thermal_geometry_ranges.py`
- `experiments/thermal_shadow_sweep.py`
- `configs/thermal_shadow_survival.json`
- `configs/thermal_geometry_ranges.json`
- `configs/thermal_shadow_sweep.json`
- `tests/test_thermal_storage.py`
- `tests/test_thermal_geometry.py`
- `tests/test_thermal_shadow_sweep.py`
- `docs/system/thermal_shadow_survival.md`
- `outputs/qst_stor_0002/cases.csv`
- `outputs/qst_stor_0002/summary.json`
- `outputs/qst_stor_0002/thermal_geometry_ranges.csv`
- `outputs/qst_stor_0002/thermal_geometry_summary.json`
- `outputs/qst_stor_0002/geometry_coupled_sweep_summary.json`

## Falsifier

If temperature support mass or heater demand eliminates the 10 mm survival margin across plausible cases, the seed envelope must grow or the mission duty cycle must change.

## Next step

Validate the committed sweep in CI, then inspect the six baseline-surface 0.5 h survivors to identify the exact PCM, initial-temperature, and duty-cycle combinations that preserve thermal survival.
