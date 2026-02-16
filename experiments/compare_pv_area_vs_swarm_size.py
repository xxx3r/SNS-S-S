"""Compare fixed-total-PV variants: few-large vs many-small swarm configurations."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.sim.config import SimulationConfig  # noqa: E402
from src.sim.simulation import Simulation  # noqa: E402


def _load_config(path: Path) -> dict:
    return json.loads(path.read_text())


def _run_single(config_path: Path) -> dict:
    data = _load_config(config_path)
    config = SimulationConfig.from_dict(data)
    metrics = Simulation(config).run()
    pv_area = float(config.agent_parameters.pv_area)
    num_agents = int(config.num_agents)
    return {
        "variant": config_path.stem,
        "N_agents": num_agents,
        "A_PV": pv_area,
        "A_total": num_agents * pv_area,
        "E_host_total": metrics.E_host_values[-1] if metrics.E_host_values else 0.0,
    }


def _write_csv(rows: List[dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=["variant", "N_agents", "A_PV", "A_total", "E_host_total"],
        )
        writer.writeheader()
        writer.writerows(rows)


def _plot_results(rows: List[dict], output_path: Path) -> str:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        import matplotlib.pyplot as plt
    except ModuleNotFoundError as err:
        warning = f"Plot generation skipped: {err}"
        (output_path.parent / "PLOT_WARNING.txt").write_text(warning + "\n")
        return warning

    labels = [row["variant"] for row in rows]
    totals = [row["E_host_total"] for row in rows]
    fig, ax = plt.subplots()
    ax.bar(labels, totals)
    ax.set_xlabel("Configuration variant")
    ax.set_ylabel("E_host_total (Wh)")
    ax.set_title("PV Area vs Swarm Size (fixed total PV area)")
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
    return ""


def run_comparison(few_large_config: Path, many_small_config: Path, output_dir: Path) -> List[dict]:
    rows = [_run_single(few_large_config), _run_single(many_small_config)]
    _write_csv(rows, output_dir / "pv_area_vs_swarm_size.csv")
    warning = _plot_results(rows, output_dir / "plots" / "pv_area_vs_swarm_size.png")
    if warning:
        print(warning)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--few-large-config",
        type=Path,
        default=ROOT / "configs" / "pv_area_vs_swarm_size_few_large.json",
        help="Few-large variant config path.",
    )
    parser.add_argument(
        "--many-small-config",
        type=Path,
        default=ROOT / "configs" / "pv_area_vs_swarm_size_many_small.json",
        help="Many-small variant config path.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "outputs" / "latest" / "pv_area_vs_swarm_size",
        help="Output directory for comparison artifacts.",
    )
    args = parser.parse_args()

    run_comparison(args.few_large_config, args.many_small_config, args.out)


if __name__ == "__main__":
    main()
