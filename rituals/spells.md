# Spells

## Install and verify

- Install: `python -m pip install -e .`
- Full tests: `python -m pytest -q`
- Summer architecture tests: `python -m pytest -q tests/test_summer_2026_architecture.py`

## Canonical runs

- Asteroid survey: `python experiments/baseline.py --config configs/summer_2026_asteroid.json --out outputs/summer_2026_asteroid`
- GEO diagnostics: `python experiments/baseline.py --config configs/summer_2026_geo_ring.json --out outputs/summer_2026_geo_ring`
- Storage audit: `python experiments/storage_geometry_audit.py --config configs/storage_geometry_audit.json --out outputs/qst_stor_0001`
- ARCI example: `python experiments/arci_example.py --config configs/arci_synthetic_target.json --out outputs/qst_arci_0001`
- Roundup staging: `python scripts/roundup_to_quests.py calendar/roundups/YYYY-MM-DD.md --out outputs/quest_staging`

## Legacy controls

- Q1 asteroid baseline: `python experiments/baseline.py --config configs/asteroid_baseline.json --steps 50 --out outputs/legacy_q1_baseline`

## Interpretation

A successful command validates the software path and declared assumptions. It does not qualify hardware.
