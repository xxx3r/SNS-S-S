# QST-STOR-0001 Storage Geometry Audit

- Scenarios: **1296**
- PASS: **1240**
- FAIL: **56**
- Overall pass rate: **95.7%**

## Assumptions

- Usable battery fraction: 80%
- Discharge efficiency: 90%
- Reserve fraction: 20%
- Shadow active duty cycle: 1.0%
- Battery bulk density estimate: 2 g/cm³
- Conservative PV charging source: 27 W
- Maximum battery charge rate: 1C

## Results by core diameter

| Core | Scenarios | PASS | Pass rate | Usable capacity range (Wh) |
| --- | ---: | ---: | ---: | ---: |
| 10 mm | 432 | 377 | 87.3% | 0.013823–0.209440 |
| 20 mm | 432 | 431 | 99.8% | 0.110584–1.675516 |
| 30 mm | 432 | 432 | 100.0% | 0.373221–5.654867 |

## Active-duty-cycle stress test

| Active duty in shadow | Overall pass rate | 10 mm | 20 mm | 30 mm |
| ---: | ---: | ---: | ---: | ---: |
| 0.0% | 97.7% | 93.1% | 100.0% | 100.0% |
| 1.0% | 95.7% | 87.3% | 99.8% | 100.0% |
| 5.0% | 90.8% | 77.8% | 95.4% | 99.3% |
| 10.0% | 87.5% | 72.5% | 92.4% | 97.7% |
| 100.0% | 68.2% | 45.1% | 74.3% | 85.2% |

## Interpretation

`pv_fill_time_s` is an ideal energy-only lower bound. It deliberately shows the geometry mismatch, but it is not a safe battery charging schedule. `charge_limited_fill_time_s` applies the configured C-rate and is the more realistic minimum charging time.

PASS means the usable battery can cover the selected shadow duration after discharge losses and the reserve policy. Thermal, radiation, aging, wiring, and converter derating are not yet included, so PASS is a geometry gate rather than flight qualification.

Regenerate the full 1,296-row CSV with:

```bash
python experiments/storage_geometry_audit.py \
  --config configs/storage_geometry_audit.json \
  --out outputs/qst_stor_0001
```
