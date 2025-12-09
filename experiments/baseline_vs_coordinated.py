"""Run baseline vs coordinated scenarios for the AsteroidWorld."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.sim.config import SimulationConfig  # noqa: E402
from src.sim.simulation import Simulation  # noqa: E402
from src.utils.plotting import plot_host_energy  # noqa: E402


def run_scenario(config_path: Path, output_dir: Path) -> dict:
    """Run a single simulation and persist the host energy plot."""

    config = SimulationConfig.from_json(config_path)
    sim = Simulation(config)
    metrics = sim.run()

    output_dir.mkdir(parents=True, exist_ok=True)
    plot_host_energy(metrics, output_dir / f"host_energy_{config.policy}.png")
    summary = {
        "policy": config.policy,
        "final_host_energy": metrics.E_host_values[-1] if metrics.E_host_values else 0.0,
        "mean_agent_energy": metrics.E_mean_values[-1] if metrics.E_mean_values else 0.0,
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
    print(f"Wrote summary to {summary_path}")


if __name__ == "__main__":
    main()
