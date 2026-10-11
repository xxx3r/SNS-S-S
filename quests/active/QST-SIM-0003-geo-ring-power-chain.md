# QST-SIM-0003: GEO Ring Power-Chain Model

Status: Active — host demand ruled out as the current synthetic delivery cap; delivery-path attribution next
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

## October 4 Weekly appraisal

The accepted phase-center diagnostic was appraised without rerunning a simulation world. On the frozen six-hour fixture, phase centers `0` and `π` each provide exactly 115 receiver-visible relay/storage agent-steps. At phase `0`, all 115 are sunlit for both eclipse settings. At phase `π`, the sunlit subset falls to 87 for `eclipse_fraction = 0.05` and 58 for `0.10`; the remaining 28 and 57 visible opportunities occur in eclipse. Accepted delivery falls from `0.37 Wh` at phase `0` to `0.283333333 Wh` and `0.193333333 Wh` at phase `π`.

Artifact: `outputs/qst_sim_0003/receiver_overlap_appraisal.json`.

This is a model-internal overlap diagnostic, not a post-hoc materiality classification or proof that overlap alone causes the energy result. Storage state, policy state, timestep ordering, and the synthetic fixture remain mediators.

### Next executable slice

Before generating another phase, visibility, role-mix, efficiency, or ephemeris case, make these quantities first-class deterministic telemetry:

- cumulative host demand;
- unmet host demand;
- host service fraction;
- role-conditioned receiver-visible sunlit and eclipse opportunities.

Add accounting-identity tests and preserve legacy summaries. This instrumentation slice generates no worlds and sets no mission adequacy threshold. A later experiment must freeze any threshold prospectively.

## October 11 Weekly demand-sensitivity result

PR #120's accepted measurement accounting enabled exactly two new demand cases without repeating the accepted `0.2 Wh/h` baseline. On the otherwise fixed coordinated fixture (`eclipse_fraction = 0.05`, beam efficiency `0.80`, visibility `0.25`, phase center `0`):

- `0.1 Wh/h` demand: `0.37 Wh` delivered, `0.23 Wh` unmet, service fraction `0.616666667`;
- accepted `0.2 Wh/h` baseline: `0.37 Wh` delivered, `0.83 Wh` unmet, service fraction `0.308333333`;
- `0.4 Wh/h` demand: `0.37 Wh` delivered, `2.03 Wh` unmet, service fraction `0.154166667`.

Delivery, curtailment, coverage, survival, and the `115` receiver-visible relay/storage opportunities are unchanged across the declared demand bracket. Within this deterministic synthetic fixture, host demand is therefore not the active delivery cap. This does not identify which remaining fixed element—receiver opportunity, policy, beam rate, storage state, or timestep ordering—is causal, and it does not establish mission adequacy.

Artifact: `outputs/qst_sim_0003/host_demand_sensitivity.json`.

### Next executable slice

Before another world, instrument delivered energy by agent role and by receiver-visible sunlit/eclipse state. Add accounting identities tying the partitions to total delivered energy. The next comparison may then distinguish unused receiver opportunity from policy or beam-rate limitation without changing geometry, demand, role mix, or architecture.
