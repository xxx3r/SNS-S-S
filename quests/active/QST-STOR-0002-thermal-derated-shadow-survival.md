# QST-STOR-0002: Thermal-Derated Shadow Survival

Status: Active  
Priority: P0  
Tags: [STOR, THERMAL, SIM]

## Hypothesis

A small SNS survival battery remains credible only when temperature-dependent capacity, heater load, eclipse duration, phase-change buffering, geometry-derived thermal properties, and a closed node mass budget are modeled together.

## Method

- Extend the storage geometry audit with battery and core temperature.
- Add heater thresholds and load.
- Add a phase-change thermal buffer with explicit mass and latent heat.
- Derive heat capacity and conductance from explicit 10 mm geometry.
- Sweep shadow duration, initial temperature, PCM mass, and duty cycle.
- Constrain PCM to a fraction of fixed total node mass and reduce displaced sensible capacity proportionally.

## Success criteria

- One reproducible parameter sweep.
- Electrical and thermal assumptions declared in config.
- PASS / FAIL distinguishes geometry survival from temperature survival.
- At least one case shows where PCM helps and where it cannot.
- Placeholder thermal properties are replaced by traceable geometry-derived ranges.
- Apparent survivors are rejected when their support mass exceeds the node envelope.

## Current evidence

The geometry-derived properties were first propagated through a 243-case Cartesian sweep spanning three conductance cases, eclipse durations of 0.5/1/2 h, initial temperatures of 263.15/273.15/283.15 K, PCM masses of 0/0.5/2 g, and duty cycles of 0.25/0.5/1.0.

Observed aggregate result:

- low-emissivity/no-parasitic: 81/81 combined PASS;
- baseline surface: 6/81 combined PASS, all at 0.5 h;
- high-emissivity/high-parasitic: 0/81 combined PASS;
- electrical margin remains positive in every declared case, while thermal survival collapses as conductance increases.

Every baseline-surface survivor required 2 g PCM, exceeding the 0.789 g geometry-derived total node mass. A second 63-case boundary sweep therefore constrained PCM to 0, 5, 10, 20, 30, 40, or 50 percent of fixed node mass, with PCM displacing baseline sensible material proportionally. It covered the same three initial temperatures and duty cycles at a 30-minute eclipse.

Mass-budget result:

- combined PASS: 0/63;
- thermal PASS: 0/63;
- electrical PASS: 63/63;
- maximum allowed PCM mass in the declared sweep: 0.395 g;
- minimum electrical margin: 0.0782 Wh.

This falsifies the prior 2 g apparent survivor within the current 10 mm baseline-surface envelope. The result remains sensitivity evidence, not hardware qualification. PCM sensible heat, packaging mass, density-driven geometry changes, component gradients, temperature-dependent conductance, view factors, hysteresis, aging, and rate effects remain omitted.

## Artifacts

- `src/sim/thermal_storage.py`
- `src/sim/thermal_geometry.py`
- `experiments/thermal_shadow_survival.py`
- `experiments/derive_thermal_geometry_ranges.py`
- `experiments/thermal_shadow_sweep.py`
- `experiments/thermal_shadow_mass_budget.py`
- `configs/thermal_shadow_survival.json`
- `configs/thermal_geometry_ranges.json`
- `configs/thermal_shadow_sweep.json`
- `configs/thermal_shadow_mass_budget.json`
- `tests/test_thermal_storage.py`
- `tests/test_thermal_geometry.py`
- `tests/test_thermal_shadow_sweep.py`
- `tests/test_thermal_shadow_mass_budget.py`
- `docs/system/thermal_shadow_survival.md`
- `outputs/qst_stor_0002/cases.csv`
- `outputs/qst_stor_0002/summary.json`
- `outputs/qst_stor_0002/thermal_geometry_ranges.csv`
- `outputs/qst_stor_0002/thermal_geometry_summary.json`
- `outputs/qst_stor_0002/geometry_coupled_sweep_summary.json`
- `outputs/qst_stor_0002/baseline_surface_survivors.json`
- `outputs/qst_stor_0002/mass_budget_boundary.json`

## Falsifier

If temperature support mass or heater demand eliminates the 10 mm survival margin across plausible cases, the seed envelope must grow, its thermal conductance must fall materially, or the mission eclipse duty must change.

## Next step

Quantify the conductance reduction required for at least one physically admissible 30-minute baseline case to survive with PCM capped at 50 percent of total node mass. Produce a threshold sweep over effective emissivity and parasitic conductance rather than adding more unconstrained storage mass.
