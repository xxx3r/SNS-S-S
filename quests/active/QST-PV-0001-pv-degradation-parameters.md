# QST-PV-0001: PV Degradation Parameter Sheet

Status: Active  
Priority: P1  
Tags: [PV, MATERIALS, THERMAL, RADIATION]

## Hypothesis

A small, source-traceable degradation model is more useful than a fixed PV efficiency constant for Summer 2026 simulations.

## Method

Extract ranges for:

- radiation dose response
- thermal-cycle degradation
- temperature coefficient
- partial recovery or annealing
- micrometeoroid / damage placeholder

## Success criteria

- Every parameter has units, range, environment, duration, and source.
- Simulation can switch between constant and degrading PV.
- No single paper is treated as flight qualification.

## Artifacts

- `data/pv_degradation_parameters.csv`
- `src/sim/pv_degradation.py`
- `docs/system/pv_degradation_assumptions.md`

## Falsifier

If literature values cannot be translated across test conditions without misleading precision, retain scenario bands rather than one canonical coefficient.
