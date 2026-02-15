# QST-0002: Baseline vs Coordinated Experiment Harness

Status: In Progress
Updated: 2026-02-14
Tags: [SWARM, CTRL]

## Hypothesis
If we implement baseline and coordinated presets with shared metrics, then we can compare swarm performance with minimal configuration changes.

## Method
- Inputs: baseline/coordinated config presets (see `docs/04_experiments_and_metrics_for_codex.txt`).
- Procedure: Implement two SimulationConfig presets and run both for a fixed horizon.
- Metrics: `E_host_total`, `E_host(t)`, mean `E_i(t)`, dead agent count.

## Success Criteria
- Must: outputs for both presets saved to a clear run folder (CSV + PNG plots).
- Nice-to-have: a quick comparison table summarizing deltas.

## Artifacts
- experiments/outputs/baseline_vs_coordinated/baseline/metrics.csv
- experiments/outputs/baseline_vs_coordinated/coordinated/metrics.csv
- experiments/outputs/baseline_vs_coordinated/baseline_vs_coordinated_comparison.csv
- experiments/outputs/baseline_vs_coordinated/baseline_vs_coordinated_summary.json
- experiments/outputs/baseline_vs_coordinated/*/plots/*

## Latest Run Summary (2026-02-14)
- Command: `python -m experiments.baseline_vs_coordinated --out outputs/latest`
- Baseline: `final_host_energy=0.0`, `mean_agent_energy=3.97416760566241`, `dead_agent_count=0`
- Coordinated: `final_host_energy=0.502777264753466`, `mean_agent_energy=3.9195708328900323`, `dead_agent_count=0`
- Delta (`coordinated - baseline`): `final_host_energy=+0.502777264753466`, `mean_agent_energy=-0.05459677277237755`, `dead_agent_count=0`

## Environment Note
Install plotting dependency when PNG outputs are required:
- `python -m pip install matplotlib`

Without matplotlib, the harness still emits CSV + summary artifacts and writes `PLOT_WARNING.txt` in each plots directory.

## Risks
- Divergent defaults between presets could invalidate comparisons.

## Next Step
- Validate plotting path by running the harness in an environment with matplotlib and confirm PNG generation for both policies.
