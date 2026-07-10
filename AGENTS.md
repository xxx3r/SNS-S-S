# AGENTS.md: SNS-S-S Summer 2026 Control Plane

This repository is a formal research instrument for Solar-Nano-Sphere swarm dynamics, energy-chain modeling, asteroid-resource intelligence, and research-calendar execution.

## Mission

Advance one shared objective:

> Make SNS disciplined enough that outside experts can run it, inspect it, criticize it, and improve it.

The repository is not flight software and must not imply hardware readiness.

## Spawn ritual

Read, in order:

1. `README.md`
2. `memory/mem_log_short.md`
3. `quests/active/README.md`
4. latest `calendar/roundups/*.md`
5. latest `calendar/monthly/*.md`, when present
6. `AURORA.md`

Then select one active quest step with a concrete artifact.

## Canonical 2026 workstreams

- `SIM`: agent, environment, policy, metrics, experiments
- `STOR`: battery, pulse buffer, thermal control, curtailment, host storage
- `PV`: flexible PV output, degradation, thermal/radiation assumptions
- `META`: beam steering, pointing loss, receiver coupling, control cost
- `ARCI`: target scoring, uncertainty, evidence trails, worked examples
- `CALENDAR`: roundup schema, belief ledger, quest generation
- `FUND`: public artifact, funding narrative, partner legibility

## Required engineering rules

1. **Clarity over cleverness.** Prefer dataclasses, enums, explicit units, and small functions.
2. **Preserve units in names.** Use suffixes such as `_W`, `_Wh`, `_s`, `_K`, and `_m2` where ambiguity is possible.
3. **Track losses.** Harvested energy must resolve into direct use, storage, delivery, or curtailment.
4. **Separate score from confidence.** Especially in ARCI.
5. **Keep scenarios configurable.** No mission-defining constants hidden in code.
6. **Maintain compatibility intentionally.** Legacy Q1 experiments may remain runnable, but new work follows the Summer 2026 ontology.
7. **No hardware overclaiming.** Simulation PASS means model criteria passed, not space qualification.
8. **Test every new behavior.** At minimum add a focused unit or smoke test.

## Quest loop

1. Choose one quest from `quests/active/README.md`.
2. State the smallest falsifiable or inspectable objective.
3. Implement the minimum coherent change.
4. Run tests and the relevant experiment.
5. Save artifacts under `outputs/<quest-or-run-id>/` when outputs matter.
6. Update the quest record with evidence.
7. Update `memory/mem_log_short.md` and append the long log.
8. Record an Aurora score.

## Definition of done

A quest step is done only when:

- the artifact exists,
- assumptions and units are explicit,
- validation passes,
- uncertainty or limitations are written down,
- docs and active-quest state agree,
- the next move is one concrete action.

## Directory contract

- `src/`: reusable model code only
- `experiments/`: reproducible runs, sweeps, and artifact writers
- `configs/`: declared inputs
- `docs/system/`: canonical system assumptions and risks
- `docs/arci/`: ARCI method and examples
- `calendar/`: external evidence translated into belief shifts and actions
- `quests/`: execution state
- `outputs/`: generated evidence
- `memory/`: short handoff and append-only session history

## Summer 2026 anti-drift rules

Do not:

- add an unrelated subsystem without a quest,
- treat the 10 mm seed as Wh-scale bulk storage,
- optimize host delivery while ignoring curtailment and thermal state,
- collapse asteroid value into one unsupported dollar number,
- let old Q1 quest files silently compete with the Summer backlog,
- replace a small inspectable model with a heavy framework without evidence that it is needed.

## Session handoff

End every coding session with:

- tests run,
- artifacts created,
- assumptions changed,
- blockers discovered,
- exact next move.
