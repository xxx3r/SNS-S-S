# SNS-TECH-3DI-001 | Heterogeneous 3D electronics, 2026 evidence / 2035 horizon

**Status:** prospective technology watch and falsifiable engineering hypothesis. **No accepted SNS subsystem, material, mass reduction, power reduction, flight heritage, or development commitment.**

## External signal

A 2026 IEEE ECTC paper, Trickett and colleagues, *First Demonstration of 450nm Pitch Cu-Cu Hybrid Bonding with 98% Yield Across 20M Interconnects for Ultra-Dense 3D Integration* (DOI `10.1109/ECTC51846.2026.00130`), reports submicrometer Cu–Cu hybrid-bond test structures. The **450 nm** number is interconnect **pitch**: center-to-center spacing, not whole die thickness or future seed dimensions. The **98% yield** refers to the reported test structures; do not interpret it as 2% of 20 million individual links failing. Full source/test-method review and SNS-relevant qualification are still required.

In an October 22, 2026 Intel fab-tour interview (Dwarkesh Patel with Intel advanced-packaging staff, https://www.dwarkesh.com/p/intel-tour), a speaker discusses potentially connecting lower silicon routing layers more directly, reducing some upper interconnect requirements and interface energy per transferred bit. These are **future architectural possibilities**, not results demonstrated for an SNS or guaranteed by the 450 nm experiment.

## Hypothesis and counter-hypotheses

**H-3DI:** At equivalent useful scientific output and environmental requirements, an actually specified heterogeneous 3D electronic subsystem could reduce installed mass/volume, electrical energy per operation/bit, or the heat burden of an SNS sensor/scout compared with a qualified conventionally packaged baseline.

Counter-hypotheses must remain live:
- Low-duty-cycle SNS control may be dominated by sensor, heater, radio and power-regulator demand rather than inter-die communication. Integration may save essentially nothing.
- The finest-pitch technology could add stack thickness, cost, leakage, test burden, heat concentration or poor yield; volume/thermal effects can be negative.
- Copper interface conductivity may help heat rejection in sunlight and unintentionally increase heat loss or heat sharing in eclipse.
- Radiation, launch vibration, vacuum cycling, chip reliability, thermal stress, low-volume economics and fabrication access remain unqualified.

## Accounting model

For a defined signal interface, `P_interface = (joules / transferred bit) × (transferred bits / second)`.

This **does not** equal total spacecraft power, nor does an illustrative picojoule/bit saving establish a meaningful system reduction without an SNS workload trace. Account separately for:
- MCU compute, memory/data movement, sleep and wake overhead
- sensing and clocks, nonvolatile retention, controller leakage
- power conversion and external inductors/passives (hybrid bonding does not remove all analog or magnetics)
- communication, pointing and optical/radio transmission
- battery charging/discharging/protection and thermal survival heater
- solar collection, curtailment and electrical loss heat deposited at named thermal nodes
- structural interfaces, substrate/interposer, heat spreading, die yield and assembly

A *lower* digital power draw also removes self-heating that can aid survival in eclipse; evaluate sun–shadow–sun, not just sunlit efficiency.

## Two-track source classification

| 2026 physical witness | 2035 technology requirement, not prediction |
|---|---|
| Industrial and lab-scale hybrid bonding for some semiconductor interfaces. | A source-backed actual stack and external connection scheme meeting SNS signal, computation and power needs. |
| Reported 450 nm bond-pitch experiment. | Comparable total installed electronics mass and bounding geometry including package, routing, passives, heat paths, and protective structure. |
| Qualitative opportunities for lower inter-die transfer power. | Measured interface energy and **total mission** energy under a specified workload with uncertainty and environmental margins. |
| Current high-performance packaging supply chain. | Qualification/reliability evidence, acceptable cost/yield and suitable fabrication path for a low-cost spacecraft swarm. |

## Minimum future discriminating study

Design one concrete representative information workload and one physical 2026 baseline assembly. Specify a hypothetical 2035 stack as **parameter bounds**, not a magical single package. Compute break-even improvements in `mW`, `mWh per eclipse`, `mm³`, mass, and degree of extra thermal coupling. Use pessimistic and optimistic bounds, explicitly label unavailable material properties.

A useful outcome is an enabling-technology requirements table **or a null result**: e.g., interconnect energy does not dominate the node's budget. No source here establishes the future architecture's success.

## Relation to accepted work and authority

This is a research intake for later source review, relevant to independently investigated PTM/REF physical-packing blockers and Issue #131. It does **not** imply any change to the current autonomous SIM3 replay route, STOR thermal reference, KiteSeed dimension, approved battery, or an architecture selected for October. See `2026-10-25_physical_reference_intake.md` and `research_handoff_gates.md`. Original independent research ZIP/PDFs remain outside the public repository.
