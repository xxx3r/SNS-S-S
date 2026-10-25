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

QST-SIM-0003 is the current executable direction. PR #128 accepted delivered-energy attribution by role and receiver-visible sunlit/eclipse state with accounting identities, generating zero worlds. Weekly's October 25 appraisal confirms that the instrument is qualified but contains no accepted attribution values yet. The next executable slice is exactly one instrumented replay of the immutable `eclipse-0.05_beam-0.80` baseline at 0.2 Wh/h, visibility 0.25, and phase center 0.0. It must reproduce every legacy summary before reporting the new partition; any mismatch invalidates the measurement. Hold geometry, demand, role mix, policy, beam rate, architecture, evaluator semantics, and mission thresholds fixed. Do not count the replay as independent evidence for the legacy 0.37 Wh result. Materiality remains prospectively undefined. See `calendar/roundups/2026-10-25.md` and `quests/dispositions/2026-10-18-routing-recovery.json`.
