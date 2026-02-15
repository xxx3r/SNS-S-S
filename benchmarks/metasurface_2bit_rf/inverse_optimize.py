"""Generate 2-bit phase codebook (4 target states)."""

from __future__ import annotations

import csv
import json
from pathlib import Path

TARGETS = [0.0, 90.0, 180.0, 270.0]


def wrap_phase_err_deg(a: float, b: float) -> float:
    d = (a - b + 180.0) % 360.0 - 180.0
    return abs(d)


def load_dataset(dataset_csv: Path):
    with dataset_csv.open("r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return [
        {
            "r_mm": float(r["r_mm"]),
            "h_mm": float(r["h_mm"]),
            "phase_deg": float(r["phase_deg"]),
            "amp": float(r["amp"]),
        }
        for r in rows
    ]


def optimize_codebook(dataset_csv: Path, out_json: Path) -> Path:
    rows = load_dataset(dataset_csv)
    states = []
    for idx, target in enumerate(TARGETS):
        best = min(rows, key=lambda r: wrap_phase_err_deg(r["phase_deg"], target) + 25.0 * (1.0 - r["amp"]))
        states.append(
            {
                "state": idx,
                "target_phase_deg": target,
                "params": {"r_mm": best["r_mm"], "h_mm": best["h_mm"]},
                "predicted": {"phase_deg": best["phase_deg"], "amp": best["amp"]},
            }
        )

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps({"targets_deg": TARGETS, "states": states}, indent=2), encoding="utf-8")
    return out_json


if __name__ == "__main__":
    root = Path("benchmarks/metasurface_2bit_rf")
    out = optimize_codebook(root / "data/dataset.csv", root / "runs/codebook.json")
    print(f"wrote {out}")
