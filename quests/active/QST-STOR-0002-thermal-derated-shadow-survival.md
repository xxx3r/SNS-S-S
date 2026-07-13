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

Implemented and artifacted on `aurora/qst-stor-0002-minimal-thermal-shadow`:

- lumped thermal integration with explicit units;
- piecewise-linear battery-capacity derating;
- thermostatic heater load coupled into electrical consumption;
- finite PCM latent-energy buffering;
- separate thermal, electrical, and combined status;
- declared no-PCM, 2 g PCM, and undersized-battery cases;
- focused tests for PCM benefit and limitation;
- checked-in `cases.csv` and `summary.json` from the declared configuration.

Observed model outputs:

- `baseline_no_pcm`: PASS; minimum temperature 255.249 K; heater energy 0.07467 Wh; electrical margin 0.12889 Wh.
- `baseline_with_2g_pcm`: PASS; minimum temperature 258.096 K; heater energy 0.04533 Wh; electrical margin 0.16847 Wh.
- `undersized_battery_with_10g_pcm`: thermal PASS but electrical FAIL; minimum temperature 273.15 K; electrical margin -0.01136 Wh.

Within this placeholder model, 2 g of PCM raises the minimum temperature by 2.847 K and reduces heater energy by 0.02933 Wh, while 10 g of PCM cannot rescue an undersized battery. These are model-behavior checks, not hardware evidence.

Thermal capacitance, conductance, environment temperature, and PCM properties remain placeholders rather than measured SNS values.

## Artifacts

- `src/sim/thermal_storage.py`
- `experiments/thermal_shadow_survival.py`
- `configs/thermal_shadow_survival.json`
- `tests/test_thermal_storage.py`
- `docs/system/thermal_shadow_survival.md`
- `outputs/qst_stor_0002/cases.csv`
- `outputs/qst_stor_0002/summary.json`

## Falsifier

If temperature support mass or heater demand eliminates the 10 mm survival margin across plausible cases, the seed envelope must grow or the mission duty cycle must change.

## Next step

Derive thermal-capacitance and conductance ranges from explicit 10 mm geometry and material assumptions, then run the full eclipse-duration, initial-temperature, PCM-mass, and duty-cycle sweep.
