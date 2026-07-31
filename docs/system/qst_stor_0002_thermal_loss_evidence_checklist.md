# QST-STOR-0002 Thermal-Loss Evidence Checklist

Status: evidence gate, not material qualification  
Updated: 2026-07-21  
Model boundary under review:

- effective system emissivity: `epsilon_eff <= 0.10`
- parasitic conductance: `G_parasitic <= 5e-5 W/K`
- declared case: 10 mm node, 30-minute eclipse, 283.15 K initial temperature, 50% PCM mass fraction, 25% active duty cycle

## Engineering question

Can a physically packaged 10 mm SNS node meet the thermal-loss boundary produced by the current lumped shadow-survival model after surface aging, vacuum, thermal cycling, radiation, contamination, supports, wiring, adhesives, deployment interfaces, and PCM containment are included?

## Success criteria for this evidence slice

This checklist is complete when it:

1. separates material emissivity from **effective system emissivity**;
2. separates bulk material conductivity from **assembled parasitic conductance**;
3. records test temperature, vacuum state, geometry, environment exposure, uncertainty, and beginning/end-of-life condition;
4. rejects nominal room-temperature constants as package-level proof;
5. identifies the minimum measurements needed before a candidate can satisfy either threshold.

## Evidence classification

Use only the following labels.

- **MEASURED:** direct measurement of the relevant specimen or assembly with geometry and environment reported.
- **INFERRED:** calculation from measured material properties and declared geometry; interfaces and degradation may remain unmeasured.
- **HERITAGE:** demonstrated spacecraft use at a materially different scale or packaging regime.
- **PROPOSED:** concept, vendor claim, simulation, or unverified transfer.
- **UNKNOWN:** evidence required but not found.

A candidate does not pass because one isolated coupon reports a favorable value. The threshold is a property of the complete thermal path.

## Primary-source baseline

### Small-spacecraft thermal-control reality

NASA's May 7, 2026 Small Spacecraft Technology State-of-the-Art review states that low thermal mass makes small spacecraft highly reactive to transient environments, extensive MLI may be impractical on CubeSats, and MLI edge effects can degrade performance. It describes relatively low-emissivity coating approaches near `epsilon ~= 0.25`, which is still above the current SNS model target of `0.10`. It also treats contact conductance, mounting, interface materials, PCM, heaters, coatings, tapes, and MLI as separate contributors that must be designed together.

Source: https://www.nasa.gov/smallsat-institute/sst-soa/thermal-control/

**Interpretation:** the current SNS threshold is more demanding than the low-emissivity coating example in NASA's 2026 review. Conventional small-satellite coating practice does not, by itself, close the model boundary.

### Heritage low-emissivity surfaces

NASA's Long Duration Exposure Facility record reports clear chromic anodized aluminum with a design infrared emittance near `0.16`, followed by post-flight optical-property measurements. NASA's coating reference also warns that formulation, thickness, preparation, manufacturing, ultraviolet exposure, and particle radiation affect absorptance and emittance and therefore require measurement for the actual material state.

Sources:

- https://ntrs.nasa.gov/citations/19920015585
- https://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/19840015630.pdf

**Interpretation:** heritage coatings can approach the boundary but do not establish `epsilon_eff <= 0.10` for a curved, penetrated, deployable 10 mm package after environmental margins.

### MLI and shield architectures

ESA describes MLI as an effective-emittance system whose performance depends on layer count, coatings, pressure, temperature, installation, contact, seams, and blanket size. ESA heritage missions use low-emissivity shields and MLI to survive eclipses, but these systems occupy macroscopic area and rely on installation quality.

Sources:

- https://www.esa.int/esapub/bulletin/bullet87/paroli87.htm
- https://sci.esa.int/web/cluster/1985-engineering

**Interpretation:** foil shields or micro-MLI are candidate *architectures*, not simple material substitutions. At 10 mm scale, seams, penetrations, edge shorts, deployment folds, and areal mass may dominate.

### Environmental degradation

NASA's LEO materials guide and thermal-coating studies identify atomic oxygen, ultraviolet radiation, ionizing radiation, contamination, debris, and thermal exposure as mechanisms that alter spacecraft material and surface properties.

Sources:

- https://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/19960000860.pdf
- https://ntrs.nasa.gov/search.jsp?R=19910009835

**Interpretation:** beginning-of-life emissivity is insufficient. Candidate evidence must include a justified end-of-life value or an explicit degradation uncertainty.

## Candidate pathway matrix

| Pathway | Relevant quantity | Current evidence class | What the evidence supports | What remains unproven for SNS |
|---|---:|---|---|---|
| Polished or vacuum-deposited metal surface | low coupon IR emissivity | HERITAGE / INFERRED | A low-emissivity outer surface is physically possible | Curvature, oxidation, contamination, charging, seams, apertures, PV integration, and end-of-life `epsilon_eff` |
| Clear anodized or conversion-coated aluminum | heritage emittance near the target region | MEASURED / HERITAGE | Space-exposed coating properties can be measured before and after flight | Reported heritage value near `0.16` does not meet the current `0.10` target |
| Tailorable-emittance oxide/VDA coating | low absorptivity with reduced emissivity | HERITAGE / PROPOSED | Coating systems can tune thermal balance | NASA's 2026 example near `0.25` does not close the current target; package and aging evidence absent |
| Double-foil shield or micro-MLI | low effective emittance | HERITAGE / PROPOSED | System-level radiative insulation can outperform a single coating | 10 mm seam, edge, penetration, deployment, mass, and manufacturability penalties |
| Variable-emissivity MEMS/electrochromic surface | switchable heat rejection | PROPOSED / HERITAGE | Low-temperature heat loss might be actively reduced | Power, control, area, reliability, radiation, cycle life, and integration at seed scale |
| Low-conductivity supports/washers | reduced structural heat leak | HERITAGE / INFERRED | Mounting geometry and low-k materials can reduce conduction | Complete `G_parasitic` including every support, wire, adhesive, hinge, and feedthrough |
| Role-specialized warm-storage host | removes strict seed boundary | PROPOSED | Network architecture can move storage and thermal mass off the scout | Mission-level transfer, pointing, availability, and failure consequences |

No row currently qualifies as a demonstrated SNS package solution.

## Emissivity evidence gate

A candidate surface or shield may be entered as **MEASURED** only when all fields below are available.

| Required field | Acceptance requirement |
|---|---|
| Quantity | Total hemispherical IR emissivity or explicitly defined effective emittance, not an unspecified spectral reflectance |
| Temperature range | Includes the modeled shadow range, currently approximately 239–283 K |
| Geometry | Curvature, area, seams, apertures, penetrations, and substrate stated |
| Vacuum | Measurement performed in relevant vacuum or transfer uncertainty declared |
| Solar absorptivity | Reported alongside emissivity so low eclipse loss does not create unacceptable sunlit heating |
| Surface state | Thickness, roughness, preparation, oxidation, adhesive, coating stack, and handling stated |
| Environment | Atomic oxygen, UV, particle radiation, contamination, and thermal-cycle basis stated |
| Life state | Beginning-of-life and end-of-life value or conservative degradation margin |
| Uncertainty | Measurement uncertainty and specimen variability reported |
| Package mapping | Demonstrates how coupon data becomes complete-node `epsilon_eff` |

### Emissivity decision rule

- **PASS:** a complete package measurement or validated package model gives `epsilon_eff <= 0.10` after uncertainty and environmental margin.
- **HOLD:** coupon or heritage evidence suggests a route, but package mapping or end-of-life margin is absent.
- **FAIL:** lower confidence bound exceeds `0.10`, or solar absorptivity creates an incompatible illuminated-state temperature.

Current state: **HOLD / MISSING PACKAGE EVIDENCE**.

## Parasitic-conductance evidence gate

The current boundary applies to the sum of every conductive path:

`G_parasitic = sum(k_i * A_i / L_i) + G_contacts + G_wiring + G_adhesives + G_hinges + G_feedthroughs`

A candidate assembly must inventory all paths rather than tune one support in isolation.

| Required path | Required evidence |
|---|---|
| Structural supports | Material, dimensions, temperature-dependent conductivity, quantity, and load case |
| Electrical wiring | Conductor material, gauge, count, length, insulation, and attachment temperatures |
| PV/deployable-film interface | Hinge, trace, tether, laminate, and folded/deployed configurations |
| Battery and PCM containment | Shell contact, encapsulant, phase-boundary contact, and packaging mass |
| Adhesives and interface layers | Bondline area, thickness, cure condition, vacuum compatibility, and conductivity |
| Sensors and feedthroughs | Thermistors, optical/RF paths, antenna traces, and mechanical penetrations |
| Contact conductance | Surface finish, preload, contact area, cycling, and measured or bounded interface value |
| Assembly validation | Vacuum thermal-balance measurement across the declared temperature interval |

### Conductance decision rule

- **PASS:** measured full-assembly heat leak divided by the measured temperature difference remains `<= 5e-5 W/K` after uncertainty and end-of-life margin.
- **HOLD:** a bottom-up calculation closes nominally but one or more interfaces or degradation terms remain inferred.
- **FAIL:** the summed upper-bound conductance exceeds `5e-5 W/K`.

Current state: **UNKNOWN / NO FULL-ASSEMBLY BUDGET**.

## Minimum experiment before promotion

1. Fabricate a geometrically representative 10 mm thermal dummy with the proposed shell, supports, wires, penetrations, and PCM containment.
2. Measure total mass and component mass fractions.
3. Measure beginning-of-life hemispherical emissivity over the relevant temperature range.
4. Run vacuum thermal-balance tests with controlled boundary temperatures to infer full-assembly `G_parasitic`.
5. Repeat after thermal cycling and at least a bounded contamination/UV/radiation exposure protocol appropriate to the intended mission environment.
6. Propagate measurement uncertainty into the shadow-survival sweep.
7. Report both sunlit overheating and eclipse survival. A low-emissivity package that survives eclipse but cannot reject illuminated waste heat is not a valid solution.

## Falsifiers

The 10 mm baseline should be rejected or reframed if any of the following holds:

- no physically packageable surface/shield remains below `epsilon_eff = 0.10` after end-of-life margin;
- wiring, supports, adhesives, and deployment interfaces exceed `G_parasitic = 5e-5 W/K` before payload integration;
- the mass needed for shielding or PCM violates the closed node mass budget;
- low eclipse emissivity causes unacceptable illuminated-state temperature;
- qualification evidence requires a larger geometry than the declared seed.

## Present conclusion

**Fact:** spacecraft thermal surfaces, MLI, interfaces, heaters, and PCM are established engineering tools, and environmental degradation of optical properties is real.

**Inference:** the current SNS thermal boundary is not impossible in abstract radiative terms, but it is substantially more demanding than common small-spacecraft coating examples and must be solved as a complete package problem.

**Unknown:** no reviewed evidence currently demonstrates that a fully penetrated, wired, deployable, environmentally aged 10 mm SNS package can simultaneously meet `epsilon_eff <= 0.10` and `G_parasitic <= 5e-5 W/K` inside the mass budget.

**Speculative design consequence:** the credible path may require a larger seed, deployable insulation, shorter eclipse exposure, role specialization, or host-level thermal support rather than a universal self-contained mote.

## Next measurement

Build a geometry-closed parasitic-conductance budget for one explicit 10 mm package architecture, including supports, wiring, adhesive bonds, PV hinge/traces, and PCM containment. Feed the upper-bound conductance and end-of-life emissivity range back into the coupled shadow-survival model.