# Autonomous Research Governance Design — 2026-08-07

## Question

How should SNS-S-S expand from one bounded Daily Research Operator without losing the auditability, ownership discipline, and scientific honesty that the August experiment is meant to test?

The immediate empirical problem is **approval-latency amplification**: a low-risk proposal can terminate one daily run, consume a later run for approval, consume another run for acknowledgement, and only then reach implementation. This creates administrative motion without scientific information gain.

The design below is grounded in three auto-research references and the SNS-S-S August incident record.

## 1. Ning et al. 2026: lineage is active research state

Reference: Jingjie Ning et al., *Auto Research with Specialist Agents Develops Effective and Non-Trivial Training Recipes*, arXiv:2605.05724.

The paper treats auto research as a closed empirical trajectory rather than a generated report. A submitted trial carries a hypothesis, executable edit, evaluator-owned outcome, and feedback that shapes later proposals. Specialist roles partition the editable surface while a shared compact lineage preserves current bests, failures, diffs, timings, and neighboring-role outcomes.

Several design observations transfer directly to SNS-S-S:

- **Externally owned measurement matters.** The editable recipe does not own its score. SNS analog: implementation agents must not rewrite the validator, authority boundary, or scientific success criterion they are being judged against.
- **Failure rows are useful state.** Crashes, size failures, runtime overruns, and gate misses are preserved and fed forward. SNS analog: blockers and failed checks are lineage, not wasted days or records to hide.
- **Compact lineage beats amnesia.** The Parameter Golf no-lineage control performed materially worse and collided with budget limits much more often. SNS analog: each new agent should receive current accepted state, recent failures, current owner, and current authorization rather than re-discovering the laboratory from prose.
- **Specialization broadens the search while preserving boundaries.** Specialist prompts explicitly define scope, non-scope, and edit radius. SNS analog: governance triage should be a different role from implementation, with a deliberately tiny edit radius.
- **One session may contain a concrete follow-up.** Their global rule permits a second trial only when the first result exposes a specific next edit. This is useful evidence against treating every micro-transition as a new day. A bounded agent may continue through a direct mechanical follow-up while still preserving each measured trial.
- **Anti-anchoring is explicit.** Failed or saturated proposal patterns are surfaced so agents do not repeatedly revisit the same high-salience move. SNS analog: consumed, expired, rejected, and completed authorizations must remain visible so the next operator cannot repeat them.

The lesson is not “run many agents.” It is “give each role a clean surface, trusted feedback, compact lineage, and enough local continuity to convert feedback into the next measured move.”

## 2. Lu et al. 2024: separate generation, iteration, and review

Reference: Chris Lu et al., *The AI Scientist: Towards Fully Automated Open-Ended Scientific Discovery*, arXiv:2408.06292.

The AI Scientist separates idea generation, experiment iteration, paper writing, and automated review. During experiment iteration it returns failures to the coding agent, permits bounded retries, records experimental notes, and replans subsequent experiments from observed results.

The framework is important to SNS-S-S for both its strengths and its failures:

- A separate reviewer/area-chair-like stage can improve the pipeline without becoming the experimenter.
- The system can competently execute and iterate while still misinterpreting why a result worked, hallucinating details, or implementing an idea incorrectly.
- Automated review is useful but not infallible; some substantive domain errors required human expertise to identify.
- The authors explicitly recommend stronger verification linking code and experiments and strict sandboxing after agents attempted to expand runtime limits, spawn processes, and create huge storage outputs.

SNS implication: the Pre-Game Game Master should behave more like a constrained area chair than a scientist. It can check authority, scope, evidence, ownership, and readiness, but it must not convert an unresolved scientific interpretation into an administrative approval.

## 3. Karpathy autoresearch: the research-org code is itself an experiment

Primary reference: `https://github.com/karpathy/autoresearch`.

Karpathy's minimal design makes the split unusually clear:

- `prepare.py` contains fixed evaluation/runtime machinery and is not edited;
- `train.py` is the bounded scientific surface the agent edits;
- `program.md` is the research-organization instruction surface edited by the human;
- each experiment has a fixed wall-clock budget and one objective metric.

The README explicitly frames `program.md` as the object humans iterate to improve the autonomous research organization and notes that additional agents can be added over time. This is directly analogous to the August SNS-S-S observation month: changing the organization is not contaminating the experiment when the organizational changes themselves are versioned, audited, and evaluated.

A secondary May 2026 BirJob synthesis of autoresearch use cases is useful mainly as a warning: metric gaming, overfit winners, and the “creativity ceiling” all reinforce that prompts are not substitutes for immutable evaluators and that a short-horizon ratchet should not own longer-horizon structural decisions. Those claims should be treated as secondary reporting rather than primary experimental evidence.

## 4. SNS design consequence: two-speed governance

The research suggests a five-loop organization:

```text
Pre-Game Governance Triage
          ↓ bounded authorization / clean runway
Daily Research Operator
          ↓ measured artifacts + failures
Weekly Evidence Synthesis
          ↓ normalized evidence + proposals
Monthly Constitutional Governance
          ↓ queue, beliefs, delegation, canonical direction
System Audit
          ↘ observes all layers
```

The new role exists to remove **administrative latency**, not to add another scientific opinion.

### Decision ladder

| Level | Decision class | Owner | Intended latency |
|---|---|---|---|
| L0 | Local reversible implementation detail inside accepted scope | Daily Research Operator | Same run |
| L1 | Bounded reversible sub-experiment or mechanically verifiable lifecycle decision inside delegation | Pre-Game Governance Triage | Same day / next available slot |
| L2 | Quest membership/order, consolidated belief, canonical move, major architecture decision | Monthly Governance | Constitutional transaction; scheduled monthly or explicit trigger |
| L3 | Protected scientific assumption, external/public action, strategic or reserved authority | Human | Explicit handoff |

The critical distinction is that **monthly authority is not the same thing as month-long latency**. Monthly governance remains the long-horizon constitutional team, while routine L1 decisions are delegated prospectively.

## 5. Work-conserving law

The organization should be considered broken if it repeatedly produces:

```text
proposal -> approval -> acknowledgement -> implementation
```

The desired path is:

```text
pre-game triage -> authorization artifact -> daily implementation
```

Therefore:

1. Approval does not consume the research slot.
2. Acknowledgement is not an artifact.
3. A valid bounded authorization is consumed directly by implementation.
4. Triage may batch several administrative decisions in one receipt, while implementation retains one-owner/one-slice law.
5. Triage cannot widen its own delegation.
6. Scientific uncertainty remains a valid stop condition.

## 6. Delegation and authorization

Monthly governance publishes a machine-readable delegation envelope. Triage may then create immutable machine-readable authorizations only inside that envelope.

An authorization must bind:

- active quest ID;
- acceptance slice;
- source commit;
- delegation ID;
- expiry;
- allowed implementation surfaces;
- budgets;
- exactly one implementation PR and one implementation receipt;
- mandatory checks;
- stop conditions;
- exact next action.

This converts “approved” from prose into executable lineage.

## 7. August experiment and September audit

The new organization should be evaluated, not assumed successful. Add these metrics to the September audit:

- proposal-to-decision latency;
- authorization-to-first-artifact latency;
- handoff hops before execution;
- approval-only runs;
- acknowledgement-only runs;
- same-day/next-slot execution rate after valid authorization;
- proposals waiting more than 48 hours;
- unnecessary escalation rate;
- administrative transactions per scientific artifact;
- scientific artifacts per scheduled research day;
- authorization issue/consume/expire/reject counts;
- delegation violations;
- duplicated acceptance slices after authorization;
- information inherited from prior failures and reviews.

The success criterion is not maximum throughput. It is higher **measured information gain per research day** without losing reproducibility, authority boundaries, or human legibility.

## 8. Initial August posture

Do not activate a ninth quest merely to prove the new governance system works. The initial delegation should apply only to the eight already-active quests and permit bounded `refine_existing` work. `QST-SYNTH-0001` can therefore remain a future full-quest candidate while a suitably bounded synthetic-world experiment may be authorized under an existing active quest if its experiment freeze, holdout separation, budgets, evidence language, and falsifiers are explicit.

This is intentionally conservative: the new member should first prove that it can clear the runway without quietly becoming the pilot.
