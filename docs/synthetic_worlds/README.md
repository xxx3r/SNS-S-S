# Synthetic Worlds Public Import

## Status

- Public owner: `SNS-S-S`
- Candidate identity: `synthetic_worlds`
- Candidate version: `0.1.0-candidate`
- Human release state: `APPROVED_FOR_PUBLIC_IMPORT`
- Import terminal state: `SNS_SYNTHETIC_WORLD_CORE_IMPORTED`
- Campaign state: `NEEDS_GOVERNANCE_REVIEW`

This directory documents the deliberate one-way import of a qualified, hash-bound synthetic-world snapshot. The imported Python modules and tiny fixture bytes are unchanged from the approved candidate. SNS-S-S owns this public copy independently. It has no private checkout, token, package registry, submodule, CI bridge, or runtime synchronization dependency.

## Public layout

- `src/sim/synthetic_worlds/`: exact imported runtime modules
- `configs/synthetic_worlds/basic_world.json`: exact deterministic example recipe
- `outputs/synthetic_worlds_import/shards/`: exact four-record, two-shard fixture
- `docs/synthetic_worlds/APPROVED_EXPORT_MANIFEST.json`: exact pre-approval export manifest retained as public-safe hash provenance
- `src/sim/SYNTHETIC_WORLDS_IMPORT_MANIFEST.json`: SNS-owned destination map, approval record, hashes, omissions, and limitations
- `tests/test_synthetic_worlds_public_import.py`: public hash, boundary, import, and round-trip checks

The approved export manifest records `human_release_state: NOT_REVIEWED` because it is the immutable pre-decision candidate receipt. The SNS import manifest separately records the later human decision `APPROVED_FOR_PUBLIC_IMPORT`. The original export manifest is not edited after approval.

## Deliberate omissions

The public import copies only exact allowlisted bytes needed for public operation and reproducibility. It does not publish the private review narrative, repository-local ignore policy, or the private staging-layout test harness. Their approved dispositions remain represented through the export-manifest and qualification hashes. SNS-S-S supplies its own public boundary tests.

## Evidence boundary

Synthetic-world output is evidence about declared SNS models and experiment contracts. It is not physical-world validation, flight qualification, hardware readiness, or proof that a material, package, orbit, or thermal design is realizable.

## Governance boundary

This import does not activate `QST-SYNTH-0001`, change the active quest queue, or begin the three-arm thermal stress campaign. The campaign requires a lawful active slot or an accepted bounded attachment under monthly governance. Until then, the imported core may be reviewed and reproduced but not treated as an active autonomous research quest.

## Verification

```bash
python -m pytest -q tests/test_synthetic_worlds_public_import.py
```

The test verifies destination SHA-256 and byte identities, the approved export-manifest self-hash, absence of prohibited private identifiers and network dependencies, deterministic generation, strict shard validation, and an isolated tiny round trip.
