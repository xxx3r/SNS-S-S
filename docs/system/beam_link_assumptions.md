# META beam-link assumptions boundary

## Accepted source; no new sweep

This document interprets the existing QST-META-0001 artifact. It does not
generate another sweep, change a formula, select hardware, or close the quest.
Source: accepted main `2c34d1835223d1c7f44a1fb6f001bf5f6c8d7ec0`.
Artifact: `outputs/qst_meta_0001/beam_link_sweep.json`.
Artifact SHA-256: `ac7f807a3cf7bc0f0882956932de62f04751d17925af829edf3701e82cedbd91`.
Implementation: `src/sim/beam_link.py`; existing tests: `tests/test_beam_link.py`.
Inheritance: PR #114's Weekly route and proposal
`QA-20260731T025500000000Z-refine-qst-meta-0001-ff001122334455667788`.
Their decision effect is to document accepted output rather than repeat it,
while keeping six distinct assumption fields separate.

## Independent physical and engineering fields

| Field | Declared abstraction | Unresolved physical evidence |
| --- | --- | --- |
| Steering physics | Deterministic angular attenuation, `max(cos(theta), 0) ** 2`; degrees are converted to radians for cosine. | No wavelength, diffraction pattern, angular calibration or measured steering envelope. |
| Actuation mechanism | None selected; angle is a model coordinate, not an actuator command. | Mechanism, response time, dynamics and control stability unknown. |
| Fabrication route | None represented or selected. | Materials, process, tolerances, degradation and manufacturability unknown. |
| Update energy | `control_base_Wh = 0.04`; `control_per_degree_Wh = 0.0005`; model subtracts their angle-dependent sum once per point. | No physical update cadence, idle load, actuation energy measurement or conversion to watts. |
| Aperture efficiency | Dimensionless synthetic multiplier `aperture_efficiency = 0.8`. | No aperture size, frequency, range, diffraction, receiver geometry or measured aperture efficiency. |
| Environment compatibility | No environmental model. | Vacuum, radiation, thermal limits, lifetime and space qualification unknown. Aqueous magnetic locomotion is outside the space baseline. |

The proposal's magneto-photonic reference motivates separation of these fields,
not adoption of an aqueous mechanism as a space power-beam baseline. No new
literature claim or physical calibration is introduced by this document.

## Accounting, units and parameter meaning

All parameters are synthetic and uncalibrated. Input energy is `1 Wh`, not
instantaneous power. Transmitter conversion is `0.72`; receiver coupling is
`0.75`. Neither multiplier establishes a particular transmitter or receiver.
For steering angle `theta` and non-negative pointing-error magnitude `e`, both
in degrees, the accepted accounting is:

```text
steering = max(cos(radians(theta)), 0) ** steering_exponent
pointing = exp(-0.5 * (e / pointing_sigma_deg) ** 2)
gross_Wh = input_Wh * aperture * conversion * coupling * steering * pointing
control_Wh = control_base_Wh + control_per_degree_Wh * abs(theta)
net_Wh = gross_Wh - control_Wh
net_fraction = net_Wh / input_Wh
```

The implementation forces steering to zero at exactly 90 degrees before
exponentiation. The accepted grid stops at 60 degrees. Steering exponent is
`2`; pointing sigma is `2 degrees`. The Gaussian-shaped pointing factor is
deterministic attenuation, not a sampled pointing distribution, success
probability, jitter simulation or measured expected-energy calculation.
The quest's stochastic-pointing method remains an unresolved modeling gap.

`minimum_useful_fraction = 0.25` is a declared model boundary, not a hardware
requirement. A point is useful when its unrounded net fraction is at least
that threshold. Artifact values are rounded to 12 decimal places. Negative
net energy is retained rather than clipped, so control-cost failures stay
visible. The 1 Wh fixture makes fraction and Wh values numerically equal;
their units and meanings remain different.

## Accepted result and counterexamples

The unchanged grid has steering angles `[0, 20, 40, 60]` degrees and pointing
errors `[0, 1, 3]` degrees: 12 points, 4 useful and 8 limited. Outcome:
`BOUNDED_BENEFIT_WITH_LOSS_LIMITS`. Useful coordinates are `(0, 0)`, `(0, 1)`,
`(20, 0)` and `(20, 1)`. Maximum net fraction is `0.392`; minimum is
`-0.034937533525`. No new measurements support this documentation slice.

The strongest positive reading—some modeled relay benefit survives the
declared losses—has a direct counterexample: at `(60, 3)` control cost
`0.07 Wh` exceeds gross delivery `0.035062466475 Wh`, producing negative net
energy. Conversely, a claim that relay losses erase benefit everywhere is
contradicted by `(0, 0)`, whose net delivery is `0.392 Wh`, above the declared
0.25 boundary. Four useful synthetic points do not establish physical utility;
eight limited points do not establish universal relay failure.

## Falsifier and nonclaims

The quest falsifier asks whether plausible pointing and conversion losses
make node-to-node energy transfer consistently wasteful; in that case retain
metasurfaces for sensing, communication or reflection control instead. This
uncalibrated grid does not establish physical plausibility or settle that
quest-level decision. Its flag
`relay_losses_erase_modeled_benefit_on_declared_grid` is false only on this grid.
The existing conservative falsifier test is preserved, not rerun as new science.

No physical power-beam performance is established. No metasurface architecture
or receiver technology is selected. No hardware readiness or space qualification
is implied. The abstraction excludes diffraction, range, thermal limits,
materials, dynamics and receiver architecture. A physical safe operating
envelope remains unknown; the grid is only a synthetic accounting boundary.
This slice preserves model/output bytes and leaves SYNTH R2 paused.

