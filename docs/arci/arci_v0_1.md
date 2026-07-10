# ARCI v0.1: Asteroid Resource Confidence Index

## Purpose

ARCI is a transparent research framework for deciding whether an asteroid target deserves additional observation, a precursor mission, or deprioritization.

It is not a single treasure number and it does not claim to determine mineral value from incomplete remote sensing.

## Dimensions

1. `composition`
2. `accessibility`
3. `recoverability`
4. `energy_environment`
5. `surface_operations`
6. `communications`
7. `market_mission_value`

Each dimension contains:

- normalized score in `[0, 1]`
- evidence confidence in `[0, 1]`
- rationale and evidence trail

## v0.1 calculation

```text
score = weighted mean of dimension scores
confidence = weighted mean of dimension confidences
confidence_adjusted_score = score × confidence
```

The uncertainty band widens as confidence falls. This first model is intentionally simple so it can be criticized and replaced.

## Decision gates

- low confidence: collect more data
- moderate adjusted score: targeted follow-up
- high score but weak confidence: reduce uncertainty before commitment
- high adjusted score: precursor mission may be justified

## Evidence ladder

- telescope classification
- radar / thermal / spectral constraints
- spacecraft remote sensing
- local flyby or orbital sensing
- contact / surface measurements
- repeated calibrated observations

An ARCI grade must always state which rung supports it.

## Worked-example policy

Synthetic examples must be labeled synthetic. Real examples must cite source datasets and record missing dimensions explicitly.

## Future work

- Bayesian dimension updates
- correlated uncertainties
- economic scenarios and NPV ranges
- instrument-value calculations
- comparison with conventional single-orbiter surveys
- calibration against known mission targets
