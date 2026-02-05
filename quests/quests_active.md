# quests_active

## QST-0100: Calendar Loop Integration

### Hypothesis
If we formalize the calendar roundup loop with belief tracking, then weekly external signals will translate into quests and Aurora scoring context.

### Method
- Inputs: `calendar/roundups/*`, `calendar/belief_ledger.csv`
- Procedure: Maintain roundups + ledger, sync quests, and reference external context in Aurora scoring.
- Metrics: Roundup YAML present, ledger entries updated, quests promoted.

### Success Criteria
- Must: calendar directory exists with roundup/monthly scaffolding and belief ledger.
- Nice-to-have: researcher brief documented for weekly process.

### Artifacts
- calendar/roundups/2026-01-25.md
- calendar/belief_ledger.csv
- agents/researcher_brief.md

### Risks
- Inconsistent quest sources (plan vs quests) could cause drift.

### Next Step
Run the next weekly roundup and append belief shifts into the ledger.

---

## QST-0001: Hello Swarm

### Hypothesis
If we run a baseline sim for 50 steps, then we will produce core output artifacts to validate the pipeline.

### Method
- Inputs: `configs/baseline.yaml`
- Procedure: Run baseline sim for 50 steps and save outputs to `outputs/latest/`.
- Metrics: `metrics.json`, `timeseries.csv`, `plot_energy.png`

### Success Criteria
- Must: outputs exist in `outputs/latest/`
- Nice-to-have: quick plot saved without errors

### Artifacts
- outputs/latest/metrics.json
- outputs/latest/timeseries.csv
- outputs/latest/plot_energy.png

### Risks
- Missing config defaults could mask errors.

### Next Step
Document a smoke test command in `rituals/spells.md`.
