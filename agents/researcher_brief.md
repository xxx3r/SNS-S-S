# Researcher Brief (Weekly Sunday Loop)

## Purpose
Translate external signals into actionable SNS quests through the /calendar system.

## Sunday Checklist
1. Read the latest roundup in `calendar/roundups/` and the monthly overview in `calendar/monthly/`.
2. Capture highlights by lens (PV, metasurfaces, storage/control, SBSP, swarms).
3. Record belief shifts (-2..+2) in the roundup YAML and append them to `calendar/belief_ledger.csv`.
4. Promote or update quests in `quests/active/README.md` (new, escalated, or deprecated).
5. Update `memory/mem_log_short.md` with the next one-shot move.
6. Update Aurora score with an `external_context_weight` based on belief ledger confidence.

## Roundup Output Requirements
- Markdown summary for humans.
- YAML footer with `week_of`, `belief_shift`, `quests`, and `search_pack`.
- Use tags from `calendar/tag_index.yml`.

## Belief Ledger Guidance
- Use `weight` (0–1) to reflect confidence in external signals.
- Keep entries granular (one tag per row).
- Default source is the roundup file path.
