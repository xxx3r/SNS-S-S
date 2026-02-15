"""Train forward surrogate (PyTorch MLP when available)."""

from __future__ import annotations

import csv
import json
import random
from pathlib import Path


def _load_rows(dataset_csv: Path):
    with dataset_csv.open("r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _train_torch(rows, model_path: Path, metrics_path: Path) -> None:
    import torch
    import torch.nn as nn

    torch.manual_seed(7)
    random.seed(7)

    xs = [[float(r["r_mm"]), float(r["h_mm"])] for r in rows]
    ys = [[float(r["phase_deg"]) / 360.0, float(r["amp"])] for r in rows]
    x = torch.tensor(xs, dtype=torch.float32)
    y = torch.tensor(ys, dtype=torch.float32)

    model = nn.Sequential(nn.Linear(2, 24), nn.Tanh(), nn.Linear(24, 24), nn.Tanh(), nn.Linear(24, 2))
    opt = torch.optim.Adam(model.parameters(), lr=0.01)

    for _ in range(250):
        pred = model(x)
        loss = ((pred - y) ** 2).mean()
        opt.zero_grad()
        loss.backward()
        opt.step()

    model_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), model_path)

    pred = model(x).detach()
    mse = float(((pred - y) ** 2).mean().item())
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(json.dumps({"backend": "torch_mlp", "mse": mse, "n": len(rows)}, indent=2), encoding="utf-8")


def _train_fallback(rows, model_path: Path, metrics_path: Path) -> None:
    # Deterministic nearest-neighbor lookup fallback for environments without torch.
    payload = {
        "backend": "table_lookup",
        "rows": [
            {
                "r_mm": float(r["r_mm"]),
                "h_mm": float(r["h_mm"]),
                "phase_deg": float(r["phase_deg"]),
                "amp": float(r["amp"]),
            }
            for r in rows
        ],
    }
    model_path.parent.mkdir(parents=True, exist_ok=True)
    model_path.write_text(json.dumps(payload), encoding="utf-8")
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(json.dumps({"backend": "table_lookup", "mse": 0.0, "n": len(rows)}, indent=2), encoding="utf-8")


def train(dataset_csv: Path, model_path: Path, metrics_path: Path) -> None:
    rows = _load_rows(dataset_csv)
    try:
        _train_torch(rows, model_path, metrics_path)
    except Exception:
        _train_fallback(rows, model_path, metrics_path)


if __name__ == "__main__":
    root = Path("benchmarks/metasurface_2bit_rf")
    train(
        dataset_csv=root / "data/dataset.csv",
        model_path=root / "models/forward_mlp.pt",
        metrics_path=root / "runs/train_metrics.json",
    )
    print("trained forward model")
