"""Run baseline vs coordinated scenarios for the AsteroidWorld."""

from __future__ import annotations

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
from src.utils.plotting import plot_dead_agent_count, plot_host_energy, plot_mean_agent_energy  # noqa: E402


def _try_generate_plots(metrics, plots_dir: Path) -> dict:
    """Generate plots when matplotlib is available."""

    try:
        plot_host_energy(metrics, plots_dir / "host_energy.png")
        plot_mean_agent_energy(metrics, plots_dir / "mean_agent_energy.png")
        plot_dead_agent_count(metrics, plots_dir / "dead_agent_count.png")
        return {"plots_generated": True, "plot_warning": ""}
    except RuntimeError as err:
        warning = f"Plot generation skipped: {err}"
        (plots_dir / "PLOT_WARNING.txt").write_text(warning + "\n")
        return {"plots_generated": False, "plot_warning": warning}


def _write_metrics_csv(metrics, output_path: Path) -> None:
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


def run_scenario(config_path: Path, output_dir: Path) -> dict:
    """Run a single simulation and persist metrics/plots."""

    config = SimulationConfig.from_json(config_path)
    sim = Simulation(config)
    metrics = sim.run()

    output_dir.mkdir(parents=True, exist_ok=True)
    run_dir = output_dir / config.policy
    plots_dir = run_dir / "plots"
    run_dir.mkdir(parents=True, exist_ok=True)
    plots_dir.mkdir(parents=True, exist_ok=True)

    _write_metrics_csv(metrics, run_dir / "metrics.csv")
    plot_state = _try_generate_plots(metrics, plots_dir)
    summary = {
        "policy": config.policy,
        "config": asdict(config),
        "final_host_energy": metrics.E_host_values[-1] if metrics.E_host_values else 0.0,
        "mean_agent_energy": metrics.E_mean_values[-1] if metrics.E_mean_values else 0.0,
        "dead_agent_count": metrics.dead_agent_count[-1] if metrics.dead_agent_count else 0,
        **plot_state,
    }
    return summary


def main() -> None:
    baseline_config = ROOT / "configs" / "asteroid_baseline.json"
    coordinated_config = ROOT / "configs" / "asteroid_coordinated.json"
    output_dir = ROOT / "experiments" / "outputs" / "baseline_vs_coordinated"

    print("Running baseline...")
    baseline_summary = run_scenario(baseline_config, output_dir)
    print("Running coordinated...")
    coordinated_summary = run_scenario(coordinated_config, output_dir)

    summaries = [baseline_summary, coordinated_summary]
    summary_path = output_dir / "baseline_vs_coordinated_summary.json"
    summary_path.write_text(json.dumps(summaries, indent=2))

    comparison_rows = [
        {
            "policy": summary["policy"],
            "final_host_energy": summary["final_host_energy"],
            "mean_agent_energy": summary["mean_agent_energy"],
            "dead_agent_count": summary["dead_agent_count"],
        }
        for summary in summaries
    ]
    comparison_path = output_dir / "baseline_vs_coordinated_comparison.csv"
    with comparison_path.open("w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=comparison_rows[0].keys())
        writer.writeheader()
        writer.writerows(comparison_rows)
    print(f"Wrote summary to {summary_path}")


if __name__ == "__main__":
    main()
