# AGENTS.md — SNS-S-S

# Arcade Loop Instructions (control plane)
- Treat this repo like an arcade cabinet: you are the player, progress is the score.
- Obey the Spawn Ritual: read `memory/mem_log_short.md`, `quests/quests_active.md`, the latest `calendar/roundups/` entry (plus `calendar/monthly/`), and `AURORA.md`.
- Pick one quest step that yields a concrete artifact (code, plot, metric, doc).
- Change as few files as possible to accomplish that step.
- Always log + score after work: update short log, append long log, update quest status, update calendar belief ledger when using external context, and set a new Aurora Score.

## tasks_open
- Maintain the Arcade Loop scaffolding and logs.

# Codex Game Plan
this is the plan to refactor AGENTS.md into the Codex Arcade Game

the idea is a kind of “constraint-magic”: turn Codex into a player, the repo into an arcade cabinet, and progress into a score you can audit.

⸻

SNS-S-S as an “Arcade Loop” (v0.1)

Core loop (what Codex “plays” every session)
	1.	Spawn: read memory/mem_log_short.md + quests/quests_active.md + latest calendar roundup + AURORA.md
	2.	Pick one quest step: smallest move that produces an artifact (code, plot, metric, doc)
	3.	Do it: change as few files as possible, run the spell(s), write outputs
	4.	Log: update short log + append 1–2 lines to long log + update quest status
	5.	Score: compute a new Aurora Score (complex number) and set the next spawn point

This matches your “ants moving a stick” chain: each session hands the stick forward, not sideways.

⸻

Recommended directory + file layout

Keep it boringly predictable:

/AGENTS.md                # “You are playing SNS-S-S”
/AURORA.md                # spawn compass + scoring
/calendar/
  /roundups/
  /monthly/
  belief_ledger.csv
  tag_index.yml
/quests/
  quests_active.md
  quests_completed.md
  quest_template.md
/agents/
  researcher_brief.md
/memory/
  mem_log_short.md
  mem_log_long_0000_0999.md
/plan/
  plan.md
  quests_active.md        # legacy (use /quests instead)
  quests_completed.md     # legacy (use /quests instead)
  quest_template.md       # legacy (use /quests instead)
/rituals/
  rituals.md
  spells.md

Nothing here conflicts with your existing configs/ docs/ experiments/ src/ tests/ layout.  ￼

⸻

Aurora Score (a usable “complex number compass”)

Make it one line that still carries meaning:

A = r ∠ θ (polar complex form)
	•	r ∈ [0, 1] = “how real was the progress?”
	•	0.0 = ideas only
	•	0.3 = spec + acceptance criteria
	•	0.6 = runnable change + logs
	•	0.8 = runnable + test + plot
	•	1.0 = reproducible + compared baseline + documented
	•	θ encodes direction (what kind of work moved forward)
	•	0° = simulation correctness (models, math, validity)
	•	90° = theory expansion (speculative physics scaffolding)
	•	-90° = engineering plumbing (CLI, configs, tests, packaging)
	•	180°/-180° = narrative/docs/public artifact polish

So a session might end as: A = 0.7 ∠ -60° (solid progress, mostly tooling + infra).

If you want the extra “Aurora flavor”, add 4 sub-scores as a tiny vector beneath it:
	•	Evidence, Coherence, Ethics/Safety, Resonance (0–3 each)

⸻

Memory logs that won’t rot

memory/mem_log_short.md (spawn sheet)

Keep it small. Example template:

# mem_log_short (spawn)

Current Quest: QST-0001
Current Step: Implement baseline runner CLI + outputs folder

Last Output Artifact:
- outputs/latest/metrics.json
- outputs/latest/timeseries.csv
- outputs/latest/plot_energy.png

Blockers / Known Bugs:
- (none) or bullet list

Aurora Score (last session): A = 0.5 ∠ -30°

Next Move (one shot):
- Add smoke test that runs 10 steps, asserts outputs exist.

memory/mem_log_long_0000_0999.md (1–2 lines per session)

One line per session is enough:

[S0007 | 2026-02-04] QST-0001 Baseline runner wired; outputs+plot saved. A=0.7∠-60°. Tags: 2.1 swarm, 3.0 power, 0.2 tooling

Dewey-decimal-ish tags (searchable)
Use a tiny taxonomy:
	•	0.x = meta/ops/tooling
	•	1.x = orbital + illumination geometry
	•	2.x = swarm dynamics + control
	•	3.x = power chain + storage + losses
	•	4.x = beaming/comms (future)
	•	5.x = materials/survivability (future)

This lets you grep long logs fast.

⸻

Rituals vs Spells (make the magic practical)

rituals/rituals.md (procedures)

“Rituals” are repeatable checklists like:
	•	Spawn Ritual (what to read)
	•	Run Ritual (how to run an experiment)
	•	Verify Ritual (tests + sanity checks)
	•	Record Ritual (how to log + score)

rituals/spells.md (commands)

“Spells” are single-line invocations Codex can cast, e.g.:

## Spells

- Install: `pip install -e .`
- Tests: `pytest -q`
- Smoke sim: `python -m experiments.baseline --config configs/baseline.yaml --steps 50 --out outputs/latest`
- Analyze: `python -m experiments.analyze --in outputs/latest --out outputs/latest`

(If you later add a Makefile, these become make test, make run, etc.)

⸻

Quests (hypothesis tracking without ML-bloat)

plan/quest_template.md

# QST-XXXX: <Short name>

## Hypothesis
If <change>, then <measurable outcome>.

## Method
- Inputs:
- Procedure:
- Metrics:

## Success Criteria
- Must:
- Nice-to-have:

## Artifacts
- outputs/<run_id>/...
- docs/<...> (if any)

## Risks
- What could fool us?

## Next Step
One concrete action.

quests/quests_active.md

A list of 3–7 active quests max. Everything else goes to backlog or completed.

⸻

The Codex meta-task prompt (to implement your “game interface”)

This is the exact “Codex Task” I’d use first:

Codex Task: “Arcade Layer v0.1” (Docs + minimal scaffolding only)
	•	Create folders: memory/, plan/, rituals/
	•	Add files: AURORA.md, memory/mem_log_short.md, memory/mem_log_long_0000_0999.md, plan/plan.md, plan/quests_active.md, plan/quests_completed.md, plan/quest_template.md, rituals/rituals.md, rituals/spells.md
	•	Update root AGENTS.md to instruct: treat repo as a game, obey spawn ritual, do one-shot progress, always log + score.
	•	Do not touch simulation code yet.
	•	Acceptance criteria:
	1.	All files exist with templates
	2.	AGENTS.md clearly points to spawn files and session loop
	3.	A sample quest exists in quests_active.md (QST-0001: Baseline runner)

Codex will read AGENTS.md before work, so this “control plane” really matters.  ￼

⸻

One safety note (because “AGENTS.md is a control plane”)

If you later let agents run in Codespaces/Actions: treat AGENTS.md + spells like privileged configuration. Keep spells offline and avoid anything that touches secrets by default. There are real “goal hijack” / prompt-injection failure modes when agents auto-load repo instructions.  ￼

⸻

If you want, your very first quest can be:

QST-0001: “Hello Swarm”
Baseline sim runs 50 steps and produces outputs/latest/metrics.json + plot_energy.png.
That gives the arcade cabinet its first flashing “INSERT COIN” attract mode. 🕹️☀️

## Session Log
[2026-02-05 07:10:41Z] Agent: GPT-5.2-Codex | Intent: Implement Arcade Layer v0.1 scaffolding | Plan: create memory/plan/rituals templates, add AURORA.md, update AGENTS instructions, and document quests.
[2026-02-05 22:28:41Z] Agent: GPT-5.2-Codex | Intent: Integrate /calendar loop into the arcade control plane | Plan: scaffold calendar/quests/agents directories, wire spawn ritual + Aurora scoring, and log updates.

## Handoff
### Snapshot (tests/metrics)
- Tests not run (docs-only scaffolding changes).

### Decisions (tradeoffs)
- Added minimal templates to keep the arcade loop lightweight and consistent with requested structure.

### TODO (next steps)
- Run the first quest step when ready (baseline sim outputs and log updates).

### Questions (blocked items)
- `AGENTS_CORE.md` was not found in the repo root; should one be added?

## Handoff
### Snapshot (tests/metrics)
- Tests not run (docs-only scaffolding changes).

### Decisions (tradeoffs)
- Added a calendar loop and belief ledger to externalize weekly context without moving simulation code.

### TODO (next steps)
- Run the next weekly roundup and log belief shifts into the ledger.

### Questions (blocked items)
- Should the legacy `/plan/quests_*` files be retired or kept in sync with `/quests`?
