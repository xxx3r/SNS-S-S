# Metasurface 2-bit RF Tile Benchmark

This benchmark is a minimal inverse-design pipeline for one tile with two geometry knobs (`r_mm`, `h_mm`) and one frequency target (`f0=10 GHz`).

## Workflow
- **Dataset**: parameter sweep with analytic backend (`dataset_make.py`) into `data/dataset.csv`.
- **Forward model**: PyTorch MLP when available (`train_forward.py`), with deterministic table fallback when torch is unavailable.
- **Inverse**: pick 4 states near target phases `{0,90,180,270}` (`inverse_optimize.py`).
- **Validation**: resimulate against analytic backend and write markdown report (`validate.py`).
- **Export**: emit per-state JSON and SVG geometry stubs (`export_geometry.py`).

## Feasibility tags
- **SIM NOW**: analytic backend + dataset + optimization + validation all run without EM solvers.
- **BENCH NOW**: exported geometry (`exports/state_*.svg/json`) can be used as quick fabrication handoff placeholders.
- **LATER**: full-wave backend integration (`backend_fullwave_stub.py`) for Meep/openEMS/RCWA calibration.

## Full-wave swap path
1. Implement `FullwaveStubBackend.simulate(params, f0)`.
2. Match return contract: `{phase_deg, amp, meta}`.
3. Re-run workflow and compare analytic vs full-wave errors in `runs/validate_report.md`.
