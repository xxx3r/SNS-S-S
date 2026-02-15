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

