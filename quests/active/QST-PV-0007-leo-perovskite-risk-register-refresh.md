# QST-PV-0007: LEO Perovskite PV Risk Register Refresh

Status: Active
Updated: 2026-06-09
Tags: [PV, MAT, RISK, DOCS]

## Hypothesis
If SNS captures a concise LEO perovskite constraint taxonomy as a risk register, then PV pathway decisions can use explicit gate criteria before scaling from macro deployables to smaller SNS node surfaces.

## Method
- Inputs: `calendar/roundups/2026-02-15.md`, prior SNS PV assumptions, publicly stated LEO PV degradation concerns.
- Procedure: Build a one-page risk register with severity/likelihood/gate fields and map each risk to required proof artifacts.
- Metrics: Register includes at least 8 risks and each risk has a validation gate.

## Success Criteria
- Must: Includes radiation, thermal cycling, vacuum effects, encapsulation, manufacturing variability, and deployment survivability risks.
- Nice-to-have: Includes separate gates for "tabletop", "subscale in-space", and "mission-ready".

## Artifacts
- docs/pv_leo_perovskite_risk_register.md
- data/pv_leo_perovskite_risks.csv
- scripts/score_pv_readiness.py
- outputs/latest/pv_readiness_summary.json

## Risks
- Public information may under-specify private test conditions and overstate readiness.

## Progress
- 2026-06-09: Drafted `docs/pv_leo_perovskite_risk_register.md` with 10 risks, gate criteria, and evidence artifacts.
- 2026-06-09: Added `data/pv_leo_perovskite_risks.csv` and `scripts/score_pv_readiness.py`; current snapshot is 30 gates, 0 mission-ready gates closed, and weighted readiness 0.013.

## Next Step
Update individual gate statuses only when a proof artifact closes or advances a tabletop, subscale in-space, or mission-ready gate.
