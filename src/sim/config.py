"""Configuration dataclasses for mission-aware SNS-S-S simulations."""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List

from src.agents.sns_agent import AgentParameters, AgentRole


@dataclass
class SimulationConfig:
    """Complete configuration for one reproducible SNS experiment."""

    duration: float = 2 * 3600.0
    dt: float = 60.0
    scenario: str = "asteroid"
    mission: str = "survey_intelligence"
    rotation_rate: float = 2 * math.pi / (4 * 3600.0)
    solar_flux: float = 1360.0
    num_agents: int = 5
    policy: str = "survey"
    host_demand_rate: float = 0.0
    coverage_bin_count: int = 36
    agent_roles: List[str] = field(default_factory=list)
    environment: Dict[str, Any] = field(default_factory=dict)
    agent_parameters: AgentParameters = field(default_factory=AgentParameters)

    def validate(self) -> None:
        """Validate mission, environment, and timestep settings."""
        if self.duration <= 0 or self.dt <= 0:
            raise ValueError("duration and dt must be positive")
        if self.num_agents <= 0:
            raise ValueError("num_agents must be positive")
        if self.coverage_bin_count <= 0:
            raise ValueError("coverage_bin_count must be positive")
        if self.scenario not in {"asteroid", "geo_ring"}:
            raise ValueError("scenario must be 'asteroid' or 'geo_ring'")
        for role in self.agent_roles:
            AgentRole(role)
        self.agent_parameters.validate()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SimulationConfig":
        """Construct from a plain dictionary."""
        agent_params = AgentParameters(**data.get("agent_parameters", {}))
        config = cls(
            duration=float(data.get("duration", cls.duration)),
            dt=float(data.get("dt", cls.dt)),
            scenario=str(data.get("scenario", "asteroid")),
            mission=str(data.get("mission", "survey_intelligence")),
            rotation_rate=float(data.get("rotation_rate", cls.rotation_rate)),
            solar_flux=float(data.get("solar_flux", cls.solar_flux)),
            num_agents=int(data.get("num_agents", cls.num_agents)),
            policy=str(data.get("policy", cls.policy)),
            host_demand_rate=float(data.get("host_demand_rate", cls.host_demand_rate)),
            coverage_bin_count=int(data.get("coverage_bin_count", cls.coverage_bin_count)),
            agent_roles=[str(value) for value in data.get("agent_roles", [])],
            environment=dict(data.get("environment", {})),
            agent_parameters=agent_params,
        )
        config.validate()
        return config

    @classmethod
    def from_json(cls, path: str | Path) -> "SimulationConfig":
        """Load configuration from a JSON file."""
        return cls.from_dict(json.loads(Path(path).read_text()))

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the full configuration."""
        return asdict(self)
