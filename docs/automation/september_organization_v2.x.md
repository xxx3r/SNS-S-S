# September Organization v2.x

## Purpose

This is one bounded organizational tuning transaction for the September experiment. It improves the instrument's ability to preserve inheritance, terminalize stale administrative surfaces, and observe communication cost. It does not choose a scientific route.

## In scope

- A frozen audit cutoff now requires an exact reachable commit ancestry set. Time alone is insufficient.
- Receipts may expose typed prior-state references for RUN, EVID, BEL, QA, and repository artifact paths, plus a recorded decision effect.
- The run-only inheritance value remains available as a diagnostic submetric.
- Generated audit metrics expose contract-complete inheritance, machine-visible lineage gaps, proposal-to-authorization latency, authorization-to-first-artifact latency, administrative transaction count, and administrative transactions per scientific artifact.
- Monthly Governance v1.2 explicitly reviews open PR lifecycle and quest terminalization, reconciles canonical memory once per accepted transition, and publishes one bounded triage delegation.

## Receipt surface

New v2.x receipts use an inheritance list such as:

    {
      "inheritance": [
        {
          "kind": "RUN",
          "ref": "RUN-...",
          "decision_effect": "Used the prior accepted synthesis to route this transition."
        },
        {
          "kind": "artifact",
          "ref": "calendar/roundups/2026-08-23.md"
        }
      ],
      "decision_effect": "The transition accepted one bounded organizational disposition.",
      "observability": {
        "proposal_at": "RFC3339 timestamp",
        "authorization_at": "RFC3339 timestamp",
        "first_artifact_at": "RFC3339 timestamp",
        "administrative_transactions": 1,
        "scientific_artifacts": 0,
        "continuity": "inherited"
      }
    }

A v1.2 receipt must include typed inheritance or explicitly declare independent continuity, and must record a non-empty decision effect. Existing receipts remain immutable and are measured through the compatible run-only diagnostic and the new lineage-gap view.

## Closure and continuity

Monthly may close an open PR as superseded historical evidence when its contents and review history are preserved, its lifecycle record is written, and no merge or reconstruction occurs. A missing typed handoff is emitted as a machine-visible lineage gap; no agent persona or memory claim repairs it implicitly.

## Boundaries

This transaction does not alter active quests, scientific code, experiment outputs, consolidated beliefs, or scheduler state. The accepted Monthly transition separately owns the September delegation, canonical-memory transition, PR #61 disposition, and ordered scheduler wake.

## Acceptance

1. The audit cutoff rejects a pre-cutoff receipt whose source commit is outside the exact cutoff ancestry.
2. The run-only diagnostic remains reproducible.
3. Typed inheritance requires a resolvable reference and decision effect.
4. Latency and administrative-cost metrics are deterministic.
5. The active Monthly v1.2 contract is unique; v1.1 remains replayable history.
6. Existing repository validation and all hosted backstops pass.
