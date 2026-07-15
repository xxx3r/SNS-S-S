# Known Identifier Collision Baseline

The active Summer 2026 quest index contains eight unique IDs, and the completed index contains `QST-STOR-0001`. No cross-queue duplicate is accepted by the new validator.

Historical manually allocated session lines remain preserved in `memory/mem_log_long_0000_0999.md`. They are not rewritten into synthetic immutable receipts. New run identity uses `RUN-<UTC-microsecond>-<loop>-<80-bit-token>` and exclusive-create receipt files.

Evidence, claim-cluster, belief-event, quest-action, and run identifiers use separate namespaces. Duplicate source fingerprints and duplicate IDs are validation errors.
