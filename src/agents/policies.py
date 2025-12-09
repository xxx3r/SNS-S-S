"""Policy helpers for SNS agents."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from src.agents.sns_agent import AgentMode, SNSAgent


@dataclass
class PolicyContext:
    """Runtime information used by policy functions."""

    sunlit: bool
    host_deficit: float
    target_theta: Optional[float] = None


class BaselinePolicy:
    """Baseline policy that mirrors the simple harvest/idle behavior."""

    def decide(self, agent: SNSAgent, context: PolicyContext) -> AgentMode:
        return AgentMode.HARVEST if context.sunlit else AgentMode.IDLE


class CoordinatedPolicy:
    """Coordinated policy using host deficit and energy thresholds."""

    def __init__(self, low_threshold: float, high_threshold: float) -> None:
        self.low_threshold = low_threshold
        self.high_threshold = high_threshold

    def decide(self, agent: SNSAgent, context: PolicyContext) -> AgentMode:
        if agent.energy < self.low_threshold:
            return AgentMode.HARVEST if context.sunlit else AgentMode.IDLE

        if agent.energy > self.high_threshold and context.host_deficit > 0:
            return AgentMode.COMM_BEAM

        if context.target_theta is not None and agent.energy >= self.low_threshold:
            return AgentMode.MOVE

        return AgentMode.HARVEST if context.sunlit else AgentMode.IDLE


def build_policy(policy_name: str, low_threshold: float, high_threshold: float):
    """Construct a policy object given a name and threshold parameters."""

    if policy_name == "coordinated":
        return CoordinatedPolicy(low_threshold=low_threshold, high_threshold=high_threshold)
    return BaselinePolicy()
