# QST-META-0005: DL Metasurface Design Pipeline (Bench-Feasible 2026) 

Status: Completed
Updated: 2026-02-15
Tags: [META, CTRL, MFG, RESEARCH]

## Hypothesis
If we curate a targeted reading list and pipeline map for DL-assisted metasurface design, then we can distinguish simulation-first tasks that are bench-feasible in 2026 from speculative hardware leaps.

## Method
- Inputs: `calendar/roundups/2026-02-08.md`, recent metasurface inverse-design literature, SNS constraints.
- Procedure: Build reading list + pipeline diagram (data, model, validation, fabrication handoff) with feasibility labels.
- Metrics: Reading list delivered; each pipeline stage tagged as "sim now", "bench now", or "later".

## Success Criteria
- Must: At least 8 curated references and a clear feasibility rubric for 2026.
- Nice-to-have: Includes a small benchmark task with public datasets/tools.

## Artifacts
- docs/metasurface_dl_pipeline_2026.md

## Risks
- Literature recency bias may underweight practical fabrication bottlenecks.

## Next Step
Assemble an initial 8-paper list and assign feasibility tags.



## QST-META-0005a: Metasurface DL Benchmark (2-bit Beam-Steering Tile)
Status: Active
Created: 2026-02-14
Tags: [META, CTRL, SIM, BENCH]

Goal:
Implement a small, reproducible inverse-design benchmark that runs locally and produces:
(1) a dataset (geometry -> phase/amp),
(2) a forward surrogate model,
(3) an inverse design loop that hits 4 target phases (2-bit),
(4) a validation report + exportable geometry files for bench handoff.

Primary constraint:
Must run “SIM NOW” with an analytic backend by default, and optionally support a full-wave backend later (Meep/openEMS/RCWA).

Artifacts:
- benchmarks/metasurface_2bit_rf/README.md
- benchmarks/metasurface_2bit_rf/config.yaml
- benchmarks/metasurface_2bit_rf/*.py
- docs/benchmarks/metasurface_2bit_rf_tile.md
- tests/test_meta_tile.py



---------------
Requirements:
1) Provide a backend interface simulate(params,f0)-> {phase_deg, amp, meta}.
2) Implement backend_analytic.py with a resonant-response phase model so the benchmark runs without external EM tools.
3) Add dataset_make.py, train_forward.py (PyTorch MLP), inverse_optimize.py (produce 4 target phases), validate.py, export_geometry.py.
4) Add docs/benchmarks/metasurface_2bit_rf_tile.md describing workflow + feasibility tags.
5) Add tests/test_meta_tile.py and ensure pytest -q passes.

Nice-to-have:
- backend_fullwave_stub.py with clean TODO hooks for meep/openEMS/RCWA.
- runs/* artifacts (metrics json, codebook json, validate report).

Keep code deterministic, small, and runnable from repo root via python -m.



—————
### QST-META-0005 is done as written.
	•	Must-have met: you delivered the artifact docs/metasurface_dl_pipeline_2026.md (8+ refs + pipeline + feasibility rubric).
	•	The “benchmark task” was a nice-to-have, so the quest can be closed cleanly now.

What we’re proposing next is best treated as a sub-quest: QST-META-0005a, so 0005 stays “completed” and 0005a is the implementation sprint that earns the extra badge. 🧩

⸻

QST-META-0005a implementation checklist (Codex-ready)

Scope choice (keeps it bench-feasible)
	•	Unit cell: one “tile” with 1–2 geometry knobs (ex: dielectric post radius + height, or slot width + length).
	•	Output target: reflection (or transmission) phase at a single frequency f0, plus amplitude.
	•	2-bit codebook: choose 4 geometries approximating phase {0, 90, 180, 270} degrees (or {0, 120, 240, 360} if you want easier spacing).

Folder + files to create

benchmarks/metasurface_2bit_rf/
  README.md
  config.yaml
  __init__.py
  backend_base.py
  backend_analytic.py
  backend_fullwave_stub.py
  dataset_make.py
  train_forward.py
  inverse_optimize.py
  validate.py
  export_geometry.py
docs/benchmarks/metasurface_2bit_rf_tile.md
tests/test_meta_tile.py

Backend contract (key to “plugging into your scaffold”)

backend_base.py
	•	simulate(params: dict, f0: float) -> dict returning:
	•	phase_deg: float
	•	amp: float
	•	meta: dict (optional diagnostics)

backend_analytic.py
	•	Implement a simple physically-plausible surrogate of a resonant scatterer:
	•	map params to an effective resonance f_r(params) and quality Q(params)
	•	phase from an arctan-like response around f0
	•	This makes the whole benchmark runnable with no heavy EM dependencies.

backend_fullwave_stub.py
	•	Provide a stub interface with clear TODO hooks:
	•	meep or openEMS later
	•	For now it raises a friendly error unless enabled.

Dataset generation

dataset_make.py
	•	Create param sweep over 2 knobs (example):
	•	r ∈ [r_min, r_max], h ∈ [h_min, h_max]
	•	Save:
	•	data/dataset.csv (or parquet)
	•	columns: r, h, phase_deg, amp
	•	Include seed + deterministic ordering.

Forward model training (minimal, reproducible)

train_forward.py
	•	Train a small MLP (PyTorch) to predict (phase_deg, amp) from (r, h)
	•	Save:
	•	models/forward_mlp.pt
	•	runs/train_metrics.json
	•	Add a tiny plot (optional) to runs/phase_fit.png

Inverse design loop

inverse_optimize.py
	•	For each target phase in {0, 90, 180, 270}:
	•	optimize params using gradient on the surrogate MLP (or simple search if you want to avoid autograd edge cases)
	•	loss = wrapped_phase_error + λ*(amp_penalty)
	•	Output:
	•	runs/codebook.json with 4 param sets + predicted response

Validation

validate.py
	•	Re-simulate the found codebook using the analytic backend (ground truth for now)
	•	Report:
	•	phase error per state
	•	amplitude per state
	•	Write runs/validate_report.md

Geometry export (bench handoff)

export_geometry.py
	•	Export each of the 4 states as:
	•	exports/state_00.json (params)
	•	plus a simple CAD-friendly format:
	•	exports/state_00.svg (good enough for many fab handoffs)
	•	optionally DXF if you already have a helper

Tests (so Codex can “close the loop”)

tests/test_meta_tile.py
	•	test_backend_returns_phase_amp()
	•	test_dataset_make_creates_file()
	•	test_train_forward_saves_model()
	•	test_inverse_produces_4_states()

Acceptance criteria for 0005a (close condition)
	•	pytest -q passes
	•	python -m benchmarks.metasurface_2bit_rf.dataset_make produces dataset
	•	training script runs and saves model
	•	inverse script outputs 4-state codebook
	•	docs/benchmarks/metasurface_2bit_rf_tile.md explains:
	•	what the benchmark is
	•	what “SIM NOW vs BENCH NOW vs LATER” means here
	•	how to swap in a full-wave backend later

⸻
