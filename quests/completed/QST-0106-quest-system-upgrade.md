# QST-0106: Quest System Upgrade

Status: Completed
Completed: 2026-02-05
Tags: [META, DOCS]

## Hypothesis
If quests live in per-quest files with an index, then the system scales to more complex quests without a monolithic list.

## Method
- Inputs: `docs/*.txt` context and existing quest list.
- Procedure: Split active/completed quests into per-quest files and seed new quests from the experiment plan.
- Metrics: clear index + per-quest files in `quests/active/` and `quests/completed/`.

## Success Criteria
- Must: each active quest has its own file and a shared index.
- Nice-to-have: completed quest logged for the system upgrade.

## Artifacts
- quests/active/README.md
- quests/active/QST-0001-hello-swarm.md
- quests/active/QST-0002-baseline-vs-coordinated.md
- quests/active/QST-0003-beaming-efficiency-sweep.md
- quests/active/QST-0004-pv-area-vs-swarm-size.md
- quests/active/QST-0100-calendar-loop-integration.md
- quests/completed/README.md
