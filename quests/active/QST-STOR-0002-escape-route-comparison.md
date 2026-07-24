# QST-STOR-0002 Evidence Slice: Architectural Escape Comparison

Status: Complete with limitations  
Parent quest: `QST-STOR-0002`  
Date: 2026-07-24

## Engineering question

After the packaged 10 mm, 30-minute shadow baseline produced zero thermal survivors, which smallest bounded single-lever change first restores model survival?

The compared routes are:

1. increase seed diameter while scaling mass, sensible capacity, PCM allocation, and battery capacity with volume;
2. shorten eclipse duration while retaining the packaged 10 mm node;
3. move thermostatic heater power to an external host while retaining the packaged 10 mm node and local base-load battery accounting.

## Success criteria

- Preserve the falsified 10 mm/30-minute baseline as a FAIL control.
- Change one declared architectural lever per route.
- Report mass, thermal capacity, radiative and package conductance, electrical margin, and PASS/FAIL in the reproducible output.
- Pin the first discrete-grid survivor for each route in tests.
- Do not promote a route as qualified hardware.

## Result

GitHub Actions regression tests confirm three first surviving screening thresholds:

| Route | First declared PASS | Interpretation |
| --- | ---: | --- |
| Increased seed diameter | 15 mm | A 1.5× diameter increase restores survival on the declared grid when thermal mass, PCM, and battery scale with volume while package conductance is held fixed. |
| Shorter eclipse | 0.25 h | The packaged 10 mm node first survives when the eclipse is reduced from 30 to 15 minutes. |
| Host-assisted thermal | 0.08 W external heater | The packaged 10 mm node first survives when a host supplies 80 mW thermostatic heat and that heater energy is excluded from the node battery ledger. |

The original 10 mm, 30-minute packaged baseline remains FAIL.

## Interpretation

This is a screening comparison, not an architecture selection.

The smallest conceptual change is the mission-duty route: avoid or limit eclipse to 15 minutes on the current discrete grid. It changes no node geometry and requires no continuous host thermal interface. However, mission feasibility depends on orbit and deployment architecture, so this result does not establish that such duty is available.

The 15 mm route is the smallest self-contained hardware change on the declared grid, but its apparent advantage depends on holding the absolute package conductance fixed as the node grows. A geometry-closed 15 mm package budget is required before promotion.

The host-assisted route preserves the 10 mm seed but requires an 80 mW external thermal service, substantially above the node's milliwatt-class local loads. It therefore changes SNS from an autonomous mote into a hosted instrument during eclipse.

## Artifacts

- `configs/qst_stor_0002_escape_routes.json`
- `experiments/architectural_escape_comparison.py`
- `tests/test_architectural_escape_comparison.py`
- `outputs/qst_stor_0002/architectural_escape_thresholds.json`

## Verification

- `python -m pytest -q` passed in GitHub Actions.
- Legacy baseline-artifact and automation-transaction workflows also passed on the implementation head before the evidence-record commits.
- Thresholds are pinned by regression assertions rather than inferred from prose.

## Limitations

- First PASS means first point in the declared coarse grid, not a continuous optimum.
- Diameter scaling omits a redesigned package-conductance budget.
- Host assistance is modeled as external thermostatic heat, not a mechanical/electrical interface design.
- Illuminated-state heat rejection remains outside scope.
- Contact resistance, gradients, exact radiation, degradation, and tolerances remain incomplete.

## Next move

Treat the 15-minute eclipse route as the leading mission-level escape hypothesis and test whether an asteroid-scout or hosted mission architecture can guarantee that shadow bound. In parallel, do not promote 15 mm hardware until a geometry-closed 15 mm package conductance budget is run.
