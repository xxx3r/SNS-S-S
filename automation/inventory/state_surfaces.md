# SNS Autonomous State-Surface Inventory

Status: frozen baseline for Issue #24 implementation  
Baseline commit: `b7f924a122a8282a3766cbbf8d6bcb8a8bfdef33`

| Surface | Prior behavior | Transactional disposition |
|---|---|---|
| `AGENTS.md` | Full spawn procedure and stable engineering law | Stable law, authority order, contract routing, terminal vocabulary |
| `AURORA.md` | Duplicated spawn reads plus scoring | Evidence scoring only; contract handles execution procedure |
| `memory/mem_log_short.md` | Daily-updated spawn state | Compact monthly-governed canonical move; daily/weekly propose changes |
| `memory/mem_log_long_0000_0999.md` | Mandatory append by multiple loops | Frozen legacy record; generated log derives from immutable receipts |
| `quests/active/**` | Daily and calendar tools could modify | Monthly queue authority; daily scoped evidence only |
| `quests/completed/**` | Quest completion records | Monthly-enacted transition with cross-queue ID validation |
| `quests/proposed/**` | Not separated | Explicit proposal queue and semantic actions |
| `quests/blocked/**` | Not separated | Explicit blocker record with reactivation condition |
| `calendar/roundups/**` | Human-readable evidence and actions mixed | Human-readable weekly view generated alongside immutable evidence events |
| `calendar/belief_ledger.csv` | Mutable weighted ledger | Preserved historical artifact; new changes use immutable belief events and generated consolidation |
| `calendar/monthly/**` | Monthly synthesis when present | Authoritative queue and belief reconciliation |
| `automation/contracts/**` | Absent | Versioned behavior contracts in Git |
| `automation/runs/**` | Sequential/shared Markdown history | Collision-safe immutable receipt per trigger |
| `automation/pr_lifecycle/**` | Inferred from GitHub state | Explicit bounded lifecycle, ownership, split, stale, and superseded states |
| open branches and PRs | Human interpretation | Monthly lifecycle reconciliation and one owner per acceptance slice |
| scheduled platform prompts | Full procedure outside Git | Thin bootstrap naming repository contract and trigger metadata |

The normative machine-readable ownership matrix is `automation/state_ownership.json`.
