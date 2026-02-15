# QST-0003: Beaming Efficiency Sweep

Status: Active
Updated: 2026-02-15
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

## Progress
- Added `experiments/sweep_eta_beam.py` CLI options to reuse `configs/asteroid_coordinated.json` by default and target a caller-selected output directory.
- Runner now writes `eta_beam_sweep.csv` and attempts `plots/eta_beam_vs_host_energy.png`; when matplotlib is unavailable it writes `plots/PLOT_WARNING.txt` instead of failing.
- Generated `outputs/latest/eta_beam_sweep/eta_beam_sweep.csv` with coordinated sweep values.

## Next Step
Interpret the sweep curve (elbow/threshold) and add a short takeaway note to this quest or README.
