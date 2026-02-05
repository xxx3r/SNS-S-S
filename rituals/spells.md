# Spells

- Install: `pip install -e .`
- Tests: `pytest -q`
- Smoke sim: `python -m experiments.baseline --config configs/baseline.yaml --steps 50 --out outputs/latest`
- Analyze: `python -m experiments.analyze --in outputs/latest --out outputs/latest`
