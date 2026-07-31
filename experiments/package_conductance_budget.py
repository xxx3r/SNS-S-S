"""Evaluate an explicit SNS package parasitic-conductance budget."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.sim.package_conductance import (  # noqa: E402
    budget_from_dict,
    evaluate_package_budget,
    summarize_categories,
)


def run_package_conductance_budget(config_path: Path, output_dir: Path) -> dict:
    """Evaluate a JSON package budget and write inspectable artifacts."""
    data = json.loads(config_path.read_text(encoding="utf-8"))
    result = evaluate_package_budget(budget_from_dict(data))
    result["category_totals_W_K"] = summarize_categories(result["paths"])
    result["limitations"] = list(data.get("limitations", []))

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "package_conductance_summary.json").write_text(
        json.dumps(result, indent=2) + "\n",
        encoding="utf-8",
    )

    rows = result["paths"]
    with (output_dir / "package_conductance_paths.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs" / "qst_stor_0002_package_conductance.json",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "outputs" / "qst_stor_0002" / "package_conductance",
    )
    args = parser.parse_args()
    result = run_package_conductance_budget(args.config, args.out)
    print(
        f"{result['status']}: conservative G={result['conservative_total_conductance_W_K']:.6g} W/K; "
        f"target={result['target_parasitic_conductance_W_K']:.6g} W/K; "
        f"dominant={result['dominant_path']}"
    )


if __name__ == "__main__":
    main()
