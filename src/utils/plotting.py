"""Simple plotting helpers for SNS-S-S metrics."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt

from src.sim.metrics import MetricsRecorder


def plot_host_energy(metrics: MetricsRecorder, output_path: Optional[str] = None) -> Path:
    """Plot host energy over time using matplotlib.

    Parameters
    ----------
    metrics: MetricsRecorder
        Recorder containing simulation history.
    output_path: Optional[str]
        Path for saving the plot. If omitted, defaults to ``host_energy.png``
        in the current working directory.

    Returns
    -------
    Path
        Location of the saved figure.
    """

    output_file = Path(output_path or "host_energy.png")
    fig, ax = plt.subplots()
    ax.plot(metrics.t_values, metrics.E_host_values, label="Host energy")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Energy (Wh)")
    ax.set_title("Host energy over time")
    ax.legend()
    fig.tight_layout()
    output_file.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_file)
    plt.close(fig)
    return output_file


def plot_mean_agent_energy(metrics: MetricsRecorder, output_path: Optional[str] = None) -> Path:
    """Plot mean agent energy over time using matplotlib."""

    output_file = Path(output_path or "mean_agent_energy.png")
    fig, ax = plt.subplots()
    ax.plot(metrics.t_values, metrics.E_mean_values, label="Mean agent energy")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Energy (Wh)")
    ax.set_title("Mean agent energy over time")
    ax.legend()
    fig.tight_layout()
    output_file.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_file)
    plt.close(fig)
    return output_file


def plot_dead_agent_count(metrics: MetricsRecorder, output_path: Optional[str] = None) -> Path:
    """Plot dead agent count over time using matplotlib."""

    output_file = Path(output_path or "dead_agent_count.png")
    fig, ax = plt.subplots()
    ax.plot(metrics.t_values, metrics.dead_agent_count, label="Dead agent count")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Agents")
    ax.set_title("Dead agent count over time")
    ax.legend()
    fig.tight_layout()
    output_file.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_file)
    plt.close(fig)
    return output_file
