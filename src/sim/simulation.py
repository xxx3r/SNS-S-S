"""Core simulation loop for SNS-S-S."""

from __future__ import annotations

import math
from typing import List, Optional, Tuple

from src.agents.sns_agent import SNSAgent
from src.agents.policies import PolicyContext, build_policy
from src.host.host_collector import HostCollector
from src.sim.config import SimulationConfig
from src.sim.metrics import MetricsRecorder
from src.world.asteroid_world import AsteroidWorld


class Simulation:
    """Run the AsteroidWorld scenario for a configured set of agents."""

    def __init__(self, config: SimulationConfig):
        self.config = config
        self.world = AsteroidWorld(rotation_rate=config.rotation_rate, solar_flux=config.solar_flux)
        self.host = HostCollector(demand_rate=config.host_demand_rate)
        self.metrics = MetricsRecorder()
        self.agents: List[SNSAgent] = self._init_agents()
        self.policy = build_policy(
            policy_name=config.policy,
            low_threshold=self.config.agent_parameters.low_threshold,
            high_threshold=self.config.agent_parameters.high_threshold,
        )

    def _init_agents(self) -> List[SNSAgent]:
        """Create agents spaced evenly around the body."""

        thetas = [2 * math.pi * i / self.config.num_agents for i in range(self.config.num_agents)]
        return [SNSAgent(agent_id=i, theta=float(theta), params=self.config.agent_parameters) for i, theta in enumerate(thetas)]

    def _largest_gap_target(self) -> Tuple[Optional[int], Optional[float]]:
        """Return the agent id and target theta for the largest coverage gap."""

        if len(self.agents) < 2:
            return None, None

        ordered = sorted(self.agents, key=lambda a: a.theta)
        max_gap = -1.0
        target_theta = None
        agent_id = None
        n = len(ordered)
        for i in range(n):
            theta_i = ordered[i].theta
            theta_next = ordered[(i + 1) % n].theta
            gap = (theta_next - theta_i) % (2 * math.pi)
            if gap > max_gap:
                max_gap = gap
                target_theta = (theta_i + gap / 2.0) % (2 * math.pi)
                agent_id = ordered[i].id

        nominal_gap = 2 * math.pi / len(self.agents)
        if max_gap < 1.2 * nominal_gap:
            return None, None
        return agent_id, target_theta

    def run(self) -> MetricsRecorder:
        """Execute the simulation time loop."""

        steps = int(self.config.duration // self.config.dt)
        for step in range(steps):
            t = step * self.config.dt
            host_deficit = self.host.get_deficit(t)
            target_agent_id, target_theta = self._largest_gap_target()

            for agent in self.agents:
                context = PolicyContext(
                    sunlit=self.world.is_sunlit(agent.theta, t),
                    host_deficit=host_deficit,
                    target_theta=target_theta if agent.id == target_agent_id else None,
                )
                agent.step(self.world, self.host, t=t, dt=self.config.dt, policy=self.policy, context=context)

            energies = [agent.energy for agent in self.agents]
            self.metrics.record(t, self.host.energy, energies)

        return self.metrics
