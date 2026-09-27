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

The September standing policy remains valid through 2026-10-01T06:00:00Z, pending the human renewal checkpoint on September 30.

QST-SYNTH-0001 R2 remains `NEEDS_SCIENTIFIC_DECISION`: electrical-failure useful delivery is unresolved in the accepted evaluator, so the sealed holdout stays untouched. QST-STOR-0002 remains P0 with only its declared fast-rotator route locally falsified.

QST-SIM-0003 is the current executable direction. Its accepted receiver diagnostic increased modeled host delivery from 0.37 Wh to 0.82 Wh and 0.73 Wh when receiver visibility widened from 0.25 to 1.0 on the fixed fixture, while curtailment remained approximately 8.8–9.5 kWh. The next slice changes phase placement, not visibility fraction: retain receiver visibility 0.25, beam efficiency 0.80, eclipse fractions 0.05 and 0.10, and the accepted coordinated 20% storage-node fixture; generate exactly two new cases at receiver phase center π and compare them to immutable phase-center-0 baselines without rerunning those baselines. Stop before additional phase centers, optimization, role-mix changes, real ephemerides, or architecture claims.
