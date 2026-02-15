"""Generate deterministic metasurface dataset with analytic backend."""

from __future__ import annotations

import csv
from pathlib import Path

from .backend_analytic import AnalyticResonantBackend

DEFAULTS = {
    "seed": 7,
    "f0_hz": 10.0e9,
    "r_mm_min": 0.6,
    "r_mm_max": 1.4,
    "h_mm_min": 1.4,
    "h_mm_max": 2.6,
    "grid_r": 11,
    "grid_h": 11,
}


def linspace(vmin: float, vmax: float, n: int):
    if n <= 1:
        return [float(vmin)]
    step = (vmax - vmin) / float(n - 1)
    return [vmin + i * step for i in range(n)]


def make_dataset(out_csv: Path) -> Path:
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    backend = AnalyticResonantBackend()
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["r_mm", "h_mm", "phase_deg", "amp"])
        writer.writeheader()
        for r in linspace(DEFAULTS["r_mm_min"], DEFAULTS["r_mm_max"], DEFAULTS["grid_r"]):
            for h in linspace(DEFAULTS["h_mm_min"], DEFAULTS["h_mm_max"], DEFAULTS["grid_h"]):
                sim = backend.simulate({"r_mm": r, "h_mm": h}, DEFAULTS["f0_hz"])
                writer.writerow(
                    {
                        "r_mm": f"{r:.6f}",
                        "h_mm": f"{h:.6f}",
                        "phase_deg": f"{sim['phase_deg']:.6f}",
                        "amp": f"{sim['amp']:.6f}",
                    }
                )
    return out_csv


if __name__ == "__main__":
    path = make_dataset(Path("benchmarks/metasurface_2bit_rf/data/dataset.csv"))
    print(f"wrote {path}")
