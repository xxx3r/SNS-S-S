# QST-SIM-0003: GEO Ring Power-Chain Model

Status: Active — host-service accounting and demand diagnostic accepted; PR #123 correction accepted; delivery attribution next
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

### Historical next slice — receiver-availability diagnostic, subsequently accepted

Use the same accepted coordinated 20% storage-node fixture, hold `beam_efficiency = 0.80`, and retain the two accepted eclipse fractions `0.05` and `0.10`.

Generate exactly two new cases with the already-supported legacy/default `receiver_visibility_fraction = 1.0`. Compare them against the immutable existing `receiver_visibility_fraction = 0.25` cases from `outputs/qst_sim_0003/eclipse_beam_sweep.json`.

Do not rerun the 0.25 cases. Do not add another visibility value, role mix, storage fraction, host-demand value, optimization loop, real ephemerides, or architecture claim.

Report only delivered energy, curtailment, survival, and coverage. If wider accepted synthetic visibility materially increases useful delivery, receiver availability becomes the next model bottleneck to characterize. If it does not, preserve that negative result and move the bottleneck search elsewhere.

## October 4 Weekly appraisal

The accepted phase-center diagnostic was appraised without rerunning a simulation world. On the frozen six-hour fixture, phase centers `0` and `π` each provide exactly 115 receiver-visible relay/storage agent-steps. At phase `0`, all 115 are sunlit for both eclipse settings. At phase `π`, the sunlit subset falls to 87 for `eclipse_fraction = 0.05` and 58 for `0.10`; the remaining 28 and 57 visible opportunities occur in eclipse. Accepted delivery falls from `0.37 Wh` at phase `0` to `0.283333333 Wh` and `0.193333333 Wh` at phase `π`.

Artifact: `outputs/qst_sim_0003/receiver_overlap_appraisal.json`.

This is a model-internal overlap diagnostic, not a post-hoc materiality classification or proof that overlap alone causes the energy result. Storage state, policy state, timestep ordering, and the synthetic fixture remain mediators.

### Historical next slice — telemetry completed in PR #120

Before generating another phase, visibility, role-mix, efficiency, or ephemeris case, make these quantities first-class deterministic telemetry:

- cumulative host demand;
- unmet host demand;
- host service fraction;
- role-conditioned receiver-visible sunlit and eclipse opportunities.

Add accounting-identity tests and preserve legacy summaries. This instrumentation slice generates no worlds and sets no mission adequacy threshold. A later experiment must freeze any threshold prospectively.

## October 18 recovery of PR #122 late findings

PR #120 completed the telemetry above. PR #122's two new demand cases at
`0.1` and `0.4 Wh/h` plus the loaded accepted `0.2 Wh/h` baseline all deliver
`0.37 Wh`. This rules out demand as the active cap only within that fixed
synthetic bracket; it does not identify a physical bottleneck or adequacy threshold.

### Next executable slice

PR #123 accepted the PR #122 routing/reproduction correction at 342eae9.
The dedicated human-owned routing repair reconciles Weekly direction permissions.
The next executable slice is to instrument delivered energy by agent role and receiver-visible
sunlit/eclipse state with accounting-identity tests before another world.
Hold geometry, demand, role mix, policy, beam rate, architecture, and mission
thresholds fixed. This successor is instrumentation only; the present recovery
does not implement it or generate new experimental evidence.

## October 25 Weekly instrument appraisal

PR #128 accepted the zero-world instrumentation above. It partitions cumulative delivered host energy by every declared agent role and receiver sunlit/eclipse state, preserves legacy summaries, and enforces conservation, monotonicity, non-negativity, complete-key, and receiver-opportunity identities. No accepted role/state attribution values were generated, so the instrument does not yet identify a limiting mechanism or materiality threshold.

### Next executable slice

Run exactly one instrumented replay of the hash-bound accepted `eclipse-0.05_beam-0.80` baseline at host demand `0.2 Wh/h`, receiver visibility `0.25`, and phase center `0.0`. Preserve the accepted coordinated role mix, six-hour duration, 300-second timestep, geometry, policy, beam rate, evaluator, and mission assumptions. The replay may produce at most one synthetic world and 720 agent-step records.

The replay must reproduce every legacy summary field within existing deterministic tolerance before its new role/state partition can be interpreted. A mismatch invalidates the measurement and stops the route. Treat the replay as a measurement upgrade, not independent confirmation of the accepted `0.37 Wh` result. Do not add a second case or infer materiality, architecture preference, real ephemeris behavior, relay performance, or hardware readiness.
