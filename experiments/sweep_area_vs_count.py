"""Compare few-large vs many-small agent configurations for fixed PV area."""

from __future__ import annotations

import csv
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import List

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.sim.config import SimulationConfig  # noqa: E402
from src.sim.simulation import Simulation  # noqa: E402


def _load_base(path: Path) -> dict:
    return json.loads(path.read_text())


def _run_config(config_data: dict) -> float:
    config = SimulationConfig.from_dict(config_data)
    metrics = Simulation(config).run()
    return metrics.E_host_values[-1] if metrics.E_host_values else 0.0


def _build_scenario(data: dict, num_agents: int, pv_area: float) -> dict:
    cfg = deepcopy(data)
    cfg["num_agents"] = num_agents
    cfg["agent_parameters"]["pv_area"] = pv_area
    return cfg


def run_area_vs_count(base_config_path: Path, output_dir: Path | None = None) -> List[dict]:
    """Run the area vs count comparison and return summary rows."""

    data = _load_base(base_config_path)
    total_area = float(data.get("total_pv_area", 0.0))
    few_agents = int(data.get("few_large_num_agents", 3))
    many_agents = int(data.get("many_small_num_agents", 9))

    if total_area <= 0:
        raise ValueError("total_pv_area must be positive in the base config")

    few_area = total_area / few_agents
    many_area = total_area / many_agents

    out_dir = output_dir or ROOT / "experiments" / "outputs" / "area_vs_count"
    out_dir.mkdir(parents=True, exist_ok=True)

    scenarios = [
        {"label": "few_large", "num_agents": few_agents, "pv_area": few_area},
        {"label": "many_small", "num_agents": many_agents, "pv_area": many_area},
    ]

    results: List[dict] = []
    for scenario in scenarios:
        cfg = _build_scenario(data, scenario["num_agents"], scenario["pv_area"])
        E_host_total = _run_config(cfg)
        results.append(
            {
                "label": scenario["label"],
                "N_agents": scenario["num_agents"],
                "A_PV": scenario["pv_area"],
                "E_host_total": E_host_total,
            }
        )

    csv_path = out_dir / "area_vs_count.csv"
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["label", "N_agents", "A_PV", "E_host_total"])
        writer.writeheader()
        writer.writerows(results)

    _plot_results(results, out_dir / "area_vs_count.png")
    return results


def _plot_results(results: List[dict], output_path: Path) -> None:
    labels = [row["label"] for row in results]
    totals = [row["E_host_total"] for row in results]
    areas = [row["A_PV"] for row in results]

    fig, ax = plt.subplots()
    ax.bar(labels, totals)
    for idx, total in enumerate(totals):
        ax.text(idx, total, f"A={areas[idx]:.2f}", ha="center", va="bottom")
    ax.set_ylabel("E_host_total (Wh)")
    ax.set_title("PV area vs agent count")
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path)
    plt.close(fig)


def main() -> None:
    base_config = ROOT / "configs" / "area_vs_count_base.json"
    run_area_vs_count(base_config)


if __name__ == "__main__":
    main()
