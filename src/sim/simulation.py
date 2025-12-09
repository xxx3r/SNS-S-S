"""Core simulation loop for SNS-S-S."""

from __future__ import annotations

import math
from typing import List

from src.agents.sns_agent import SNSAgent
from src.host.host_collector import HostCollector
from src.sim.config import SimulationConfig
from src.sim.metrics import MetricsRecorder
from src.world.asteroid_world import AsteroidWorld


class Simulation:
    """Run the AsteroidWorld scenario for a configured set of agents."""

    def __init__(self, config: SimulationConfig):
        self.config = config
        self.world = AsteroidWorld(rotation_rate=config.rotation_rate, solar_flux=config.solar_flux)
        self.host = HostCollector()
        self.metrics = MetricsRecorder()
        self.agents: List[SNSAgent] = self._init_agents()

    def _init_agents(self) -> List[SNSAgent]:
        """Create agents spaced evenly around the body."""

        thetas = [2 * math.pi * i / self.config.num_agents for i in range(self.config.num_agents)]
        return [SNSAgent(agent_id=i, theta=float(theta), params=self.config.agent_parameters) for i, theta in enumerate(thetas)]

    def run(self) -> MetricsRecorder:
        """Execute the simulation time loop."""

        steps = int(self.config.duration // self.config.dt)
        for step in range(steps):
            t = step * self.config.dt
            for agent in self.agents:
                agent.step(self.world, self.host, t=t, dt=self.config.dt, coordinated=self.config.policy == "coordinated")

            energies = [agent.energy for agent in self.agents]
            self.metrics.record(t, self.host.energy, energies)

        return self.metrics
