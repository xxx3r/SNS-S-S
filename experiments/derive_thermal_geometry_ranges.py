from __future__ import annotations
import argparse, csv, json
from pathlib import Path
from src.sim.thermal_geometry import ThermalGeometryCase, case_with_result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    config = json.loads(Path(args.config).read_text())
    records = [case_with_result(ThermalGeometryCase(**case)) for case in config["cases"]]
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    with (out / "thermal_geometry_ranges.csv").open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)
    summary = {
        "case_count": len(records),
        "thermal_capacity_J_K": {
            "min": min(r["thermal_capacity_J_K"] for r in records),
            "max": max(r["thermal_capacity_J_K"] for r in records),
        },
        "total_conductance_W_K": {
            "min": min(r["total_conductance_W_K"] for r in records),
            "max": max(r["total_conductance_W_K"] for r in records),
        },
        "placeholder_comparison": {
            "prior_thermal_capacity_J_K": 50.0,
            "prior_thermal_conductance_W_K": 0.005,
        },
    }
    (out / "thermal_geometry_summary.json").write_text(json.dumps(summary, indent=2) + "\n")


if __name__ == "__main__":
    main()
