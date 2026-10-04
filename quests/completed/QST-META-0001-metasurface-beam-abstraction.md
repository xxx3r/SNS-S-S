# QST-META-0001: Metasurface Beam-Steering Abstraction

Status: Completed — 2026-10-04  
Priority: P1  
Tags: [META, BEAM, CONTROL]

## Hypothesis

A compact loss model using steering angle, pointing error, aperture, receiver coupling, and control power can bound when SNS relay behavior is useful.

## Method

Implement a pure-Python abstraction for:

- angular steering penalty
- pointing-error loss
- transmitter / receiver coupling
- control-energy cost
- safe operating envelope

## Success criteria

- Unit-tested loss function.
- Sweep showing net delivered energy versus angle and error.
- Clear boundary between data-link abstraction and power-beam claim.

## Artifacts

- `src/sim/beam_link.py`
- `outputs/qst_meta_0001/beam_link_sweep.json`
- `docs/system/beam_link_assumptions.md`

## Falsifier

If plausible pointing and conversion losses make node-to-node energy transfer consistently wasteful, retain metasurfaces for sensing, communication, or reflection control instead.

## Completion disposition — 2026-10-04

Accepted code and tests implement the declared compact loss function. The immutable 12-point sweep reports net delivered energy across steering-angle and pointing-error inputs, including one negative control-cost case; 4 points meet the declared synthetic useful-fraction boundary and 8 do not. PR #116 accepted the missing assumptions boundary and byte-bound tests, preserving the output and formulas exactly.

The declared bounded success criteria are therefore complete. The quest-level falsifier did not fire across the entire declared grid because four synthetic points remain above its internal useful boundary. This does not establish stochastic pointing behavior, diffraction/range performance, actuation or fabrication feasibility, environmental qualification, a receiver architecture, real power-beam performance, or hardware readiness. Those are distinct successor questions, not reasons to keep this bounded abstraction quest permanently active.
