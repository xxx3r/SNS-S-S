# QST-0003: Beaming Efficiency Sweep

Status: Active
Updated: 2026-02-05
Tags: [SBSP, CTRL, SWARM]

## Hypothesis
If we sweep `eta_beam` for a coordinated configuration, then we can quantify the efficiency threshold where beaming becomes beneficial.

## Method
- Inputs: coordinated config + `eta_beam` sweep values.
- Procedure: Run coordinated sims for `eta_beam ∈ {0.1, 0.3, 0.5, 0.7, 0.9}` and capture outputs.
- Metrics: `E_host_total` per run.

## Success Criteria
- Must: CSV with `[eta_beam, E_host_total]` and a summary plot.
- Nice-to-have: note the elbow/threshold in README.

## Artifacts
- outputs/<run_id>/eta_beam_sweep.csv
- outputs/<run_id>/plots/eta_beam_vs_host_energy.png

## Risks
- Too-short simulation horizon may flatten differences.

## Next Step
Add a sweep runner that reuses the coordinated config and writes the CSV + plot.
