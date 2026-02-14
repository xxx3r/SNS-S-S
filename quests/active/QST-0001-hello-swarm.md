# QST-0001: Hello Swarm

Status: Active
Updated: 2026-02-06
Tags: [SWARM, CTRL, PV]

## Hypothesis
If we run a baseline sim for 50 steps, then we will produce core output artifacts to validate the pipeline.

## Method
- Inputs: `configs/astroid_baseline.json`
- Procedure: Run the baseline sim for 50 steps and save outputs to `outputs/latest/`.
- Metrics: `metrics.json`, `timeseries.csv`, `plot_energy.png`

## Success Criteria
- Must: outputs exist in `outputs/latest/`.
- Nice-to-have: quick plot saved without errors.

## Artifacts
- outputs/latest/metrics.json
- outputs/latest/timeseries.csv
- outputs/latest/plot_energy.png

## Risks
- Missing config defaults could mask errors.

## Next Step
Promote this baseline commnad into CI/docs so outputs/latest artifacts stay reproducible each session.
