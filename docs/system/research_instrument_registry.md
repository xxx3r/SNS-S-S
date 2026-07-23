# SNS Research Instrument Registry

This registry is the public discoverability surface for reusable, already-merged research instruments. It answers **what tools are available**, not **what the laboratory is authorized to do next**.

An instrument entry never activates a quest, changes queue priority, grants evidence authority, or permits model writes. Agents should consult an entry only when the selected acceptance slice plausibly needs that capability, then preserve the active contract, quest, budget, holdout, and evidence boundaries.

## `synthetic_worlds`

Status: Available on `main`  
Public owner: SNS-S-S  
Import terminal state: `SNS_SYNTHETIC_WORLD_CORE_IMPORTED`  
Campaign state: `NEEDS_GOVERNANCE_REVIEW`

### Capability

A standard-library-only toolkit for deterministic, bounded synthetic-world generation:

- declarative recipes with unknown-key rejection;
- deterministic parameter sweeps and temporal/spatial samplers;
- preflight record, point, shard, and byte budgets;
- atomic JSONL shard writing;
- strict shard, record, manifest, and hash validation;
- tiny reproducible fixtures;
- public provenance and import receipts.

### Entry points

- Runtime: `src/sim/synthetic_worlds/`
- Public import manifest: `src/sim/SYNTHETIC_WORLDS_IMPORT_MANIFEST.json`
- Example recipe: `configs/synthetic_worlds/basic_world.json`
- Reproduction guide: `docs/synthetic_worlds/REPRODUCTION.md`
- Boundary tests: `tests/test_synthetic_worlds_public_import.py`
- Governing campaign issue: Issue #30

### Appropriate uses

The instrument may be proposed inside a bounded acceptance slice when deterministic scenario diversity, matched experiment arms, anomaly injection, seed separation, or reproducible holdouts would improve an SNS model experiment.

The nearest identified use is the proposed `QST-SYNTH-0001` thermal/eclipsing campaign. Monthly governance may instead attach a smaller synthetic-world experiment to a suitable active quest, including storage or thermal work, when ownership and budgets remain explicit.

### Use gate

Before an agent uses the instrument for a scientific campaign, the owning quest or accepted sub-experiment must freeze:

1. world schema and imported snapshot identity;
2. development and holdout seeds;
3. parameter ranges and anomaly types;
4. world, record, runtime, and storage budgets;
5. evaluator, policy family, metrics, exclusions, and retry rules;
6. evidence language and falsifiers.

Failed, invalid, excluded, and budget-rejected worlds must remain visible. An agent may not regenerate worlds until favorable results appear or alter holdouts after observing outcomes.

### Nonclaims and prohibitions

Synthetic outcomes are evidence about declared SNS models, not the physical world. This instrument does not establish hardware feasibility, material performance, flight readiness, or space qualification.

It grants no authority to:

- activate or reprioritize quests;
- change monthly governance;
- train, update, consolidate, install, or write a model;
- access private repositories, archives, credentials, or authenticated resources;
- create an automatic synchronization channel;
- modify the generator and evaluator in the same experimental run.

### Governance reminder

`QST-SYNTH-0001` remains inactive while the active queue is full. A pending quest-action proposal asks monthly governance to activate it when a lawful slot exists, attach a bounded experiment to a suitable active quest, or explicitly defer it.
