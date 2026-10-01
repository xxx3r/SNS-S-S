# Active Quests: Summer 2026

Only quests listed here are active. Historical Q1 / Spring 2026 quest files have been removed from this directory and summarized in `quests/backlog/legacy_spring_2026.md`.

Keep 1–8 active quests. Each quest must produce an inspectable artifact and state what could invalidate its conclusion.

## Active Index

1. [QST-STOR-0002: Thermal-Derated Shadow Survival](QST-STOR-0002-thermal-derated-shadow-survival.md)
2. [QST-SYNTH-0001: Agent-Authored Thermal Stress Worlds](QST-SYNTH-0001-thermal-stress-worlds.md)
3. [QST-SIM-0002: Asteroid Illumination + Coverage Model](QST-SIM-0002-asteroid-illumination-model.md)
4. [QST-SIM-0003: GEO Ring Power-Chain Model](QST-SIM-0003-geo-ring-power-chain.md)
5. [QST-PV-0001: PV Degradation Parameter Sheet](QST-PV-0001-pv-degradation-parameters.md)
6. [QST-META-0001: Metasurface Beam-Steering Abstraction](QST-META-0001-metasurface-beam-abstraction.md)
7. [QST-CALENDAR-0001: Weekly Roundup → Quest Pipeline](QST-CALENDAR-0001-roundup-parser.md)

## Recently completed

- `QST-ARCI-0001`: ARCI v0.1 synthetic-target sensitivity assessment
- `QST-STOR-0001`: storage geometry audit
- `QST-SIM-0001`: role-aware SNS agent and explicit power-state baseline
- `QST-FUND-0001`: measurement-philosophy public-artifact outline

## Selection rule

The human-approved October standing policy applies only after qualified acceptance on main and expires at 2026-11-01T06:00:00Z. The September policy remains expired historical authority.

QST-SYNTH-0001 R2 remains `NEEDS_SCIENTIFIC_DECISION`: electrical-failure useful delivery is unresolved in the accepted evaluator, so the sealed holdout stays untouched. QST-STOR-0002 remains P0 with only its declared fast-rotator route locally falsified.

QST-META-0001 is the current executable direction under the existing Weekly owner. The previously selected SIM3 phase diagnostic is accepted in PR #113; do not repeat it. PR #114 routes only the missing `docs/system/beam_link_assumptions.md` artifact and byte-bound tests against the accepted 12-point META sweep. Preserve output bytes and formulas; no sweep generation, expansion, materiality reclassification, architecture claim or quest closure is included. After acceptance, Weekly separately appraises the completed SIM3 phase evidence and records the next bounded direction or an explicit deferral. See `calendar/monthly/2026-10.md` and `quests/dispositions/2026-10-01.json`.
