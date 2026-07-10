"""Run the QST-STOR-0001 SNS seed-storage geometry audit."""

from __future__ import annotations

import argparse
import csv
import itertools
import json
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.sim.storage_geometry import StorageScenario, evaluate_storage_scenario  # noqa: E402


def load_config(path: Path) -> dict:
    return json.loads(path.read_text())


def run_audit(config: dict) -> list[dict]:
    sweep = config["sweep"]
    rows = []
    keys = list(sweep)
    for values in itertools.product(*(sweep[key] for key in keys)):
        scenario = StorageScenario(**dict(zip(keys, values)))
        rows.append(asdict(evaluate_storage_scenario(scenario, float(config["eclipse_hours"]))))
    return rows


def summarize(rows: list[dict]) -> dict:
    total = len(rows)
    pass_count = sum(row["status"] == "PASS" for row in rows)
    by_core = {}
    for core in sorted({row["core_diameter_mm"] for row in rows}):
        subset = [row for row in rows if row["core_diameter_mm"] == core]
        passed = sum(row["status"] == "PASS" for row in subset)
        by_core[f"{int(core)}_mm"] = {"pass": passed, "fail": len(subset) - passed, "pass_rate": passed / len(subset)}
    return {
        "scenario_count": total,
        "pass_count": pass_count,
        "fail_count": total - pass_count,
        "pass_rate": pass_count / total,
        "by_core_diameter": by_core,
        "best_margin_wh": max(row["margin_wh"] for row in rows),
        "worst_margin_wh": min(row["margin_wh"] for row in rows),
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_sensitivity(path: Path, rows: list[dict]) -> None:
    fields = ["active_duty_cycle", "scenario_count", "pass_count", "fail_count", "pass_rate"]
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for duty in sorted({row["active_duty_cycle"] for row in rows}):
            subset = [row for row in rows if row["active_duty_cycle"] == duty]
            passed = sum(row["status"] == "PASS" for row in subset)
            writer.writerow({"active_duty_cycle": duty, "scenario_count": len(subset), "pass_count": passed, "fail_count": len(subset) - passed, "pass_rate": passed / len(subset)})


def write_report(path: Path, summary: dict) -> None:
    path.write_text("\n".join([
        "# QST-STOR-0001 Storage Geometry Audit",
        "",
        f"Scenarios: {summary['scenario_count']}",
        f"PASS: {summary['pass_count']} / FAIL: {summary['fail_count']}",
        "",
        "The checked-in summary uses the runner's nested `by_core_diameter` schema.",
    ]) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = run_audit(load_config(args.config))
    summary = summarize(rows)
    args.out.mkdir(parents=True, exist_ok=True)
    write_csv(args.out / "storage_sweep.csv", rows)
    (args.out / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    write_sensitivity(args.out / "active_duty_sensitivity.csv", rows)
    write_report(args.out / "report.md", summary)
    print(f"Evaluated {summary['scenario_count']} storage geometries")
    print(f"PASS {summary['pass_count']} / FAIL {summary['fail_count']}")


if __name__ == "__main__":
    main()
