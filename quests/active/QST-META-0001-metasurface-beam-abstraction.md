# QST-META-0001: Metasurface Beam-Steering Abstraction

Status: Active  
Priority: P1  
Tags: [META, BEAM, CONTROL]

## Hypothesis

A compact loss model using steering angle, pointing error, aperture, receiver coupling, and control power can bound when SNS relay behavior is useful.

## Method

Implement a pure-Python abstraction for:

- angular steering penalty
- stochastic pointing error
- transmitter / receiver coupling
- control-energy cost
- safe operating envelope

## Success criteria

- Unit-tested loss function.
- Sweep showing net delivered energy versus angle and error.
- Clear boundary between data-link abstraction and power-beam claim.

## Artifacts

- `src/sim/beam_link.py`
- `outputs/qst_meta_0001/`
- `docs/system/beam_link_assumptions.md`

## Falsifier

If plausible pointing and conversion losses make node-to-node energy transfer consistently wasteful, retain metasurfaces for sensing, communication, or reflection control instead.
