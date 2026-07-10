"""Transparent rule-based policies for Summer 2026 SNS simulations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from src.agents.sns_agent import AgentMode, AgentRole, SNSAgent
from src.world.base import EnvironmentSample


@dataclass
class PolicyContext:
    """Runtime information supplied to a node policy."""

    sunlit: bool
    host_deficit: float
    target_theta: Optional[float] = None
    sample: Optional[EnvironmentSample] = None
    coverage_fraction: float = 0.0
    predicted_shadow_s: float = 0.0


class BaselinePolicy:
    """Independent node policy used as an experimental control."""

    def decide(self, agent: SNSAgent, context: PolicyContext) -> AgentMode:
        return AgentMode.HARVEST if context.sunlit else AgentMode.SLEEP


class CoordinatedPolicy:
    """Role-aware policy for survival, surveying, and host delivery."""

    def __init__(self, low_threshold: float, high_threshold: float) -> None:
        self.low_threshold = low_threshold
        self.high_threshold = high_threshold

    def decide(self, agent: SNSAgent, context: PolicyContext) -> AgentMode:
        if not context.sunlit and agent.energy <= self.low_threshold:
            return AgentMode.SLEEP
        if agent.energy < self.low_threshold:
            return AgentMode.HARVEST if context.sunlit else AgentMode.SLEEP

        if (
            agent.role in {AgentRole.RELAY, AgentRole.STORAGE}
            and agent.energy > self.high_threshold
            and context.host_deficit > 0
            and (context.sample is None or context.sample.line_of_sight_to_host)
        ):
            return AgentMode.COMM_BEAM

        if context.target_theta is not None and agent.role in {AgentRole.SCOUT, AgentRole.SENSOR}:
            return AgentMode.MOVE

        if agent.role in {AgentRole.SCOUT, AgentRole.SENSOR} and context.sunlit:
            return AgentMode.SCOUT

        return AgentMode.HARVEST if context.sunlit else AgentMode.IDLE


class SurveyPolicy(CoordinatedPolicy):
    """Alias emphasizing the asteroid-resource intelligence mission."""


def build_policy(policy_name: str, low_threshold: float, high_threshold: float):
    """Construct a known policy or raise for an unknown name."""
    normalized = policy_name.strip().lower()
    if normalized == "baseline":
        return BaselinePolicy()
    if normalized in {"coordinated", "survey", "role_aware"}:
        return SurveyPolicy(low_threshold=low_threshold, high_threshold=high_threshold)
    raise ValueError(f"Unknown policy: {policy_name}")
