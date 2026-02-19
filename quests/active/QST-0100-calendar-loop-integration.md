# QST-0100: Calendar Loop Integration

Status: Active
Updated: 2026-02-19
Tags: [META, DOCS]

## Hypothesis
If we formalize the calendar roundup loop with belief tracking, then weekly external signals will translate into quests and Aurora scoring context.

## Method
- Inputs: `calendar/roundups/*`, `calendar/belief_ledger.csv`
- Procedure: Maintain roundups + ledger, sync quests, and reference external context in Aurora scoring.
- Metrics: Roundup YAML present, ledger entries updated, quests promoted.

## Success Criteria
- Must: calendar directory exists with roundup/monthly scaffolding and belief ledger.
- Nice-to-have: researcher brief documented for weekly process.

## Artifacts
- calendar/roundups/2026-01-25.md
- calendar/roundups/2026-02-08.md
- calendar/belief_ledger.csv
- quests/active/QST-SBSP-0001-relay-chain-reality-check.md
- quests/active/QST-CTRL-0002-toy-relay-jitter-sim.md
- quests/active/QST-SBSP-0003-darpa-power-crib-sheet.md
- quests/active/QST-SWARM-0004-starling-constraints-extraction.md
- quests/active/QST-META-0005-dl-metasurface-pipeline.md
- quests/active/QST-STOR-0006-night-side-energy-budget.md
- quests/active/QST-PV-0007-leo-perovskite-risk-register-refresh.md

## Risks
- Inconsistent quest sources (plan vs quests) could cause drift.

## Next Step
Execute one suggested action artifact from the latest roundup (recommended: draft `docs/pv_leo_perovskite_risk_register.md` for QST-PV-0007).
