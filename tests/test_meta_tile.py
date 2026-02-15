from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from benchmarks.metasurface_2bit_rf.backend_analytic import AnalyticResonantBackend  # noqa: E402
from benchmarks.metasurface_2bit_rf.dataset_make import make_dataset  # noqa: E402
from benchmarks.metasurface_2bit_rf.inverse_optimize import optimize_codebook  # noqa: E402
from benchmarks.metasurface_2bit_rf.train_forward import train  # noqa: E402


def test_backend_returns_phase_amp():
    sim = AnalyticResonantBackend().simulate({"r_mm": 1.0, "h_mm": 2.0}, 10.0e9)
    assert 0.0 <= sim["phase_deg"] <= 360.0
    assert 0.0 <= sim["amp"] <= 1.0
    assert "meta" in sim


def test_dataset_make_creates_file(tmp_path):
    out = tmp_path / "dataset.csv"
    make_dataset(out)
    assert out.exists()
    lines = out.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) > 10


def test_train_forward_saves_model(tmp_path):
    ds = tmp_path / "dataset.csv"
    make_dataset(ds)
    model = tmp_path / "forward_mlp.pt"
    metrics = tmp_path / "train_metrics.json"
    train(ds, model, metrics)
    assert model.exists()
    m = json.loads(metrics.read_text(encoding="utf-8"))
    assert "backend" in m


def test_inverse_produces_4_states(tmp_path):
    ds = tmp_path / "dataset.csv"
    make_dataset(ds)
    out = tmp_path / "codebook.json"
    optimize_codebook(ds, out)
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert len(payload["states"]) == 4
