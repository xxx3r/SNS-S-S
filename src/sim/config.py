"""Configuration dataclasses for SNS-S-S simulations."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict

from src.agents.sns_agent import AgentParameters


@dataclass
class SimulationConfig:
    """Container for simulation parameters.

    Attributes
    ----------
    host_demand_rate:
        Linear demand rate (Wh/hour) used to build a simple host demand
        curve when an explicit demand function is not provided.
    """

    duration: float = 2 * 3600.0
    dt: float = 60.0
    rotation_rate: float = 2 * math.pi / (4 * 3600.0)
    solar_flux: float = 1000.0
    num_agents: int = 5
    policy: str = "baseline"
    host_demand_rate: float = 0.0
    agent_parameters: AgentParameters = field(default_factory=AgentParameters)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SimulationConfig":
        """Construct from a plain dictionary (e.g., loaded from JSON)."""

        agent_params_data = data.get("agent_parameters", {})
        agent_params = AgentParameters(**agent_params_data)
        return cls(
            duration=float(data.get("duration", cls.duration)),
            dt=float(data.get("dt", cls.dt)),
            rotation_rate=float(data.get("rotation_rate", cls.rotation_rate)),
            solar_flux=float(data.get("solar_flux", cls.solar_flux)),
            num_agents=int(data.get("num_agents", cls.num_agents)),
            policy=str(data.get("policy", cls.policy)),
            host_demand_rate=float(data.get("host_demand_rate", cls.host_demand_rate)),
            agent_parameters=agent_params,
        )

    @classmethod
    def from_json(cls, path: str | Path) -> "SimulationConfig":
        """Load configuration from a JSON file."""

        data = json.loads(Path(path).read_text())
        return cls.from_dict(data)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize configuration to a dictionary."""

        return {
            "duration": self.duration,
            "dt": self.dt,
            "rotation_rate": self.rotation_rate,
            "solar_flux": self.solar_flux,
            "num_agents": self.num_agents,
            "policy": self.policy,
            "host_demand_rate": self.host_demand_rate,
            "agent_parameters": self.agent_parameters.__dict__,
        }
