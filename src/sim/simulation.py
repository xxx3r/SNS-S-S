"""Mission-aware simulation loop for SNS swarm research."""

from __future__ import annotations

import math
from typing import List, Optional, Tuple

from src.agents.policies import PolicyContext, build_policy
from src.agents.sns_agent import AgentRole, SNSAgent
from src.host.host_collector import HostCollector
from src.sim.config import SimulationConfig
from src.sim.metrics import MetricsRecorder
from src.world.asteroid_world import AsteroidWorld
from src.world.geo_ring_world import GEORingWorld


class Simulation:
    """Run an asteroid-survey or GEO-ring scenario with explicit energy flows."""

    def __init__(self, config: SimulationConfig):
        config.validate()
        self.config = config
        self.world = self._build_world()
        self.host = HostCollector(demand_rate=config.host_demand_rate)
        self.metrics = MetricsRecorder()
        self.covered_regions: set[int] = set()
        self.agents: List[SNSAgent] = self._init_agents()
        self.policy = build_policy(
            policy_name=config.policy,
            low_threshold=config.agent_parameters.low_threshold,
            high_threshold=config.agent_parameters.high_threshold,
        )

    def _build_world(self):
        env = self.config.environment
        if self.config.scenario == "geo_ring":
            return GEORingWorld(
                solar_flux=self.config.solar_flux,
                orbital_period_s=float(env.get("orbital_period_s", 86164.0)),
                eclipse_fraction=float(env.get("eclipse_fraction", 0.05)),
                coverage_bin_count=self.config.coverage_bin_count,
                sun_temperature_K=float(env.get("sun_temperature_K", 315.0)),
                eclipse_temperature_K=float(env.get("eclipse_temperature_K", 230.0)),
                receiver_phase_center_rad=float(env.get("receiver_phase_center_rad", 0.0)),
                receiver_visibility_fraction=float(env.get("receiver_visibility_fraction", 1.0)),
            )
        return AsteroidWorld(
            rotation_rate=self.config.rotation_rate,
            solar_flux=self.config.solar_flux,
            sun_direction=float(env.get("sun_direction", 0.0)),
            coverage_bin_count=self.config.coverage_bin_count,
            day_temperature_K=float(env.get("day_temperature_K", 330.0)),
            night_temperature_K=float(env.get("night_temperature_K", 190.0)),
        )

    def _roles(self) -> list[AgentRole]:
        if self.config.agent_roles:
            values = [AgentRole(role) for role in self.config.agent_roles]
            return [values[index % len(values)] for index in range(self.config.num_agents)]
        if self.config.policy == "baseline":
            return [AgentRole.SCOUT] * self.config.num_agents
        default_mix = [AgentRole.SCOUT, AgentRole.SCOUT, AgentRole.SENSOR, AgentRole.RELAY, AgentRole.STORAGE]
        return [default_mix[index % len(default_mix)] for index in range(self.config.num_agents)]

    def _init_agents(self) -> List[SNSAgent]:
        thetas = [2 * math.pi * index / self.config.num_agents for index in range(self.config.num_agents)]
        roles = self._roles()
        return [
            SNSAgent(agent_id=index, theta=float(theta), params=self.config.agent_parameters, role=roles[index])
            for index, theta in enumerate(thetas)
        ]

    def _largest_gap_target(self) -> Tuple[Optional[int], Optional[float]]:
        """Return a survey-capable agent and midpoint of the largest angular gap."""
        survey_agents = [agent for agent in self.agents if agent.role in {AgentRole.SCOUT, AgentRole.SENSOR}]
        if len(survey_agents) < 2:
            return None, None
        ordered = sorted(survey_agents, key=lambda agent: agent.theta)
        max_gap = -1.0
        target_theta: Optional[float] = None
        agent_id: Optional[int] = None
        for index, agent in enumerate(ordered):
            next_theta = ordered[(index + 1) % len(ordered)].theta
            gap = (next_theta - agent.theta) % (2 * math.pi)
            if gap > max_gap:
                max_gap = gap
                target_theta = (agent.theta + gap / 2.0) % (2 * math.pi)
                agent_id = agent.id
        nominal_gap = 2 * math.pi / len(ordered)
        return (None, None) if max_gap < 1.2 * nominal_gap else (agent_id, target_theta)

    def run(self) -> MetricsRecorder:
        """Execute the configured scenario and return recorded metrics."""
        steps = int(self.config.duration // self.config.dt)
        for step_index in range(steps):
            t = step_index * self.config.dt
            target_agent_id, target_theta = self._largest_gap_target()
            step_results = []
            for agent in self.agents:
                sample = self.world.sample(agent.theta, t)
                host_deficit = self.host.get_deficit(t + self.config.dt)
                context = PolicyContext(
                    sunlit=sample.sunlit,
                    host_deficit=host_deficit,
                    target_theta=target_theta if agent.id == target_agent_id else None,
                    sample=sample,
                    coverage_fraction=len(self.covered_regions) / self.world.coverage_bin_count,
                )
                result = agent.step(self.world, self.host, t=t, dt=self.config.dt, policy=self.policy, context=context)
                step_results.append(result)
                if agent.role in {AgentRole.SCOUT, AgentRole.SENSOR}:
                    self.covered_regions.add(result.region_id)
            coverage = len(self.covered_regions) / self.world.coverage_bin_count
            self.metrics.record(
                t,
                self.host.energy,
                [agent.energy for agent in self.agents],
                step_results=step_results,
                coverage_fraction=coverage,
                roles=[agent.role.value for agent in self.agents],
            )
        return self.metrics
