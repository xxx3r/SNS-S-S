# QST-0100: Calendar Loop Integration

Status: Active
Updated: 2026-02-05
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
- calendar/belief_ledger.csv
- agents/researcher_brief.md

## Risks
- Inconsistent quest sources (plan vs quests) could cause drift.

## Next Step
Run the next weekly roundup and append belief shifts into the ledger.
