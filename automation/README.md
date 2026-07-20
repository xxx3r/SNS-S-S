# SNS Autonomous Transaction Layer

This directory coordinates daily, weekly, monthly, and audit research loops without changing SNS physics, thermal/storage conclusions, ARCI weights, quest hypotheses, or active scientific implementations.

## Authority flow

```text
platform safety / explicit human instruction
  -> AGENTS.md stable law
  -> active versioned loop contract
  -> executable schema + semantic validator
  -> issue / PR acceptance slice
  -> active quest
  -> monthly governance
  -> accepted weekly evidence
  -> compact memory
  -> historical records and older plans
```

Daily executes. Weekly proposes from evidence. Monthly governs shared state. Audit observes and recommends.

## Canonical record dialect

`automation/schemas/*.schema.json` and the matching Python validators are normative for record identity and field shape. `docs/SNS_autonomous_loop_schema_reconciliation.md` provides copyable examples and supersedes conflicting lower-case examples in the original transaction plan.

Use `automation.ids.new_event_id` and `automation.ids.new_run_id`. New immutable identifiers use `RUN-`, `EVID-`, `CLM-`, `BEL-`, and `QA-`, followed by a UTC timestamp, namespace, and 20-hex collision suffix.

Never validate new records only by comparing them with prose. Before publication run:

```bash
python -m pytest -q tests/test_automation_*.py
python -m automation.cli validate-repository
```

## Layout

- `contracts/`: versioned executable behavior agreements;
- `schemas/`: machine-readable record contracts;
- `runs/YYYY/MM/`: immutable run receipts;
- `pr_lifecycle/`: one explicit lifecycle record per automation-owned PR;
- `inventory/`: frozen migration baseline and ownership analysis;
- `reports/`: generated logs, metrics, and migration evidence;
- `state_ownership.json`: authoritative mutation and reconciliation matrix;
- Python modules: dependency-light ID, receipt, semantic, concurrency, repository-validation, and audit tooling.

## Commands

```bash
python -m automation.cli validate-repository
python -m automation.cli write-receipt path/to/staged-receipt.json
python -m automation.cli generate-long-log
python -m automation.cli audit \
  --cutoff-time 2026-09-01T14:00:00Z \
  --cutoff-commit <main-sha>
```

## Immutability

A receipt or semantic event is never edited after publication. Corrections are new records linked to the original ID. Human-readable long logs and audit reports are generated views and may be regenerated. A still-unmerged draft record may be corrected before acceptance because it has not entered canonical history.

## Optimistic concurrency

Every implementation run records its source commit and state hashes. Immediately before publishing, compare the current snapshot. Governance or PR-ownership changes block stale publication; unrelated source movement may be rebased only after revalidation.

## Activation and retirement

A contract becomes active only after merge to `main`, successful parser and semantic tests, available receipt tooling, compatibility documentation, and an external scheduled prompt that names the contract version. Retired contracts remain in Git and require explicit replay mode.

## Scientific boundary

These tools govern coordination and evidence provenance. They do not establish flight readiness, alter physical assumptions, or turn a simulation PASS into hardware qualification.
