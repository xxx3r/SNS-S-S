# QST-SIM-0003: GEO Ring Power-Chain Model

Status: Active — receiver availability is material on the fixed fixture; phase-position diagnostic next  
Priority: P1  
Tags: [SIM, GEO, SBSP, POWER]

## Hypothesis

Role-specialized nodes around an idealized GEO ring can maintain field coverage and intermittent host delivery through eclipse windows more effectively than identical independent nodes.

## Current baseline

`GEORingWorld` provides orbital phase, eclipse windows, thermal proxy, and coverage bins.

## Remaining method

- Add receiver / line-of-sight windows.
- Compare role mixes and storage-node fractions.
- Sweep eclipse fraction and beam efficiency.

## Success criteria

- Energy, survival, curtailment, and coverage plots.
- Baseline versus coordinated comparison.
- Explicit conditions under which relay losses erase benefit.

## Artifacts

- `outputs/qst_sim_0003/`
- `docs/system/geo_ring_assumptions.md`

## Falsifier

If the host receives less useful energy after relay costs across plausible efficiencies, power relaying should remain secondary to sensing and diagnostics.


## September 20 Weekly recovery disposition

The accepted fixed 2 x 2 sweep at `receiver_visibility_fraction = 0.25` is retained as non-repeatable evidence:

- full coverage and zero dead agents in all four cases;
- `beam_efficiency 0.60 -> 0.80` adds `0.0925 Wh` delivered at both eclipse settings;
- `eclipse_fraction 0.05 -> 0.10` changes delivered energy by `0 Wh`;
- the same eclipse change reduces curtailment by `708.319947017 Wh`;
- curtailment remains orders of magnitude larger than delivered host energy on this fixture.

This does not establish a real receiver bottleneck. It earns one bounded discriminating measurement using parameters already supported by accepted code.

### Next executable slice

Use the same accepted coordinated 20% storage-node fixture, hold `beam_efficiency = 0.80`, and retain the two accepted eclipse fractions `0.05` and `0.10`.

Generate exactly two new cases with the already-supported legacy/default `receiver_visibility_fraction = 1.0`. Compare them against the immutable existing `receiver_visibility_fraction = 0.25` cases from `outputs/qst_sim_0003/eclipse_beam_sweep.json`.

Do not rerun the 0.25 cases. Do not add another visibility value, role mix, storage fraction, host-demand value, optimization loop, real ephemerides, or architecture claim.

Report only delivered energy, curtailment, survival, and coverage. If wider accepted synthetic visibility materially increases useful delivery, receiver availability becomes the next model bottleneck to characterize. If it does not, preserve that negative result and move the bottleneck search elsewhere.


## September 27 Weekly disposition

The accepted two-case receiver-availability diagnostic is retained without rerun:

- at eclipse fraction 0.05, widening receiver visibility from 0.25 to 1.0 raised delivered energy from 0.37 Wh to 0.82 Wh;
- at eclipse fraction 0.10, the same change raised delivered energy from 0.37 Wh to 0.73 Wh;
- coverage remained 1.0 and dead-agent count remained zero;
- curtailment fell only 1.137202881 Wh and 0.878482613 Wh and still remained approximately 9.5 kWh and 8.8 kWh.

The relative sensitivity is material for this synthetic fixture, but the absolute delivery is still tiny beside curtailment. This identifies receiver-window geometry as a model bottleneck; it does not establish real relay value or architecture superiority.

### Next executable slice

Use the accepted coordinated 20% storage-node fixture, `beam_efficiency = 0.80`, `receiver_visibility_fraction = 0.25`, and eclipse fractions `0.05` and `0.10`.

Generate exactly two new cases with `receiver_phase_center_rad = π`. Compare them against the immutable phase-center-`0` baseline cases from `outputs/qst_sim_0003/eclipse_beam_sweep.json`; do not rerun the baselines.

Report delivered energy, curtailment, survival, and coverage. If the antipodal phase placement materially changes delivery, preserve phase alignment as an explicit model variable. If it does not, preserve the negative result and keep the simpler visibility-fraction abstraction. Do not add phase centers, change visibility fraction, role mix, storage fraction, host demand, or beam efficiency; do not optimize or make real-ephemeris, architecture, relay-performance, or hardware-readiness claims.
