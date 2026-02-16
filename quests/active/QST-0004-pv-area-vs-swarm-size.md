# QST-0004: PV Area vs Swarm Size Tradeoff

Status: Active
Updated: 2026-02-16
Tags: [PV, SWARM]

## Hypothesis
If we hold total PV area constant while varying swarm size, then we can quantify whether many-small or few-large units deliver more host energy.

## Method
- Inputs: total PV area `A_total` with two configurations: many-small vs few-large.
- Procedure: Run two sims where `N_large * A_PV_small = N_small * A_PV_large = A_total`.
- Metrics: `E_host_total` for each configuration.

## Success Criteria
- Must: table summarizing `(N_agents, A_PV, E_host_total)`.
- Nice-to-have: bar plot comparing the two configurations.

## Artifacts
- outputs/<run_id>/pv_area_vs_swarm_size.csv
- outputs/<run_id>/plots/pv_area_vs_swarm_size.png

## Risks
- Edge cases where per-agent overhead dominates small units.

## Progress
- Defined fixed-total-area variants in `configs/pv_area_vs_swarm_size_few_large.json` and `configs/pv_area_vs_swarm_size_many_small.json` with `A_total = 2.4` for both scenarios.
- Added `experiments/compare_pv_area_vs_swarm_size.py` to run both variants, write a comparison CSV, and generate a bar chart when matplotlib is available.
- Ran the comparison and generated `outputs/latest/pv_area_vs_swarm_size/pv_area_vs_swarm_size.csv`; plotting gracefully degraded to `plots/PLOT_WARNING.txt` because matplotlib is not installed.

## Next Step
Interpret the comparison output and add a short takeaway on whether many-small or few-large performs better under this configuration.
