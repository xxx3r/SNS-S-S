# Weekly bootstrap incident — 2026-09-13

The September 13 Weekly run reported source `94818f80c865dd5db83aa07c3f0003da5a464e2a`, which was the September 5 repository state, while current accepted main was `ced5b459711a808333cec198d2ee732cc3eeb094`.

This caused the run to interpret the retired Weekly v1 contract and an old evidence horizon. It stopped without publishing research state. No scientific result was corrupted; one Weekly delivery opportunity was lost.

Classification: `STALE_SOURCE_BOOTSTRAP / PRIOR_RUN_CONTEXT_REUSE`.

For the September 20 review, count this as an orchestration reliability incident with medium operational severity and zero scientific corruption. The fail-closed provenance behavior was correct, while the initial source selection was stale.
