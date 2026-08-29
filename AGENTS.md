# AGENTS.md: SNS-S-S Stable Law

SNS-S-S is a formal research instrument for Solar-Nano-Sphere swarm dynamics, explicit energy-chain modeling, asteroid-resource intelligence, and evidence-driven research execution. It is not flight software and must never imply hardware readiness.

## Authority order

1. platform safety and explicit human instruction;
2. this stable law;
3. the selected active contract in `automation/contracts/`;
4. executable record schemas in `automation/schemas/` and their matching validators;
5. the active issue and PR acceptance slice;
6. the active quest record;
7. accepted monthly governance and its current delegation envelope;
8. accepted fast-governance authorization for the bounded slice, when present;
9. accepted weekly evidence;
10. `memory/mem_log_short.md`;
11. historical logs and older plans.

No lower layer silently overrides a higher layer. For automation record identity or field shape, `docs/SNS_autonomous_loop_schema_reconciliation.md` explains the executable authority. Older planning examples are historical and non-normative when they conflict with schemas or validators.

## Loop routing

The platform prompt supplies a `loop_id`, not a contract version. After reading this stable law, resolve exactly one contract whose front matter has that `loop_id` and `status: active`. Never select a retired/proposed contract because a scheduler prompt, old receipt, memory file, or historical plan names it.

The research-loop IDs are:

- `daily-governance-triage`;
- `daily-research-operator`;
- `weekly-evidence-synthesis`;
- `monthly-governance`;
- `system-audit`.

The ordinary operating sequence is **pre-game triage -> daily execution -> weekly evidence -> monthly constitutional direction**, with audit observing the system rather than governing it. The desired external instantiation/cadence is declared separately in `automation/runtime_manifest.json`; repository contracts define lifetime behavior, not scheduler state.

Every trigger ends with one immutable receipt under `automation/runs/**` and one explicit terminal state. Triage may disposition multiple independent administrative candidates in one run; the Daily Research Operator still produces one smallest coherent implementation slice.

## Prompt bootloader law

`automation/prompts/bootstrap.v1.md` is the canonical external prompt surface. External schedulers may substitute the requested `loop_id`, but evolving institutional law belongs here, in active contracts, schemas, the research graph, and the runtime manifest.

A scheduler prompt must not hard-code contract versions, month-specific PR/issue lore, routing algorithms, schema field lists, scientific thresholds, or queue state. If the platform prompt conflicts with accepted repository law, fail closed and report the exact conflict rather than executing stale copied instructions.

## Work-conserving law

1. Approval does not consume the scientific research slot. Routine Level-1 governance runs before daily implementation.
2. Acknowledgement is not an artifact. A Daily Research Operator with a valid bounded authorization must attempt the authorized slice rather than spend a run restating approval.
3. Approved work begins immediately when bounded. The daily receipt records the consumed authorization ID.
4. Triage may authorize but may not implement science. It cannot widen its own delegation.
5. One implementation acceptance slice still has one current owner, at most one implementation PR, exactly one **budget-consuming implementation receipt**, and one terminal disposition. A provenance-only append-only correction does not grant or consume a second scientific implementation attempt.
6. Queue membership, priority, consolidated beliefs, canonical memory, major architecture choices, contracts, schemas, and external/public actions remain outside fast-governance authority.

## Instrument discovery

When a selected acceptance slice may benefit from reusable simulation, generation, validation, or analysis machinery, inspect the relevant entry in `docs/system/research_instrument_registry.md`. Registry entries advertise available tools but never activate a quest, change queue priority, grant evidence authority, or permit model writes. Read only entries relevant to the bounded acceptance slice.

## Record-shape and provenance law

Create immutable IDs only through the repository's canonical ID helpers when the record family has one. New run, evidence, claim-cluster, belief, and quest-action IDs use the canonical uppercase prefixes `RUN-`, `EVID-`, `CLM-`, `BEL-`, and `QA-`. Fast-governance authorization IDs use the schema-defined `AUTH-` format and delegation envelopes use `DELEG-` IDs.

Historical `sns.loop-run.v1` receipts remain immutable replay evidence. **New run receipts use `sns.loop-run.v2`.** v2 removes the agent-invented opaque `state_hash` as a concurrency claim and replaces it with `sns.state-snapshot.v1`: an inspectable list of canonical repository roles/paths and their exact Git blob SHAs, plus the observed open-PR ownership rows. The snapshot object itself is authority; its SHA-256 fingerprint is derivative convenience metadata.

Every v2 state snapshot must include at least:

- `AGENTS.md` as `stable_law`;
- the selected active contract as `active_contract`;
- `automation/state_ownership.json` as `state_ownership`;
- `quests/active/README.md` as `active_quest_index`;
- `quests/research_graph.json` as `research_graph`;
- `automation/runtime_manifest.json` as `runtime_manifest`;
- `memory/mem_log_short.md` as `canonical_memory`.

Add current delegation, authorization, monthly state, or other owned records when the selected contract depends on them. Connector-authored runs may use the Git blob SHA returned by each GitHub file read; missing local shell access never justifies an empty or placeholder digest. `automation.provenance` and `python -m automation.cli snapshot-state` define the deterministic reference implementation.

A receipt correction is a new immutable `sns.loop-run.v2` record with `receipt_kind: correction` and `correction_of`. It may repair provenance or record shape but may not smuggle a second scientific implementation, new result, new quest mutation, or weakened evaluator into the lineage. Correction receipts do not count against `max_run_receipts` implementation budgets; the original artifact remains visible.

Before publication, validate new records against the executable repository:

```bash
python -m pytest -q tests/test_automation_*.py
python -m automation.cli validate-repository
```

Do not copy lower-case `run_*`, `ev_*`, `be_*`, or `qa_*` examples from historical plans. Do not claim schema validation from manual comparison with prose. If executable validation fails, stop with an honest terminal state or correct only the still-unmerged records.

## Research graph law

`quests/research_graph.json` is the machine-readable topology of accepted research state. Quest Markdown remains the rich scientific record; the graph stores only the minimum routing semantics needed to expose structure.

- Typed nodes distinguish research quests, research infrastructure, public synthesis, routes, experiments, artifacts, and evidence.
- `requires` is the only hard execution-dependency edge. Its subgraph must remain acyclic and is used to derive the ready frontier.
- `contains`, `informs`, `unlocks`, `falsifies`, `competes_with`, `supports`, `supersedes`, and `revisit_after` preserve research lineage and may form cycles. This is how the program may spiral back to old questions without creating scheduler deadlocks.
- Priority is not dependency. First derive the graph-ready frontier, then apply accepted priority, stable active-index order, blocker scope, delegation, and one-owner law.
- Do not infer new scientific dependencies merely to make the graph visually connected. An absent edge means no accepted machine-enforced dependency has been established yet.
- Queue membership and priority remain monthly-owned. Graph routing selects among already-active lawful candidates; it does not activate or reprioritize quests.

## Orchestration law

`automation/runtime_manifest.json` is the desired research-runtime configuration. It records which loop instances should be scheduler-managed, their titles, cadence, timing mode, ordering, desired enabled state, and canonical bootloader surface. The external scheduler remains the execution platform, but its state is no longer invisible institutional state.

`automation.orchestration.compare_runtime_manifest()` compares a normalized live task snapshot against the manifest. System Audit must report drift rather than silently accepting a different organization. Runtime drift is not automatically a scientific blocker: classify its scope and effect. A missing/disabled Daily operator, stale hard-coded prompt, or inverted Pre-Game/Daily order is an orchestration defect even when repository contracts are healthy.

## Scientific and engineering invariants

1. Prefer explicit dataclasses, enums, units, and small inspectable functions.
2. Preserve units in names such as `_W`, `_Wh`, `_s`, `_K`, and `_m2`.
3. Resolve harvested energy into direct use, storage, delivery, or curtailment.
4. Separate score from confidence, especially in ARCI.
5. Keep mission assumptions configurable rather than hidden in code.
6. Preserve legacy compatibility intentionally; new work follows the Summer 2026 ontology.
7. Simulation PASS means declared model criteria passed, not space qualification.
8. Test every new behavior and record limitations, uncertainty, and falsifiers.
9. Keep active quests artifact-first and bounded to 1–8 entries.
10. Do not alter scientific claims through automation-infrastructure work.

## Shared-state law

`automation/state_ownership.json` is normative.

- Pre-game triage reads the current delegation, compact lineage, quest proposals, live PR state, accepted governance, and graph-ready frontier. It may create immutable bounded authorizations and mechanically synchronize unambiguous PR lifecycle facts, but it cannot mutate the queue, beliefs, canonical memory, or scientific implementation surfaces.
- Daily loops execute within accepted quest scope and may consume one valid triage authorization directly.
- Weekly loops normalize evidence and propose changes.
- Monthly governance owns queue-wide decisions, consolidated beliefs, stale/ambiguous work resolution, canonical memory, and the delegation envelope.
- Audit loops observe, measure, and recommend.

Raw run, evidence, belief, quest-action, delegation, and authorization records preserve history. Corrections or replacements are new linked or superseding records rather than silent rewrites. Shared Markdown append history is not a required write surface. Generated logs derive from immutable receipts.

## Decision ladder

- **L0:** local reversible implementation detail inside an accepted slice -> Daily Research Operator.
- **L1:** bounded reversible sub-experiment or routine mechanically verifiable lifecycle decision inside the current delegation -> Daily Governance Triage.
- **L2:** quest activation, reprioritization, retirement, canonical move, consolidated belief change, major architecture choice, ambiguous stale-work disposition -> Monthly Governance.
- **L3:** protected scientific assumption, external publication/action, strategic choice, or reserved authority -> Human.

Escalation is based on authority and evidence, not on calendar latency. Monthly governance is a constitutional role with a monthly scheduled review; it may also be explicitly triggered when a genuine non-delegable L2 decision cannot reasonably wait.

## Concurrency and PR law

Capture the v2 inspectable state snapshot before work. Recheck its canonical record identities, current governance/delegation/authorization, graph readiness, accepted source, and live PR ownership immediately before publication. One PR owns one quest acceptance slice. Continue the valid owner, split expanding work, and classify stale or superseded branches explicitly. Automatic merge remains conservative.

## Terminal states

Use only:

- `DONE`, `DONE_WITH_LIMITATIONS`;
- `BLOCKED_ENVIRONMENT`, `BLOCKED_MISSING_EVIDENCE`, `BLOCKED_CONFLICT`;
- `VERIFICATION_FAILED`;
- `NEEDS_SCIENTIFIC_DECISION`, `NEEDS_GOVERNANCE_REVIEW`, `NEEDS_APPROVAL`.

A precise blocker is a valid outcome. Do not continue merely to avoid reporting one. A blocker does not imply that the next scheduled daily run should spend its entire slot acknowledging the blocker; fast governance should disposition lawful L1 cases before implementation starts.

## Definition of done

An implementation acceptance slice is complete only when its artifact exists, checks are evidenced, assumptions and limitations are explicit, ownership is current, semantic repository validation passes, the receipt is immutable, any consumed authorization is current and scope-valid, graph readiness is satisfied, provenance is inspectable, and the next action is one concrete transition.
