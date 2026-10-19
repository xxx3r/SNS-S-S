# Active Quests: October 2026

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

The human-approved October standing policy applies only after qualified acceptance on main and expires at 2026-11-01T06:00:00Z. The September policy remains expired historical authority.

QST-SYNTH-0001 R2 remains `NEEDS_SCIENTIFIC_DECISION`: electrical-failure useful delivery is unresolved in the accepted evaluator, so the sealed holdout stays untouched. QST-STOR-0002 remains P0 with only its declared fast-rotator route locally falsified.

QST-META-0001 completed after PR #116 accepted its missing assumptions boundary and byte-bound tests; the deterministic 12-point output remains synthetic evidence, not a physical beam or hardware claim.

QST-SIM-0003 is the current executable direction. PR #120 completed host-demand, unmet-demand, service-fraction, and role-conditioned receiver-opportunity telemetry. PR #122 then accepted the bounded demand diagnostic: delivery stayed at 0.37 Wh across 0.1, 0.2, and 0.4 Wh/h; the 0.2 baseline was loaded, not rerun. PR #123 accepted the PR #122 routing/reproduction correction at 342eae9. The dedicated human-owned routing repair reconciles Weekly direction permissions. The next executable slice is to instrument delivered energy by agent role and receiver-visible sunlit/eclipse state with accounting-identity tests before another world. Hold geometry, demand, role mix, policy, beam rate, architecture, and mission thresholds fixed. Materiality remains prospectively undefined. See `quests/dispositions/2026-10-18-routing-recovery.json`.
