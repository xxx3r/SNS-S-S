# Spells

- Install: `pip install -e .`
- Tests: `pytest -q`
- Smoke test (QST-0001): `pytest -q tests/test_simulation_smoke.py`
- Smoke sim: `python -m experiments.baseline --config configs/baseline.yaml --steps 50 --out outputs/latest`
- Analyze: `python -m experiments.analyze --in outputs/latest --out outputs/latest`
