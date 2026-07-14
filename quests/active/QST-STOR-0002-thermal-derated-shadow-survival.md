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

The minimal coupled model and checked-in two-hour cases remain reproducible. The geometry-range slice now adds:

- a 10 mm outer sphere with an explicit 8 mm core and shell volume;
- component density and specific-heat inputs;
- linearized radiative conductance from emissivity, area, and temperature;
- separately declared parasitic conductance;
- three low/baseline/high-loss cases, focused tests, and CSV/JSON artifacts.

For the declared baseline composition, total mass is 0.789 g and lumped heat capacity is 0.741 J/K. Total conductance spans 7.01e-5 to 2.12e-3 W/K across the declared surface/parasitic cases. The previous 50 J/K placeholder is therefore about 67 times larger than this first geometry-derived estimate. This strongly weakens the prior thermal-inertia assumption but is not yet hardware evidence because component packing, coatings, internal interfaces, and material selections remain provisional.

## Artifacts

- `src/sim/thermal_storage.py`
- `src/sim/thermal_geometry.py`
- `experiments/thermal_shadow_survival.py`
- `experiments/derive_thermal_geometry_ranges.py`
- `configs/thermal_shadow_survival.json`
- `configs/thermal_geometry_ranges.json`
- `tests/test_thermal_storage.py`
- `tests/test_thermal_geometry.py`
- `docs/system/thermal_shadow_survival.md`
- `outputs/qst_stor_0002/cases.csv`
- `outputs/qst_stor_0002/summary.json`
- `outputs/qst_stor_0002/thermal_geometry_ranges.csv`
- `outputs/qst_stor_0002/thermal_geometry_summary.json`

## Falsifier

If temperature support mass or heater demand eliminates the 10 mm survival margin across plausible cases, the seed envelope must grow or the mission duty cycle must change.

## Next step

Feed the geometry-derived heat-capacity and conductance cases into the coupled shadow model and run the full eclipse-duration, initial-temperature, PCM-mass, and duty-cycle sweep.
