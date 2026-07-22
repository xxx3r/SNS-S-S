# QST-STOR-0002: Thermal-Derated Shadow Survival

Status: Active  
Priority: P0  
Tags: [STOR, THERMAL, SIM]

## Hypothesis

A small SNS survival battery remains credible only when temperature-dependent capacity, heater load, eclipse duration, phase-change buffering, geometry-derived thermal properties, a closed node mass budget, and environmentally qualified surface/interface evidence are modeled together.

## Method

- Extend the storage geometry audit with battery and core temperature.
- Add heater thresholds and load.
- Add a phase-change thermal buffer with explicit mass and latent heat.
- Derive heat capacity and conductance from explicit 10 mm geometry.
- Sweep shadow duration, initial temperature, PCM mass, and duty cycle.
- Constrain PCM to a fraction of fixed total node mass and reduce displaced sensible capacity proportionally.
- Sweep effective emissivity and parasitic conductance under the most favorable declared admissible mass-budget case.
- Translate the resulting loss boundary into a qualification-style evidence checklist that separates coupon properties from complete-package performance.
- Close one explicit package architecture by summing supports, wiring, adhesive bonds, PV hinge/traces, feedthroughs, and PCM containment with `G = kA/L` and a declared uncertainty multiplier.

## Success criteria

- One reproducible parameter sweep.
- Electrical and thermal assumptions declared in config.
- PASS / FAIL distinguishes geometry survival from temperature survival.
- At least one case shows where PCM helps and where it cannot.
- Placeholder thermal properties are replaced by traceable geometry-derived ranges.
- Apparent survivors are rejected when their support mass exceeds the node envelope.
- The first declared emissivity/parasitic-loss survivor is recorded without treating an effective parameter as a qualified material claim.
- Candidate thermal paths distinguish measured, inferred, heritage, proposed, and unknown evidence.
- Promotion requires package-level emissivity and assembled-conductance evidence after uncertainty and environmental margins.
- At least one complete screening package reports every conductive path, dominant contributors, uncertainty multiplier, and margin against the `5e-5 W/K` proxy target.

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

A third 42-case boundary sweep held the deliberately favorable admissible case fixed at 283.15 K initial temperature, 50% PCM mass fraction, and 25% duty cycle while varying effective emissivity and parasitic conductance.

Loss-boundary result:

- combined PASS: 18/42;
- electrical PASS: 42/42;
- effective emissivity 0.2: 0/7 PASS, including zero parasitic conductance;
- effective emissivity 0.15: 0/7 PASS;
- first declared survivor: effective emissivity 0.1 with parasitic conductance 5e-5 W/K;
- first-survivor total conductance: 1.9025e-4 W/K;
- first-survivor minimum temperature: 238.98 K;
- first-survivor electrical margin: 0.0880 Wh.

This converts the thermal blocker into an inspectable target: the current proxy needs effective emissivity below the baseline 0.2 and tightly bounded parasitic leakage. The result is a model boundary, not proof that a realizable coating/interface stack can achieve it. PCM sensible heat, packaging mass, density-driven geometry changes, component gradients, temperature-dependent conductance, exact radiative exchange, view factors, hysteresis, aging, and rate effects remain omitted.

The evidence checklist compared this boundary against NASA and ESA primary/heritage sources. NASA's May 2026 Small Spacecraft Technology review gives a low-emissivity SmallSat coating example near 0.25 and warns that low thermal mass, limited MLI volume, interfaces, and MLI edge effects control transients. LDEF heritage reports clear chromic anodized aluminum near 0.16. MLI and foil shields can lower effective emittance, but their performance is installation-, seam-, contact-, pressure-, and scale-dependent. No reviewed source demonstrates a complete wired, penetrated, deployable 10 mm package simultaneously meeting `epsilon_eff <= 0.10` and `G_parasitic <= 5e-5 W/K` after environmental margins.

Evidence-gate result:

- emissivity path: **HOLD / MISSING PACKAGE EVIDENCE**;
- parasitic-conductance path: **UNKNOWN / NO FULL-ASSEMBLY BUDGET**;
- no candidate material or architecture is promoted as an SNS package solution;
- a full assembly must be evaluated for both eclipse heat retention and illuminated-state heat rejection.

A geometry-closed first screening package now declares six path families: polymer supports, copper battery leads, PV flex traces, adhesive bonds, ceramic feedthroughs, and PCM containment ribs. Each path is explicit in count, conductivity, cross-section, length, and evidence class. The nominal sum is `1.1305e-4 W/K`; applying the declared 1.5 uncertainty multiplier gives `1.69575e-4 W/K`, or 3.39 times the current `5e-5 W/K` proxy target. Adhesive bonds dominate at `6e-5 W/K` (53.1% of nominal), followed by battery wiring at `1.95e-5 W/K` and feedthroughs at `1.875e-5 W/K`.

Package-budget result:

- status: **FAIL**;
- nominal assembled conductance: `1.1305e-4 W/K`;
- conservative assembled conductance: `1.69575e-4 W/K`;
- target margin: `-1.19575e-4 W/K`;
- dominant path: core-to-shell adhesive bonds;
- all dimensions and material properties remain screening assumptions, not released package geometry or qualification evidence.

This is useful negative evidence: the first complete package budget does not merely miss the target because of one exotic component. Ordinary bonds, leads, and feedthroughs collectively consume the thermal allowance before environmental margin.

## Artifacts

- `src/sim/thermal_storage.py`
- `src/sim/thermal_geometry.py`
- `src/sim/package_conductance.py`
- `experiments/thermal_shadow_survival.py`
- `experiments/derive_thermal_geometry_ranges.py`
- `experiments/thermal_shadow_sweep.py`
- `experiments/thermal_shadow_mass_budget.py`
- `experiments/thermal_shadow_loss_boundary.py`
- `experiments/package_conductance_budget.py`
- `configs/thermal_shadow_survival.json`
- `configs/thermal_geometry_ranges.json`
- `configs/thermal_shadow_sweep.json`
- `configs/thermal_shadow_mass_budget.json`
- `configs/thermal_shadow_loss_boundary.json`
- `configs/qst_stor_0002_package_conductance.json`
- `tests/test_thermal_storage.py`
- `tests/test_thermal_geometry.py`
- `tests/test_thermal_shadow_sweep.py`
- `tests/test_thermal_shadow_mass_budget.py`
- `tests/test_thermal_shadow_loss_boundary.py`
- `tests/test_package_conductance.py`
- `docs/system/thermal_shadow_survival.md`
- `docs/system/qst_stor_0002_thermal_loss_evidence_checklist.md`
- `outputs/qst_stor_0002/cases.csv`
- `outputs/qst_stor_0002/summary.json`
- `outputs/qst_stor_0002/thermal_geometry_ranges.csv`
- `outputs/qst_stor_0002/thermal_geometry_summary.json`
- `outputs/qst_stor_0002/geometry_coupled_sweep_summary.json`
- `outputs/qst_stor_0002/baseline_surface_survivors.json`
- `outputs/qst_stor_0002/mass_budget_boundary.json`
- `outputs/qst_stor_0002/loss_boundary.json`
- `outputs/qst_stor_0002/package_conductance/package_conductance_summary.json`
- `outputs/qst_stor_0002/package_conductance/package_conductance_paths.csv`

## Falsifier

If temperature support mass or heater demand eliminates the 10 mm survival margin across plausible cases, or if no complete package can meet the radiative and conductive loss targets after environmental margins, the seed envelope must grow, its mission eclipse duty must change, or thermal/storage responsibility must move to a specialized host.

## Next step

Propagate the conservative package conductance (`1.69575e-4 W/K`) and an explicit beginning-/end-of-life emissivity range through the 30-minute shadow model. Determine whether any mass-admissible survivor remains; if none does, compare the smallest envelope growth or host-assisted architecture that restores survival.
