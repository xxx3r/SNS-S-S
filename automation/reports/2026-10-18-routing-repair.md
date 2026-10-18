# Dedicated human-owned Weekly routing repair — October 18

## Problem and authorization

PR #122's late authority finding exposed a mismatch: Weekly's accepted contract
and ownership table assign direction reconciliation across quest/index/graph,
short memory and dispositions, but the standing validator's `route` action
accepts only memory, receipts and PR lifecycle files. An otherwise legitimate
reconciliation fails with `write outside action surfaces`.

M explicitly authorized publishing the governance records and removing the
concrete governance obstructions tonight. This dedicated human-owned change
implements only that identified routing repair. It is not a running loop
rewriting its own permissions under standing authority. No other organization
redesign, scientific decision, renewal, or scheduler change is authorized here.

## Bounded change

Only `weekly-evidence-synthesis` plus action `route` gains these path patterns:

- `quests/active/**`
- `quests/dispositions/**`
- `quests/research_graph.json`
- `calendar/roundups/**`

Such a request must cite accepted evidence. Active-quest/graph requests must
also bind `routing_source_commit` to the receipt source. The CLI validates the
actual proposed worktree against that Git source: active file names, numbered
index IDs/targets, quest identity/status/priority/tags, and all graph data must
remain unchanged. Requested active paths must already exist. This permits
routing prose reconciliation but no membership, metadata or graph transition.
Ordinary routing to existing memory surfaces retains its prior behavior. Existing role write surfaces, protected
paths, scope, expiry, transaction ceilings and aggregate budgets still apply.

Triage and Daily gain no new action surfaces. Raw quest actions, proposed and
completed quest files, scientific implementation files and authority code remain
outside routing. Activation/retirement, priority changes, consolidated beliefs,
and scientific decisions retain their separate contract requirements. The transition guard checks these structural invariants; semantic review still
checks the legitimacy of the routing prose.

## Tests and preservation

Regression coverage exercises one complete realistic Weekly reconciliation,
rejects the same request without accepted evidence, rejects raw proposals,
quest transitions, scientific source and protected control paths, and rejects
each added surface for both other operational roles. Full qualification and
exact-head review are required before merge.

Accepted policies, contracts, schemas, historical receipts, raw proposals,
scientific fixtures and outputs remain unchanged. The current October expiry
and SYNTH/STOR scientific stops remain in force. No simulation campaign or new
independent scientific evidence is produced.

## Handoff

PR #123 accepted the correction at `342eae9dfc352b53062c759371c0fc225da2008d`
after all hosted gates and exact-head automated review completed clean. Both
original #122 threads are resolved. This transaction starts from that fresh
accepted source, reconciles #122/#123 lifecycle and advances the live next move.
The midmonth packet is review evidence; it does not claim a completed Monthly
review or future renewal. The next research slice remains zero-new-world SIM3
delivery attribution, with existing fixture coordinates held fixed.

## Pre-merge P1 correction

Automated review of the first PR124 head correctly found that path permission
alone could disguise a coordinated membership transition as routing. That head
was not merged. The correction validates actual source/result trees and rejects
coordinated file/index/graph additions and removals, index-only changes, quest
identity/status/priority changes and graph edits. Receipt validation binds the
request source to its enclosing receipt and replays against the immutable
receipt-introduction commit; later separately authorized lifecycle changes do
not invalidate an accepted routing receipt. New uncommitted receipts check the
current proposed worktree. No historical receipt bytes are rewritten.
