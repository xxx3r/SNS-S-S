"""Sweep eta_beam values for the coordinated policy and plot results."""

from __future__ import annotations

import csv
import json
import sys
import argparse
from copy import deepcopy
from pathlib import Path
from typing import Iterable, List, Tuple


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.sim.config import SimulationConfig  # noqa: E402
from src.sim.simulation import Simulation  # noqa: E402


DEFAULT_SWEEP_VALUES: Tuple[float, ...] = (0.1, 0.3, 0.5, 0.7, 0.9)


def _load_config(base_path: Path) -> dict:
    return json.loads(base_path.read_text())


def _run_single(config_data: dict) -> float:
    config = SimulationConfig.from_dict(config_data)
    metrics = Simulation(config).run()
    return metrics.E_host_values[-1] if metrics.E_host_values else 0.0


def run_eta_beam_sweep(
    base_config_path: Path,
    eta_values: Iterable[float] = DEFAULT_SWEEP_VALUES,
    output_dir: Path | None = None,
) -> List[dict]:
    """Run the sweep and return summary rows."""

    base_data = _load_config(base_config_path)
    results: List[dict] = []
    out_dir = output_dir or ROOT / "experiments" / "outputs" / "eta_beam_sweep"
    out_dir.mkdir(parents=True, exist_ok=True)

    for eta in eta_values:
        cfg = deepcopy(base_data)
        cfg["agent_parameters"]["beam_efficiency"] = eta
        E_host_total = _run_single(cfg)
        results.append({"eta_beam": eta, "E_host_total": E_host_total})

    csv_path = out_dir / "eta_beam_sweep.csv"
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["eta_beam", "E_host_total"])
        writer.writeheader()
        writer.writerows(results)

    plot_warning = _plot_results(results, out_dir / "plots" / "eta_beam_vs_host_energy.png")
    if plot_warning:
        print(plot_warning)
    return results


def _plot_results(results: List[dict], output_path: Path) -> str:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        import matplotlib.pyplot as plt
    except ModuleNotFoundError as err:
        warning = f"Plot generation skipped: {err}"
        (output_path.parent / "PLOT_WARNING.txt").write_text(warning + "\n")
        return warning

    eta = [row["eta_beam"] for row in results]
    totals = [row["E_host_total"] for row in results]
    fig, ax = plt.subplots()
    ax.plot(eta, totals, marker="o")
    ax.set_xlabel("eta_beam")
    ax.set_ylabel("E_host_total (Wh)")
    ax.set_title("Beaming efficiency sweep")
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
    return ""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs" / "asteroid_coordinated.json",
        help="Path to the coordinated base config to sweep.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "experiments" / "outputs" / "eta_beam_sweep",
        help="Directory where CSV + plot outputs are written.",
    )
    args = parser.parse_args()
    run_eta_beam_sweep(args.config, output_dir=args.out)


if __name__ == "__main__":
    main()
