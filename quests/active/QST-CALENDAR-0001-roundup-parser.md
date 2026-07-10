# QST-CALENDAR-0001: Weekly Roundup → Quest Pipeline

Status: Active, parser implemented  
Priority: P1  
Tags: [CALENDAR, QUESTS, TOOLING]

## Hypothesis

A strict weekly schema can turn literature review into auditable belief shifts and Codex-readable quests without manual drift.

## Current baseline

`src/research/roundup.py` parses JSON-compatible YAML front matter and `quest_engine.py` normalizes suggested actions.

## Remaining method

- Add CLI generation into a staging directory.
- Validate duplicate quest IDs.
- Append belief shifts to the ledger.
- Add one real Sunday roundup using the template.

## Success criteria

- Parser rejects malformed or incomplete front matter.
- Generated quests are deterministic.
- No automatic activation without human review.

## Artifacts

- `scripts/roundup_to_quests.py`
- `calendar/roundups/<date>.md`
- `outputs/qst_calendar_0001/`

## Falsifier

If the schema encourages low-value quest proliferation, increase the promotion threshold and cap suggested actions.
