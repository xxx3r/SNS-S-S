# Issue #38 Transaction 5: Queue-Invariant Validation

- Generated at: `2026-09-02T17:21:02.902433Z`
- Exact source main: `15e540d91fad65fa084471e5f428223edd9ad5e1`
- Owner: `system-audit`
- Authority: explicit human continuation of Issue #38
- Scope: active queue IDs, README membership, cross-queue uniqueness, and duplicate-branch invariants

This report validates repository invariants without changing queue membership, priorities, quest files, memory, beliefs, delegations, scheduler state, or scientific implementation.

## Active queue

The canonical active index lists exactly eight distinct IDs, each once:

1. `QST-STOR-0002`
2. `QST-SIM-0002`
3. `QST-SIM-0003`
4. `QST-PV-0001`
5. `QST-META-0001`
6. `QST-ARCI-0001`
7. `QST-CALENDAR-0001`
8. `QST-FUND-0001`

Each indexed active quest has a matching quest file. The active directory also contains three evidence-slice files for `QST-STOR-0002`; they share one canonical parent ID and do not create duplicate queue membership.

## Cross-queue uniqueness

- Active canonical IDs: **8**
- Completed quest IDs present in the completed queue: **5**
- Proposed quest IDs: **0**
- Blocked quest IDs: **0**
- Duplicate canonical IDs within a queue: **0 observed**
- Active/completed/proposed/blocked intersections: **0 observed**

The completed IDs are historical and distinct from the active set. The proposed and blocked indexes contain no quest records, so no cross-queue collision exists.

## Branch invariants

The current live connector view contains one open PR (#61) and one open head branch. Duplicate open head branches: **0 observed**. This preserves transaction 4’s evidence-only disposition; PR #61 is not rebased, merged, closed, or reconstructed.

## Result and boundary

Queue IDs, index membership, cross-queue disjointness, and duplicate-branch invariants are valid at the exact source main. No mutation was required. The next bounded campaign step is transaction 6: validate recent immutable receipt IDs, schema conformance, and referenced artifact existence.
