"""Run declared QST-STOR-0002 thermal shadow-survival cases."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.sim.thermal_storage import ThermalShadowScenario, scenario_with_result  # noqa: E402


def run(config_path: Path, out_dir: Path) -> list[dict[str, float | str]]:
    config = json.loads(config_path.read_text())
    rows: list[dict[str, float | str]] = []
    for case in config["cases"]:
        case = dict(case)
        name = str(case.pop("name"))
        rows.append({"name": name, **scenario_with_result(ThermalShadowScenario(**case))})

    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / "cases.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "case_count": len(rows),
        "pass_count": sum(row["status"] == "PASS" for row in rows),
        "cases": {
            str(row["name"]): {
                "status": row["status"],
                "temperature_status": row["temperature_status"],
                "electrical_status": row["electrical_status"],
                "minimum_temperature_K": row["minimum_temperature_K"],
                "heater_energy_Wh": row["heater_energy_Wh"],
                "electrical_margin_Wh": row["electrical_margin_Wh"],
                "pcm_latent_energy_used_J": row["pcm_latent_energy_used_J"],
            }
            for row in rows
        },
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    rows = run(args.config, args.out)
    print(f"Evaluated {len(rows)} thermal shadow cases")
    for row in rows:
        print(f"{row['name']}: {row['status']}")


if __name__ == "__main__":
    main()
