# QST-0002: Baseline vs Coordinated Experiment Harness

Status: Active
Updated: 2026-02-05
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
- outputs/<run_id>/baseline/metrics.csv
- outputs/<run_id>/coordinated/metrics.csv
- outputs/<run_id>/plots/*.png

## Risks
- Divergent defaults between presets could invalidate comparisons.

## Next Step
Define the two preset configs and stub a runner script in `experiments/`.
