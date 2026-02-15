# QST-SWARM-0004: Starling-Informed Swarm Constraints

Status: Active
Updated: 2026-02-15
Tags: [SWARM, CTRL, DOCS]

## Hypothesis
If SNS swarm assumptions explicitly encode Starling-like operational constraints (comms windows, autonomy level, fault handling), then swarm policies and simulation scenarios will better match plausible mission operations.

## Method
- Inputs: `calendar/roundups/2026-02-08.md`, public Starling operations notes, existing SNS swarm assumptions.
- Procedure: Extract constraint categories and translate them into machine-readable and narrative assumptions.
- Metrics: Constraint matrix produced; assumptions mapped to simulation knobs or TODOs.

## Success Criteria
- Must: Defines comm cadence/windows, autonomy escalation levels, and fault response classes.
- Nice-to-have: Provides a scenario table mapping constraints to likely failure modes.

## Artifacts
- docs/swarm_constraints_starling_mapping.md
- configs/swarm_constraints.yaml

## Risks
- Overfitting assumptions to one mission architecture may limit generality.

## Next Step
Draft a constraint matrix with traceability links to simulation parameters.
