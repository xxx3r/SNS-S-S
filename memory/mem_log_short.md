# mem_log_short: Summer 2026 Spawn

Current Program: SNS-S-S as formal research instrument

Current Quest: QST-STOR-0002

Current Step: Test whether the leading 15-minute eclipse escape route is compatible with an explicit asteroid-scout or hosted mission shadow geometry.

Last Evidence:

- QST-STOR-0001 retired the 10 Wh seed assumption.
- Summer 2026 architecture adds role-aware nodes, pulse storage, curtailment, asteroid/GEO scenarios, ARCI scaffolding, and roundup-to-quest parsing.
- The explicit 10 mm geometry model yields 0.789 g total mass and 0.741 J/K lumped heat capacity for the declared baseline composition.
- A closed PCM mass budget and package conductance model falsified the packaged 10 mm, 30-minute eclipse baseline: 0/24 thermal passes while all electrical cases passed.
- Conservative package conductance is 1.69575e-4 W/K; ordinary adhesive, wiring, and feedthrough paths dominate the leakage budget.
- A matched 17-case architectural escape comparison changed one lever at a time and preserved the falsified baseline as the control.
- First discrete-grid survivors are: 15 mm seed diameter, 15-minute eclipse duration, or 80 mW host-supplied thermostatic heat.
- GitHub Actions regression tests pin all three thresholds.
- The 15-minute mission-duty route is the smallest conceptual change because it adds neither seed mass nor continuous host thermal service, but orbital/mission availability is unproven.
- The 15 mm route remains conditional on a new geometry-closed package-conductance budget; fixed absolute package leakage is only a screening assumption.
- The host route changes the mote into a hosted instrument during eclipse and requires thermal service far above local milliwatt-class loads.

Blockers / Known Limits:

- Escape thresholds are first points on a coarse grid, not continuous optima.
- Every package path dimension and material property remains a screening assumption pending explicit mechanical design and measured evidence.
- Contact resistance, multidimensional spreading, internal radiation, temperature dependence, tolerance distributions, and environmental degradation remain omitted.
- The package budget addresses eclipse retention only; illuminated-state heat rejection must be checked separately.
- Candidate coatings still lack package-level BOL/EOL emissivity evidence at the required scale and penetrated geometry.
- The asteroid/GEO environment models do not yet prove a 15-minute maximum continuous shadow interval for the intended mission.
- Pointing, receiver coupling, PV degradation, and communication loss remain abstractions.
- ARCI v0.1 is a transparent weighted baseline, not a calibrated industry standard.

Aurora Score: A = 1.0 ∠ -30° | w_ext = 0.0

Next Move (one shot):

- Add a bounded mission-shadow feasibility experiment that asks whether the existing asteroid-scout or hosted geometry can guarantee a maximum continuous eclipse of 15 minutes; retain the 10 mm thermal model as the acceptance boundary.
