# QST-STOR-0002 Evidence Slice: Mission-Shadow Feasibility

Status: Implementation complete; CI verification pending  
Parent quest: `QST-STOR-0002`  
Date: 2026-07-25

## Engineering question

Can a bounded asteroid-scout or hosted mission geometry guarantee the 15-minute maximum continuous shadow interval that first restored survival for the packaged 10 mm thermal model?

## Hypothesis

A generic passive circular asteroid orbit will not meet the 15-minute bound. The bound can be met only by selecting a sufficiently fast rotating surface target or by imposing an actively maintained sunward hosted geometry.

## Success criteria

- Preserve `0.25 h / 15 min` as the inherited QST-STOR-0002 thermal acceptance limit.
- Model at least surface-fixed, passive circular-orbit, and actively hosted sunward geometries.
- Keep units and guarantee class explicit.
- Reject passive mission cases that exceed the bound rather than averaging their shadow exposure away.
- Pin the boundary and architecture conclusions in regression tests.
- Do not present a screening geometry as trajectory design or flight qualification.

## Implementation

Added:

- `src/sim/mission_shadow.py`
- `configs/qst_stor_0002_mission_shadow.json`
- `experiments/mission_shadow_feasibility.py`
- `tests/test_mission_shadow_feasibility.py`

The surface model uses half the declared rotation period as the maximum equatorial night interval. The passive orbit model uses a uniform-density spherical asteroid and a central-umbra circular-orbit crossing. The hosted model records zero geometric occultation only while an active sunward half-space constraint is maintained.

## Declared screening result

- Surface-fixed geometry meets the bound only for rotation periods at or below 30 minutes on the declared grid. This is target-selection evidence, not a generic asteroid guarantee.
- None of the five declared passive circular-orbit cases meets the 15-minute bound, including the high-density near-surface case.
- Active sunward hosted standoff conditionally excludes occultation, but the PASS depends on navigation, propulsion, fault tolerance, and host service remaining available.

Therefore the earlier `15-minute eclipse` escape route is **not available as a generic passive asteroid-scout orbit**. It survives only as:

1. an explicit fast-rotator target-selection constraint, or
2. an active hosted/station-kept mission architecture.

## Fact / inference / unknown

### Model facts

- A spherical surface-fixed equatorial node is dark for half a rotation.
- In the declared uniform-density circular-orbit screen, central eclipse duration remains above 15 minutes for every tested density and orbital-radius ratio.
- Maintaining a sunward host constraint removes geometric occultation by construction.

### Inference

- Mission architecture, not additional PCM tuning, is now the leading lever for preserving the 10 mm envelope.
- A passive free-orbiting scout should not inherit the 15-minute thermal PASS without target- and trajectory-specific proof.

### Unknown

- Irregular-body shape, terrain, latitude, tumbling, seasonal Sun geometry, penumbra, perturbations, deployment dispersion, and station-keeping failure probability.
- Propulsion, navigation, and power cost of maintaining the hosted sunward condition.
- Whether illuminated-state heat rejection remains compatible with the same host geometry.

## Verification

Focused tests are committed. Full repository pytest and GitHub Actions are required before this slice is considered verified.

## Belief impact

Confidence decreases that the 15-minute route is a low-cost generic mission-duty change. It is instead a target-selection or actively hosted architecture constraint. Confidence increases that the storage/thermal falsifier is now connected to an explicit mission-geometry decision.

## Next move

Compare the two remaining 10 mm-compatible paths on one matched mission ledger:

1. fast-rotator surface deployment with a measured rotation-period requirement, and
2. active sunward hosted operation with station-keeping and host-service energy explicitly charged.

Report which path preserves `min_materials` after propulsion, host, and operational dependencies are counted.
