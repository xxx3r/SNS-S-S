# LEO Perovskite PV Risk Register v0.1

Quest: QST-PV-0007  
Date: 2026-06-09  
Status: Investigation draft

## Scope

This register captures early scale-up risks for using perovskite solar cells (PSCs) in Low Earth Orbit (LEO) SNS power surfaces. It is intentionally gate-oriented: a risk is not “closed” by a promising paper or press release, only by evidence that survives the listed tabletop, subscale in-space, and mission-ready gates.

## Source Notes

- The 2026-02-15 SNS roundup treats LEO perovskite PV as promising but still constrained by stability, radiation, thermal/vacuum cycling, encapsulation, and deployment readiness.
- A 2026 review in *International Journal of Molecular Sciences* emphasizes that terrestrial qualification routes do not adequately cover space PSC reliability, and calls for space-oriented protocols combining vacuum, AM0 illumination, wider thermal ranges, and particle irradiation.
- Ricoh announced an HTV-X1/SDX in-orbit demonstration in October 2025, with approximately two months of exposure and I-V measurements to evaluate generation performance and durability.
- NASA’s ROSA lineage is treated here as a macro-deployable bridge reference, not as proof that PSC films themselves are deployment-ready.

## Risk Register

| ID | Risk | Severity | Likelihood | Why it matters for SNS | Tabletop gate | Subscale in-space gate | Mission-ready gate | Proof artifact |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PV-01 | Proton/electron radiation creates defects, charge traps, and output decay. | High | Medium | SNS nodes may rely on thin, low-mass PV with little shielding margin. | Irradiate coupon stack with mission-relevant proton/electron spectra; report pre/post I-V, EQE, dark current, and annealing behavior. | Expose instrumented coupons in LEO with periodic I-V sweeps and temperature/radiation logs. | Show end-of-life power margin after dose equivalent to mission duration plus design margin. | Radiation test report; dose model; EOL power budget. |
| PV-02 | Thermal cycling causes microcracks, delamination, and interfacial stress. | High | High | LEO eclipse cycles repeatedly stress flexible multilayer stacks. | Cycle full stack across expected hot/cold bounds in vacuum; inspect adhesion, cracks, series resistance, and encapsulant strain. | Fly coupon on a thermally representative plate; log cycles and degradation per orbit. | Demonstrate stable output after mission-equivalent cycles with deployable substrate attached. | Thermal-vacuum cycling report; microscopy; power retention curve. |
| PV-03 | Vacuum and heat drive volatile loss, stoichiometry shifts, ion migration, or electrode reactions. | High | Medium | Perovskite device stacks can fail through chemistry that is masked in ambient tests. | Hold encapsulated and unencapsulated stacks at hot-case vacuum; measure mass loss, gas species, and I-V drift. | Compare witness coupons with different encapsulation/barrier recipes in LEO. | Qualify stack with bounded outgassing, no critical interface reaction, and acceptable drift under combined stress. | TVAC/outgassing report; materials compatibility matrix. |
| PV-04 | AM0 ultraviolet exposure accelerates photochemical degradation. | Medium | High | Space UV differs from terrestrial AM1.5 conditions and can attack absorber, transport layers, and encapsulants. | Run AM0 UV dose testing with continuous maximum-power tracking and spectral response checks. | Correlate UV exposure telemetry with I-V degradation on exposed coupons. | Demonstrate UV-stable stack or protective coating across mission dose plus margin. | AM0 UV exposure report; coating selection memo. |
| PV-05 | Atomic oxygen erodes unprotected surfaces in LEO. | High | Medium | Low-altitude SNS demonstrators may see aggressive atomic oxygen that attacks organics and exposed barriers. | Atomic-oxygen beam test on complete encapsulated stack, edges, interconnects, and coatings. | Fly edge-sealed coupons at a known LEO altitude/inclination; inspect erosion and leakage. | Show AO erosion margin for selected orbit or choose altitude/attitude constraints that avoid the risk. | AO test report; orbit-dependent erosion model. |
| PV-06 | Encapsulation/barrier design trades protection against mass, flexibility, optical loss, and repairability. | High | High | SNS cannot simply add heavy coverglass if the concept depends on low areal density. | Compare barrier recipes for water/oxygen ingress, UV loss, AO resistance, flex fatigue, and areal density. | Fly at least two barrier variants with identical cells to separate cell vs package degradation. | Freeze an encapsulation stack with verified optical transmission, edge seal reliability, and mass budget fit. | Encapsulation trade matrix; selected stack drawing; areal-density budget. |
| PV-07 | Manufacturing variability and scale-up reduce yield, uniformity, and predictability. | Medium | High | Swarm surfaces need many repeatable cells, not isolated hero coupons. | Build statistically meaningful coupon lot; report efficiency distribution, defect density, and process controls. | Fly representative lot samples, not only best cells. | Establish acceptance sampling and derating rules for production lots. | Lot qualification report; SPC/yield dashboard. |
| PV-08 | Flexible deployment, stowage, vibration, and handling damage films or interconnects. | High | Medium | A film that survives radiation may still fail during launch, roll-out, or repeated flexure. | Run stow/deploy cycles, bend-radius testing, launch vibration, and post-test I-V/EL imaging. | Demonstrate deployment on a small space-rated carrier or hosted payload. | Qualify integrated PV blanket, hinges, interconnects, and strain relief at mission scale. | Deployment test report; vibration report; post-deploy power map. |
| PV-09 | Micrometeoroid/orbital debris punctures create localized shorts, cracks, or contamination paths. | Medium | Medium | Large-area thin films increase exposed target area. | Hypervelocity impact or surrogate puncture test with electrical isolation analysis. | Track degradation/local failures on exposed coupons where possible. | Design segmentation and bypass so single damage sites do not cascade. | Damage-tolerance analysis; segment/bypass schematic. |
| PV-10 | Measurement optimism: short demonstrations under-report long-duration, combined-stressor degradation. | High | High | SNS decisions could overfit to two-month or single-factor results. | Define combined-stressor protocol and minimum reporting fields before accepting evidence. | Require public/partner data with time-resolved environment telemetry, not only headline efficiency. | Use model validated by ground + flight data to predict EOL power with uncertainty bands. | Qualification protocol; data schema; validated degradation model. |

## Initial Gate Policy

1. **No mission power budget may use headline beginning-of-life PSC efficiency without an explicit derating factor.** The derating must trace to radiation, thermal-vacuum, UV, AO, deployment, and manufacturing evidence.
2. **Single-factor tests are useful only as diagnostics.** Risk retirement requires combined-stressor testing or a documented reason why stressor coupling is negligible for the selected orbit and stack.
3. **Short in-space demos are pathfinders, not closure.** A two-month exposure can unlock a subscale gate, but mission-ready status requires duration scaling, environment telemetry, and uncertainty-bounded degradation modeling.
4. **Macro deployables are the bridge architecture.** Until PSC films close the package/deployment gates, SNS should treat ROSA-like deployable heritage as the structural reference and PSC as an experimental blanket material.

## Next Investigation Step

Convert this register into a machine-readable CSV/JSON checklist and add a tiny scoring script that computes a PV readiness score from gate status, evidence freshness, and combined-stressor coverage.

## External References

- Akylbayeva et al., “Stability and Degradation of Perovskite Solar Cells in Space Environments: Mechanisms and Protocols,” *International Journal of Molecular Sciences*, 2026. https://www.mdpi.com/1422-0067/27/8/3459
- Ricoh, “Ricoh perovskite solar cells installed on Japan Aerospace Exploration Agency cargo transfer spacecraft HTV-X1,” 2025-10-27. https://www.ricoh.com/release/2025/1027_1
- NASA, “Impact Story: Roll-Out Solar Arrays.” https://www.nasa.gov/directorates/stmd/impact-story-roll-out-solar-arrays/
