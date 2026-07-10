# SNS-S-S

**Solar-Nano-Sphere Simulation + Surveying**

SNS-S-S is Aurora Lab's open Python framework for turning the Solar-Nano-Sphere concept into a formal research instrument.

The Summer 2026 mission is not hardware readiness. It is **model readiness**: a legible, testable system for swarm dynamics, energy-chain accounting, asteroid-resource confidence, literature tracking, and quest-based research execution.

> **SNS does not mine asteroids. SNS helps decide which asteroids deserve miners.**

The long-horizon vision remains an intelligent solar-system energy mesh. The near-term path is narrower and more credible: build the measurement language, simulation spine, and uncertainty framework that future sensing swarms could sharpen.

## Current program phase

**2026: definition, simulation, and narrative**

This repository should make the following questions inspectable:

1. How does an SNS-like node allocate sunlight among direct loads, pulse storage, survival storage, beaming, and curtailment?
2. When does a coordinated swarm outperform independent nodes?
3. How do asteroid illumination, thermal cycles, coverage gaps, and communication geometry affect mission value?
4. What evidence is required before an asteroid target becomes credible enough for a precursor mission?
5. How should weekly literature signals become explicit belief shifts and repo quests?

## Summer 2026 architecture

```text
calendar/
  roundups/          weekly research with machine-usable front matter
  monthly/           roundup-of-roundups and belief consolidation

docs/
  system/            SNS system definition, constraints, budgets, risks
  arci/              Asteroid Resource Confidence Index
  architecture/      repository and simulation design

src/
  agents/            role-aware SNS nodes and policies
  world/             asteroid and GEO-ring environments
  sim/               config, simulation loop, metrics, storage audits
  arci/              transparent confidence scoring
  research/          roundup parser and quest generation

quests/
  active/            3–8 current research or implementation quests
  completed/         evidence-bearing completed work

experiments/          reproducible runs and parameter sweeps
configs/              versioned experiment inputs
outputs/              generated artifacts, not arguments by assertion
```

## Node ontology

The Summer 2026 model treats an SNS node as a small thermodynamic agent, not a panel attached to a giant battery.

Each node tracks:

- role: `scout`, `sensor`, `relay`, or `storage`
- mode: harvest, scout, relay, move, idle, sleep, or reflect
- survival battery energy
- pulse-buffer energy
- health state
- core-temperature proxy
- harvested, directly used, stored, delivered, and curtailed energy

The dominant storage lesson is architectural: a 10 mm seed cannot warehouse the output of a 0.1–1.0 m² kite. The model therefore makes curtailment visible and treats meaningful Wh-scale storage as a role-specialized or host-level function.

## Mission scenarios

### Asteroid resource intelligence

A rotating asteroid world with:

- cosine-weighted illumination
- day/night temperature proxies
- coverage bins
- role-aware surveying and relay behavior
- host-energy demand

Run:

```bash
python experiments/baseline.py \
  --config configs/summer_2026_asteroid.json \
  --out outputs/summer_2026_asteroid
```

### GEO / SBSP field diagnostics

An idealized GEO ring with:

- eclipse windows
- orbital coverage bins
- sensor, relay, scout, and storage roles
- energy delivery and field-coverage metrics

Run:

```bash
python experiments/baseline.py \
  --config configs/summer_2026_geo_ring.json \
  --out outputs/summer_2026_geo_ring
```

## Core metrics

Every mission run should expose at least:

- total energy harvested
- energy delivered to the host
- energy curtailed
- node survival / failure count
- coverage fraction
- battery distribution
- role distribution
- mode distribution
- health distribution
- mean temperature proxy

A useful result is not merely a high score. It is a result whose assumptions, units, and losses are visible.

## ARCI

`src/arci/` contains the first transparent Asteroid Resource Confidence Index scaffold.

ARCI v0.1 separates:

- target score
- evidence confidence
- confidence-adjusted score
- uncertainty bounds
- recommendation gate

The current dimensions are:

1. composition
2. accessibility
3. recoverability
4. energy environment
5. surface-operations risk
6. communications geometry
7. market / mission value

ARCI is not a mineral-valuation oracle. It is a research framework for exposing what is known, what is inferred, and what measurement should come next.

## Research calendar

Weekly roundups use Markdown plus JSON-compatible YAML 1.2 front matter. Each Sunday roundup must emit:

- `weighted_belief_shifts`
- `suggested_actions`
- `sns_awareness_update`

The parser lives in `src/research/roundup.py`. Suggested actions can be normalized into quest drafts through `src/research/quest_engine.py`.

Template: `calendar/roundups/TEMPLATE.md`

## Active quests

The canonical index is `quests/active/README.md`.

Summer 2026 priorities are:

1. minimal role-aware SNS agent
2. asteroid illumination and coverage model
3. GEO-ring power-chain model
4. storage and thermal-control refinement
5. metasurface steering abstraction
6. ARCI v0.1
7. roundup-to-quest pipeline
8. public artifact outline

Do not create a new theory galaxy when one measurable quest step will do.

## Install and test

```bash
python -m pip install -e .
python -m pytest -q
```

The core favors the standard library. NumPy remains an explicit dependency for the pre-existing metasurface benchmark; `pytest` and `matplotlib` are development dependencies.

## Evidence rules

- Simulation outputs are evidence about the model, not proof of hardware feasibility.
- Placeholder parameters must be labeled.
- Score and confidence must remain separate.
- Claims about external technology require sources in the research calendar or system docs.
- A completed quest must point to a reproducible artifact, test, calculation, or documented decision.

## 2026 win condition

By the end of Summer 2026, an outside expert should be able to:

1. understand the mission in ten minutes,
2. run asteroid and GEO examples,
3. inspect the energy ledger,
4. critique the system assumptions,
5. evaluate an ARCI example,
6. trace a literature signal into a quest.

That is the first flag on the ridge: not deployment, but legitimacy.
