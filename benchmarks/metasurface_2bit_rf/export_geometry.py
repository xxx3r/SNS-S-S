"""Export codebook states as JSON and simple SVG geometry views."""

from __future__ import annotations

import json
from pathlib import Path


def _svg_circle(radius_mm: float) -> str:
    r_px = max(4.0, radius_mm * 40.0)
    size = 160
    c = size / 2
    return (
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{size}' height='{size}'>"
        f"<rect x='0' y='0' width='{size}' height='{size}' fill='white' stroke='black'/>"
        f"<circle cx='{c}' cy='{c}' r='{r_px}' fill='none' stroke='blue' stroke-width='2'/>"
        "</svg>"
    )


def export(codebook_json: Path, out_dir: Path) -> Path:
    codebook = json.loads(codebook_json.read_text(encoding="utf-8"))
    out_dir.mkdir(parents=True, exist_ok=True)
    for st in codebook["states"]:
        sid = int(st["state"])
        params = st["params"]
        (out_dir / f"state_{sid:02d}.json").write_text(json.dumps(params, indent=2), encoding="utf-8")
        (out_dir / f"state_{sid:02d}.svg").write_text(_svg_circle(float(params["r_mm"])), encoding="utf-8")
    return out_dir


if __name__ == "__main__":
    root = Path("benchmarks/metasurface_2bit_rf")
    out = export(root / "runs/codebook.json", root / "exports")
    print(f"wrote {out}")
