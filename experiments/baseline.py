"""Run a mission-aware SNS baseline and write reproducible artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.sim.config import SimulationConfig  # noqa: E402
from src.sim.simulation import Simulation  # noqa: E402


def write_timeseries_csv(metrics, output_path: Path) -> None:
    """Write flat mission metrics to CSV."""
    rows = metrics.to_rows()
    with output_path.open("w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(rows[0]) if rows else [])
        if rows:
            writer.writeheader()
            writer.writerows(rows)


def _png_chunk(chunk_type: bytes, data: bytes) -> bytes:
    import struct
    import zlib
    return struct.pack(">I", len(data)) + chunk_type + data + struct.pack(">I", zlib.crc32(chunk_type + data) & 0xFFFFFFFF)


def write_plot_png(x_values: list[float], y_values: list[float], output_path: Path) -> None:
    """Write a dependency-free line plot for CI and legacy artifact checks."""
    import struct
    import zlib
    width, height = 640, 360
    pixels = [[[255, 255, 255] for _ in range(width)] for _ in range(height)]
    if x_values and y_values:
        x_min, x_max = min(x_values), max(x_values)
        y_min, y_max = min(y_values), max(y_values)
        x_span, y_span = (x_max - x_min) or 1.0, (y_max - y_min) or 1.0
        points = [
            (int((x - x_min) / x_span * (width - 1)), int((1 - (y - y_min) / y_span) * (height - 1)))
            for x, y in zip(x_values, y_values)
        ]
        for (x0, y0), (x1, y1) in zip(points, points[1:]):
            dx, dy = abs(x1 - x0), -abs(y1 - y0)
            sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
            err, x, y = dx + dy, x0, y0
            while True:
                if 0 <= x < width and 0 <= y < height:
                    pixels[y][x] = [20, 90, 200]
                if x == x1 and y == y1:
                    break
                e2 = 2 * err
                if e2 >= dy:
                    err += dy
                    x += sx
                if e2 <= dx:
                    err += dx
                    y += sy
    raw = bytearray()
    for row in pixels:
        raw.append(0)
        for rgb in row:
            raw.extend(rgb)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as handle:
        handle.write(b"\x89PNG\r\n\x1a\n")
        handle.write(_png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)))
        handle.write(_png_chunk(b"IDAT", zlib.compress(bytes(raw), level=9)))
        handle.write(_png_chunk(b"IEND", b""))


def build_metrics_payload(config: SimulationConfig, metrics) -> dict:
    """Build a versioned result envelope."""
    return {
        "schema_version": "summer-2026-v1",
        "scenario": config.scenario,
        "mission": config.mission,
        "policy": config.policy,
        "config": config.to_dict(),
        "final": metrics.summary(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--steps", type=int, default=None)
    parser.add_argument("--out", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = SimulationConfig.from_json(args.config)
    if args.steps is not None:
        config.duration = float(args.steps) * config.dt
    metrics = Simulation(config).run()
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "metrics.json").write_text(json.dumps(build_metrics_payload(config, metrics), indent=2))
    write_timeseries_csv(metrics, args.out / "timeseries.csv")
    write_plot_png(metrics.t_values, metrics.E_host_values, args.out / "plot_energy.png")
    print(json.dumps(metrics.summary(), indent=2))


if __name__ == "__main__":
    main()
