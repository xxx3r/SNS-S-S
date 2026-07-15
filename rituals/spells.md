# Spells

## Install and verify

- Install: `python -m pip install -e .`
- Full tests: `python -m pytest -q`
- Transaction tests: `python -m pytest -q tests/test_automation_*.py`
- Repository semantics: `python -m automation.cli validate-repository`
- Generated run log: `python -m automation.cli generate-long-log`
- September audit: `python -m automation.cli audit --cutoff-time 2026-09-01T14:00:00Z --cutoff-commit <main-sha>`

## Canonical scientific runs

- Asteroid survey: `python experiments/baseline.py --config configs/summer_2026_asteroid.json --out outputs/summer_2026_asteroid`
- GEO diagnostics: `python experiments/baseline.py --config configs/summer_2026_geo_ring.json --out outputs/summer_2026_geo_ring`
- Storage audit: `python experiments/storage_geometry_audit.py --config configs/storage_geometry_audit.json --out outputs/qst_stor_0001`
- ARCI example: `python experiments/arci_example.py --config configs/arci_synthetic_target.json --out outputs/qst_arci_0001`
- Roundup staging: `python scripts/roundup_to_quests.py calendar/roundups/YYYY-MM-DD.md --out outputs/quest_staging`

A successful command validates software paths and declared assumptions. It does not qualify hardware.
