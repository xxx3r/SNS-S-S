# QST-STOR-0001: SNS Storage Geometry Audit Findings

Date: 2026-07-10  
Status: Geometry audit complete  
Scope: electrical storage geometry only; not flight qualification

## Question

Can a spherical SNS core with diameter 10, 20, or 30 mm contain enough rechargeable storage to survive representative shadow intervals?

The audit replaces the conceptual `0.1–10 Wh` seed range with a volume-derived calculation:

\[
V_{core}=\frac{4}{3}\pi\left(\frac{d}{2}\right)^3
\]

\[
E_{usable}=V_{core}\,f_{battery}\,\rho_E\,f_{usable}
\]

\[
E_{required}=\frac{P_{shadow}\,t_{shadow}(1+r_{reserve})}{\eta_{discharge}}
\]

The baseline shadow load is sleep power plus a 1% duty-averaged active load.

## Declared assumptions

| Assumption | Baseline |
| --- | ---: |
| Usable fraction of gross cell capacity | 80% |
| Discharge efficiency | 90% |
| Charge efficiency | 90% |
| Required reserve | 20% |
| Active duty during shadow | 1% |
| Battery bulk density for mass estimate | 2.0 g/cm³ |
| Conservative available PV charge power | 27 W |
| Maximum battery charge rate | 1C |

Battery mass is a geometry-derived estimate from allocated cell volume and assumed bulk density. It is not a complete storage-subsystem mass budget.

## Baseline sweep result

The six-dimensional Cartesian sweep contains 1,296 scenarios.

| Core | Scenarios | PASS | Pass rate | Usable capacity range |
| --- | ---: | ---: | ---: | ---: |
| 10 mm | 432 | 377 | 87.3% | 0.0138–0.2094 Wh |
| 20 mm | 432 | 431 | 99.8% | 0.1106–1.6755 Wh |
| 30 mm | 432 | 432 | 100.0% | 0.3732–5.6549 Wh |
| **All** | **1,296** | **1,240** | **95.7%** | **0.0138–5.6549 Wh** |

The original 10 Wh upper bound is not reached anywhere in this sweep. Even the largest case, a 30 mm core with 50% battery allocation and 1,000 Wh/L cells, reaches 5.65 Wh usable. The maximum 10 mm case reaches 0.209 Wh usable; at the more representative 30% battery fraction it reaches 0.126 Wh.

## Failure frontier

Of 56 baseline failures:

- 55 occur in 10 mm cores.
- 49 occur at the 72-hour shadow duration.
- 35 include the maximum sleep load and maximum active load.
- The single 20 mm failure is the weakest storage geometry under the harshest load-duration case.
- No 30 mm geometry fails the baseline assumptions.

Worst case:

- 10 mm core
- 15% battery volume
- 220 Wh/L
- 1,000 µW sleep
- 100 mW active at 1% duty
- 72 h shadow
- usable energy: 0.0138 Wh
- required energy: 0.192 Wh
- qualified survival: 5.18 h
- margin: -0.178 Wh

This is the expected shape: failures gather where small volume, low energy density, low battery allocation, high load, and long darkness intersect.

## Duty-cycle attack

The baseline pass rate depends strongly on the assumption that expensive activity is rare during shadow.

| Active duty in shadow | Overall PASS | 10 mm | 20 mm | 30 mm |
| ---: | ---: | ---: | ---: | ---: |
| 0% | 97.7% | 93.1% | 100.0% | 100.0% |
| 1% | 95.7% | 87.3% | 99.8% | 100.0% |
| 5% | 90.8% | 77.8% | 95.4% | 99.3% |
| 10% | 87.5% | 72.5% | 92.4% | 97.7% |
| 100% | 68.2% | 45.1% | 74.3% | 85.2% |

Therefore the correct interpretation is not “storage is mostly solved.” It is:

> A small SNS seed can be a credible survival buffer only when darkness is treated as a low-activity state.

## PV fill time versus battery acceptance

The ideal energy-only PV fill times range from 2.05 s to 837.76 s using a 27 W charging source and 90% charge efficiency. These values expose the generation/storage geometry mismatch, but they are not safe electrochemical charge times.

At the declared 1C charge limit, the time to reach the 80% usable target is 2,880 s, or 48 minutes, for every geometry. The battery acceptance rate, not available sunlight, becomes the charging clock.

Future models should retain both quantities:

- `pv_fill_time_s`: lower bound imposed by available solar power.
- `charge_limited_fill_time_s`: lower bound imposed by cell acceptance.

## Design consequences

1. Retire `0.1–10 Wh` as a generic 10 mm seed range.
2. Use a 10 mm geometry envelope of roughly 0.014–0.209 Wh for the audited volume fractions and energy densities.
3. Treat the 10 mm seed battery as survival storage, not a reservoir for the kite's full harvested flow.
4. Schedule sensing, compute, and transmission primarily in illumination.
5. Add charge-rate, temperature, aging, heater, converter, and radiation derating before interpreting PASS as hardware readiness.
6. Compare specialized scout, relay, and storage-node architectures rather than forcing identical storage into every node.

## Reproduction

```bash
python experiments/storage_geometry_audit.py \
  --config configs/storage_geometry_audit.json \
  --out outputs/qst_stor_0001

pytest -q tests/test_storage_geometry_audit.py
```

## Next measurement

Extend the audit into **QST-STOR-0002: Thermal-Derated Shadow Survival** by adding battery temperature, heater load, phase-change buffering, temperature-dependent usable capacity, and cycle-aging derating.
