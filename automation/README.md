# SNS Autonomous Transaction Layer

This directory coordinates daily, weekly, monthly, and audit research loops without changing SNS physics, thermal/storage conclusions, ARCI weights, quest hypotheses, or active scientific implementations.

## Authority flow

```text
platform safety / explicit human instruction
  -> AGENTS.md stable law
  -> active versioned loop contract
  -> issue / PR acceptance slice
  -> active quest
  -> monthly governance
  -> accepted weekly evidence
  -> compact memory
  -> historical records
```

Daily executes. Weekly proposes from evidence. Monthly governs shared state. Audit observes and recommends.

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

A receipt or semantic event is never edited after publication. Corrections are new records linked to the original ID. Human-readable long logs and audit reports are generated views and may be regenerated.

## Optimistic concurrency

Every implementation run records its source commit and state hashes. Immediately before publishing, compare the current snapshot. Governance or PR-ownership changes block stale publication; unrelated source movement may be rebased only after revalidation.

## Activation and retirement

A contract becomes active only after merge to `main`, successful parser and semantic tests, available receipt tooling, compatibility documentation, and an external scheduled prompt that names the contract version. Retired contracts remain in Git and require explicit replay mode.

## Scientific boundary

These tools govern coordination and evidence provenance. They do not establish flight readiness, alter physical assumptions, or turn a simulation PASS into hardware qualification.
