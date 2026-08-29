# SNS Autonomous Transaction Layer

This directory coordinates pre-game, daily, weekly, monthly, and audit research loops without changing SNS physics, thermal/storage conclusions, ARCI weights, quest hypotheses, or active scientific implementations.

## Authority flow

```text
platform safety / explicit human instruction
  -> AGENTS.md stable law
  -> active versioned loop contract
  -> executable schema + semantic validator
  -> issue / PR acceptance slice
  -> active quest
  -> monthly governance + delegation
  -> accepted weekly evidence
  -> compact memory
  -> historical records and older plans
```

Pre-Game routes and authorizes. Daily executes. Weekly proposes from evidence. Monthly governs shared state. Audit observes and recommends.

## Four organization layers

- **Prompt Engineering**: `prompts/bootstrap.v1.md` is the tiny external fire starter. Runtime prompts name only a loop ID and dynamically resolve repository law.
- **Loop Engineering**: contracts, immutable receipts, provenance snapshots, correction law, ownership, and hosted validation govern one agent lifetime.
- **Graph Engineering**: `../quests/research_graph.json` stores typed research topology. Hard `requires` edges form an acyclic execution graph; lineage/revisit edges may cycle.
- **Orchestration Engineering**: `runtime_manifest.json` declares desired external loop cadence/enabled state and is compared with live scheduler state for drift.

Lineage/evidence runs through all four layers rather than forming a separate authority layer.

## Canonical record dialect

`automation/schemas/*.schema.json` and the matching Python validators are normative for record identity and field shape. `docs/SNS_autonomous_loop_schema_reconciliation.md` explains compatibility with accepted history.

Historical `sns.loop-run.v1` receipts remain immutable. New run receipts use `sns.loop-run.v2` with an inspectable `sns.state-snapshot.v1` instead of an agent-invented opaque state hash. Connector-authored snapshots record the exact Git blob SHA returned by repository reads for required canonical records plus normalized open-PR ownership rows.

Use `automation.ids.new_event_id` and `automation.ids.new_run_id`. New immutable identifiers use `RUN-`, `EVID-`, `CLM-`, `BEL-`, and `QA-`, followed by a UTC timestamp, namespace, and 20-hex collision suffix.

Never validate new records only by comparing them with prose. Before publication run:

```bash
python -m pytest -q tests/test_automation_*.py
python -m automation.cli validate-repository
```

## Layout

- `contracts/`: versioned executable behavior agreements;
- `schemas/`: machine-readable record contracts;
- `prompts/`: external bootloader prompt surface;
- `runtime_manifest.json`: desired external orchestration;
- `runs/YYYY/MM/`: immutable run and correction receipts;
- `pr_lifecycle/`: one explicit lifecycle record per automation-owned PR;
- `inventory/`: frozen migration baseline and ownership analysis;
- `reports/`: generated logs, metrics, and migration evidence;
- `state_ownership.json`: authoritative mutation and reconciliation matrix;
- `provenance.py`: inspectable connector/local state-snapshot and receipt-v2 builder;
- `research_graph.py`: typed graph and ready-frontier logic;
- `routing.py`: deterministic priority/blocker router fed by graph readiness;
- `orchestration.py`: bootloader renderer, runtime-manifest validation, and drift comparison.

## Commands

```bash
python -m automation.cli validate-repository
python -m automation.cli write-receipt path/to/staged-receipt.json
python -m automation.cli snapshot-state --source-commit <sha> --record ROLE=PATH ... --output snapshot.json
python -m automation.cli build-receipt-v2 --draft draft.json --snapshot snapshot.json --output receipt.json
python -m automation.cli graph-frontier --active-ids QST-STOR-0002,QST-ARCI-0001
python -m automation.cli runtime-drift --observed observed_runtime.json
python -m automation.cli generate-long-log
python -m automation.cli audit \
  --cutoff-time 2026-09-01T14:00:00Z \
  --cutoff-commit <main-sha>
```

## Immutability and corrections

A receipt or semantic event is never edited after publication. Corrections are new records linked to the original ID. `sns.loop-run.v2` correction receipts repair provenance/record semantics without granting a second scientific implementation attempt or consuming a second implementation-receipt budget. Human-readable long logs and audit reports are generated views and may be regenerated. A still-unmerged draft record may be corrected before acceptance because it has not entered canonical history.

## Optimistic concurrency

A new run captures an inspectable canonical state snapshot before work. Immediately before publication, re-read the same canonical roles and live PR ownership and compare exact identities. Governance, delegation, graph-readiness, authorization, or PR-ownership drift blocks stale publication according to its scope. The v2 snapshot is designed to be reproducible through GitHub connector reads even when no local shell exists.

## Activation and retirement

A contract becomes active only after merge to `main`, successful parser and semantic tests, available receipt tooling, and compatibility documentation. External scheduled prompts do **not** name a contract version; the bootloader resolves the one repository contract currently marked `status: active`. Retired contracts remain in Git and require explicit replay mode.

## Scientific boundary

These tools govern coordination and evidence provenance. They do not establish flight readiness, alter physical assumptions, or turn a simulation PASS into hardware qualification.
