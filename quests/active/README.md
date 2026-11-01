# Active Quests: November 2026

Only quests listed here are active. Historical Q1 / Spring 2026 quest files have been removed from this directory and summarized in `quests/backlog/legacy_spring_2026.md`.

Keep 1–8 active quests. Each quest must produce an inspectable artifact and state what could invalidate its conclusion.

## Active Index

1. [QST-STOR-0002: Thermal-Derated Shadow Survival](QST-STOR-0002-thermal-derated-shadow-survival.md)
2. [QST-SYNTH-0001: Agent-Authored Thermal Stress Worlds](QST-SYNTH-0001-thermal-stress-worlds.md)
3. [QST-SIM-0002: Asteroid Illumination + Coverage Model](QST-SIM-0002-asteroid-illumination-model.md)
4. [QST-SIM-0003: GEO Ring Power-Chain Model](QST-SIM-0003-geo-ring-power-chain.md)
5. [QST-PV-0001: PV Degradation Parameter Sheet](QST-PV-0001-pv-degradation-parameters.md)
6. [QST-CALENDAR-0001: Weekly Roundup → Quest Pipeline](QST-CALENDAR-0001-roundup-parser.md)

## Recently completed

- `QST-ARCI-0001`: ARCI v0.1 synthetic-target sensitivity assessment
- `QST-STOR-0001`: storage geometry audit
- `QST-SIM-0001`: role-aware SNS agent and explicit power-state baseline
- `QST-FUND-0001`: measurement-philosophy public-artifact outline
- `QST-META-0001`: bounded metasurface beam-link abstraction and assumptions boundary

## Selection rule

Resolve `automation/standing/current.json` from freshly accepted main. The November Trio v2 policy is current, with a midmonth review on 2026-11-15 and expiry at 2026-12-01T07:00:00Z. Older policies remain historical replay authority only.

QST-SYNTH-0001 R2 remains `NEEDS_SCIENTIFIC_DECISION`: electrical-failure useful delivery is unresolved in the accepted evaluator, so the sealed holdout stays untouched. QST-STOR-0002 remains P0 with only its declared fast-rotator route locally falsified.

QST-META-0001 completed after PR #116 accepted its missing assumptions boundary and byte-bound tests; the deterministic 12-point output remains synthetic evidence, not a physical beam or hardware claim.

PR #134's one-world SIM3 replay is present on main and must not be repeated. Its immutable receipt discloses post-execution standing validation, so this reconciliation does not promote the role/state partition into qualified scientific evidence or infer a bottleneck. QST-SIM-0003 remains active without another generation route.

The bounded QST-SIM-0002 matrix is accepted and must not be repeated. Survey policy produced a small equal primary-endpoint gain in both declared rotation regimes and no survival difference, so the result supports neither a rotation-regime effect nor a mission-value claim. Irregular rotation, policy optimization, and resource accounting remain separate future protocols.

QST-PV-0001 is now the independent work-conserving direction. Prepare a source-traceable parameter sheet with units, ranges, environment, duration, and primary-source provenance; preserve scenario bands when test conditions do not translate cleanly. Do not mix literature translation with SIM2 generation or treat one paper as flight qualification. See `calendar/roundups/2026-11-01.md` and `quests/dispositions/2026-11-01-sim2-appraisal.json`.
