# QST-CTRL-0002: Toy Relay Jitter Simulation

Status: Active
Updated: 2026-02-15
Tags: [CTRL, SBSP, SWARM, SIM]

## Hypothesis
If we model an N-node relay chain with pointing jitter and control uncertainty, then end-to-end received power sensitivity will expose which jitter regimes dominate system viability.

## Method
- Inputs: `calendar/roundups/2026-02-08.md`, beamforming-under-uncertainty paper notes, current experiment scaffolding.
- Procedure: Build a simple simulator sweeping node count and jitter; compute received power and outage probability.
- Metrics: Curves for received power vs jitter and vs node count; reproducible CSV outputs.

## Success Criteria
- Must: CLI/script runs and writes metrics for at least three relay lengths and five jitter levels.
- Nice-to-have: Adds a control-policy knob (e.g., adaptive pointing gain) for comparison.

## Artifacts
- experiments/relay_jitter_sim.py
- experiments/outputs/relay_jitter_sim/<run_id>/metrics.csv
- experiments/outputs/relay_jitter_sim/<run_id>/power_vs_jitter.png

## Risks
- Toy model may overstate coherence retention without realistic phase noise and delay.

## Next Step
Define minimal equations + assumptions, then implement a no-frills CSV-first prototype.
