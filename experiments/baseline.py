"""Run a baseline simulation and write quest output artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.sim.config import SimulationConfig  # noqa: E402
from src.sim.simulation import Simulation  # noqa: E402


def write_timeseries_csv(metrics, output_path: Path) -> None:
    rows = [
        {
            "t": t,
            "E_host": host,
            "E_mean": mean,
            "E_min": min_val,
            "E_max": max_val,
            "dead_agent_count": dead,
        }
        for t, host, mean, min_val, max_val, dead in zip(
            metrics.t_values,
            metrics.E_host_values,
            metrics.E_mean_values,
            metrics.E_min_values,
            metrics.E_max_values,
            metrics.dead_agent_count,
        )
    ]
    with output_path.open("w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=rows[0].keys() if rows else [])
        if rows:
            writer.writeheader()
            writer.writerows(rows)


def _png_chunk(chunk_type: bytes, data: bytes) -> bytes:
    import struct
    import zlib

    return struct.pack(">I", len(data)) + chunk_type + data + struct.pack(">I", zlib.crc32(chunk_type + data) & 0xFFFFFFFF)


def write_plot_png(x_values: list[float], y_values: list[float], output_path: Path) -> None:
    import struct
    import zlib

    width, height = 640, 360
    bg = (255, 255, 255)
    line = (20, 90, 200)

    pixels = [[list(bg) for _ in range(width)] for _ in range(height)]

    if x_values and y_values:
        x_min, x_max = min(x_values), max(x_values)
        y_min, y_max = min(y_values), max(y_values)
        x_span = (x_max - x_min) or 1.0
        y_span = (y_max - y_min) or 1.0

        points = []
        for x, y in zip(x_values, y_values):
            px = int((x - x_min) / x_span * (width - 1))
            py = int((1.0 - (y - y_min) / y_span) * (height - 1))
            points.append((px, py))

        for (x0, y0), (x1, y1) in zip(points, points[1:]):
            dx = abs(x1 - x0)
            dy = -abs(y1 - y0)
            sx = 1 if x0 < x1 else -1
            sy = 1 if y0 < y1 else -1
            err = dx + dy
            x, y = x0, y0
            while True:
                if 0 <= x < width and 0 <= y < height:
                    pixels[y][x] = list(line)
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
        for r, g, b in row:
            raw.extend((r, g, b))

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    idat = zlib.compress(bytes(raw), level=9)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(_png_chunk(b"IHDR", ihdr))
        f.write(_png_chunk(b"IDAT", idat))
        f.write(_png_chunk(b"IEND", b""))


def build_metrics_payload(config: SimulationConfig, metrics) -> dict:
    return {
        "policy": config.policy,
        "config": asdict(config),
        "steps": len(metrics.t_values),
        "final": {
            "E_host": metrics.E_host_values[-1] if metrics.E_host_values else 0.0,
            "E_mean": metrics.E_mean_values[-1] if metrics.E_mean_values else 0.0,
            "E_min": metrics.E_min_values[-1] if metrics.E_min_values else 0.0,
            "E_max": metrics.E_max_values[-1] if metrics.E_max_values else 0.0,
            "dead_agent_count": metrics.dead_agent_count[-1] if metrics.dead_agent_count else 0,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True, help="Path to simulation config JSON file")
    parser.add_argument("--steps", type=int, default=None, help="Override number of simulation steps")
    parser.add_argument("--out", type=Path, required=True, help="Output directory")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = SimulationConfig.from_json(args.config)
    if args.steps is not None:
        config.duration = float(args.steps) * float(config.dt)

    sim = Simulation(config)
    metrics = sim.run()

    args.out.mkdir(parents=True, exist_ok=True)
    metrics_path = args.out / "metrics.json"
    timeseries_path = args.out / "timeseries.csv"
    plot_path = args.out / "plot_energy.png"

    metrics_path.write_text(json.dumps(build_metrics_payload(config, metrics), indent=2))
    write_timeseries_csv(metrics, timeseries_path)
    write_plot_png(metrics.t_values, metrics.E_host_values, plot_path)

    print(f"Wrote {metrics_path}")
    print(f"Wrote {timeseries_path}")
    print(f"Wrote {plot_path}")


if __name__ == "__main__":
    main()
