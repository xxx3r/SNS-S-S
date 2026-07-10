# QST-STOR-0001: SNS seed storage geometry audit

## Status
Completed; PR review fix regenerated the checked-in summary artifact from the runner schema.

## Artifacts
- `src/sim/storage_geometry.py`
- `experiments/storage_geometry_audit.py`
- `configs/storage_geometry_audit.json`
- `outputs/qst_stor_0001/storage_sweep.csv`
- `outputs/qst_stor_0001/summary.json`
- `outputs/qst_stor_0001/active_duty_sensitivity.csv`
- `outputs/qst_stor_0001/report.md`

## Result
- 1,296 configured geometry scenarios evaluated.
- Checked-in `summary.json` now matches the runner's nested `by_core_diameter` schema.

## Next Step
Use the storage envelope as an input to QST-STOR-0006 night-side energy budgeting.
