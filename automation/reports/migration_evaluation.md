# Issue #24 Transaction-Layer Evaluation

## Compared architectures

| Stage | Identity | History surface | Governance | Semantic records | Expected failure profile |
|---|---|---|---|---|---|
| Current baseline | manually allocated session lines | shared Markdown append | overlapping prompt instructions | roundup/ledger conventions | collisions, log conflicts, stale ownership |
| Contracts only | named contract version | shared Markdown append remains | authority documented | existing conventions | behavior reconstructable, collisions remain |
| Contracts + receipts | collision-safe run ID | immutable per-run JSON | conflict visible in receipt | existing conventions | identity/logging collisions removed |
| Full transaction layer | namespaced immutable IDs | generated views from events | ownership matrix + CAS recheck | evidence, belief, quest action, PR lifecycle | conflicts terminate explicitly and remain auditable |

## Representative concurrency fixtures

The automated suite covers the plan’s six canonical scenarios:

1. **Daily + weekly from one commit:** unique IDs and independent receipt paths.
2. **Daily implementation + monthly reprioritization:** governance hash change produces `GOVERNANCE_CHANGED` rather than stale publication.
3. **Two daily triggers on one quest:** PR ownership hash change produces `PR_OWNERSHIP_CHANGED`; the second run continues or blocks instead of opening a duplicate owner.
4. **Five reports of one demonstration:** one claim cluster retains five sources but zero independent replications.
5. **Evidence falsifies an active quest:** weekly authority cannot enact deletion; it emits a proposal or emergency escalation for governance.
6. **Audit overlaps in-flight work:** the frozen cutoff includes pre-cutoff receipts and reports later work separately.

## Gates

- collision-safe ID generation uses UTC microseconds, loop namespace, and 80 random bits;
- receipt publication uses filesystem exclusive-create and duplicate-ID scans;
- correction events are linked new receipts;
- contract parser enforces one active version per loop and explicit replay for retirement;
- repository validation checks cross-queue IDs, active queue bounds, event provenance, PR ownership, receipt references, and artifact existence;
- belief magnitude and confidence scales are normalized;
- quest refinements cannot masquerade as new quests;
- weekly evidence cannot enact queue-wide governance;
- stale, split, superseded, abandoned, and merged PR states are explicit;
- information inheritance requires an explicit later consumption edge.

## Cost and complexity judgment

The implementation uses only the Python standard library at runtime. Human-readable roundups, monthly syntheses, and quest files remain. Machine records are the substrate, not the only interface. Infrastructure is isolated from simulation and ARCI modules except for the backward-compatible roundup-to-quest bridge.

## Acceptance evidence

Local isolated transaction suite before publication: `23 passed`. GitHub Actions and the full repository semantic validator are authoritative for the merged result and are recorded in the final implementation receipt.
