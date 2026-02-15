"""Validate predicted codebook against analytic backend truth."""

from __future__ import annotations

import json
from pathlib import Path

from .backend_analytic import AnalyticResonantBackend


def wrap_phase_err_deg(a: float, b: float) -> float:
    d = (a - b + 180.0) % 360.0 - 180.0
    return abs(d)


def validate(codebook_json: Path, out_report: Path, f0_hz: float = 10.0e9) -> Path:
    backend = AnalyticResonantBackend()
    codebook = json.loads(codebook_json.read_text(encoding="utf-8"))

    lines = ["# Metasurface 2-bit Validate Report", "", "|state|target|phase_truth|amp_truth|phase_err|", "|---:|---:|---:|---:|---:|"]
    for st in codebook["states"]:
        target = float(st["target_phase_deg"])
        sim = backend.simulate(st["params"], f0_hz)
        err = wrap_phase_err_deg(sim["phase_deg"], target)
        lines.append(
            f"|{st['state']}|{target:.1f}|{sim['phase_deg']:.2f}|{sim['amp']:.3f}|{err:.2f}|"
        )

    out_report.parent.mkdir(parents=True, exist_ok=True)
    out_report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out_report


if __name__ == "__main__":
    root = Path("benchmarks/metasurface_2bit_rf")
    out = validate(root / "runs/codebook.json", root / "runs/validate_report.md")
    print(f"wrote {out}")
