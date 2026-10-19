---
name: sns-receipt-provenance
description: "Read-only SNS-S-S standing-request and receipt provenance preflight. Use for exact-source snapshots, policy-byte bindings, trigger IDs, and append-only corrections. Exclude general science, quest selection, scheduler edits, and authority changes."
---

# SNS receipt and provenance preflight

Check an SNS request or proposed receipt against its source and task. Return findings or a reviewable draft. Do not publish, merge, write canonical records, run science, or grant execution authority through this skill.

## Resolve the source

Read repository `AGENTS.md`, exactly one active role contract, and the current standing-policy pointer and selected policy. Load accepted Monthly supplements and quest/protocol records when relevant. These sources and repository validators remain authoritative.

For prospective work, freshly observe accepted main and open ownership; pin reads to that commit. For offline fixtures, use the supplied observations and audit time and label them as fixture evidence. Never claim a live GitHub observation. Historical replay retains its original source, policy and qualification context; it cannot authorize a new action.

If a newer observation differs from the draft source, preserve the old draft as historical and require refreshed bindings before publication. An internally valid snapshot does not establish freshness.

## Use existing repository tools

Read only the helper needed:

| Need | Existing implementation |
|---|---|
| Role/scope/path/budget/expiry checks | `python -m automation.cli validate-standing-request --request REQUEST.json --now UTC_TIME` |
| Snapshot from accepted Git objects | `scripts.provenance_snapshot.snapshot_for_loop(root, loop_id, source_commit, open_prs)` |
| Connector rows and fingerprint | `automation.provenance.snapshot_from_connector_records`, `validate_state_snapshot` |
| Receipt envelope, IDs, full validation | `automation.provenance.build_run_receipt_v2`, `automation.ids.new_run_id`, `automation.receipts.validate_run_receipt` |

Use read-only validation against the supplied source. Do not call the hosted helper's network entrypoint for offline fixtures. If computation or access is missing, report the limitation; never invent IDs, hashes or passed checks.

## Check the bindings

- Match receipt/snapshot commits to the applicable observation. Compare named record paths and blob identities to Git source, not merely self-declared hashes.
- Preserve policy text byte-for-byte, including whitespace and final newline. Parsed JSON equivalence is insufficient. Bind both `standing_pointer` and `standing_authority` to exact accepted bytes.
- Include base snapshot roles plus task-dependent records. A base helper does not prove every decision dependency was inspected.
- Validate the concrete request under the selected policy with all four budgets and cumulative transaction count. Do not relabel an action or alter paths to bypass rejection.
- Preserve original trigger identity across slices and implementation/merge requests, normalized as the contract specifies. A correction does not grant another experiment.
- For a complete receipt, validate `standing_execution`, required check evidence, decision effect, continuity and terminal state with the existing validator. Structural PASS establishes neither scientific truth nor current ownership or execution permission.
- Keep accepted records immutable. Corrections are new linked receipts. Empty requests require genuine `NO_ACTION` with no effects.

## Return evidence

State scope, exact source/time, fixture versus live observation, actual checks, all blockers, and one lawful next action. Distinguish request validity, snapshot consistency, freshness and full receipt qualification. Partial validation is not publication permission. Use repository terminal states where applicable; retain UNKNOWN and negative evidence.

Operational requirements remain in their contracts if this skill is unavailable. Token counts, calls and receipt volume are diagnostics, never success quotas.
