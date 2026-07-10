"""Transparent Asteroid Resource Confidence Index (ARCI) scaffolding."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Mapping

from src.utils.math_utils import clamp


DEFAULT_WEIGHTS: Mapping[str, float] = {
    "composition": 0.20,
    "accessibility": 0.15,
    "recoverability": 0.15,
    "energy_environment": 0.10,
    "surface_operations": 0.15,
    "communications": 0.10,
    "market_mission_value": 0.15,
}


@dataclass(frozen=True)
class ArciDimension:
    """One normalized ARCI dimension with an evidence confidence."""

    score: float
    confidence: float
    rationale: str = ""

    def validate(self) -> None:
        if not 0.0 <= self.score <= 1.0:
            raise ValueError("dimension score must be in [0, 1]")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("dimension confidence must be in [0, 1]")


@dataclass(frozen=True)
class ArciResult:
    """Computed ARCI score, confidence, uncertainty band, and decision gate."""

    score: float
    confidence: float
    confidence_adjusted_score: float
    lower_bound: float
    upper_bound: float
    grade: str
    recommendation: str
    dimensions: dict[str, dict]
    weights: dict[str, float]

    def to_dict(self) -> dict:
        return asdict(self)


class ArciAssessment:
    """Combine resource, mission, environment, and evidence dimensions."""

    def __init__(self, dimensions: Mapping[str, ArciDimension], weights: Mapping[str, float] | None = None) -> None:
        self.dimensions = dict(dimensions)
        self.weights = dict(weights or DEFAULT_WEIGHTS)
        missing = set(self.weights) - set(self.dimensions)
        if missing:
            raise ValueError(f"Missing ARCI dimensions: {', '.join(sorted(missing))}")
        if any(weight < 0 for weight in self.weights.values()) or sum(self.weights.values()) <= 0:
            raise ValueError("ARCI weights must be non-negative with a positive total")
        for dimension in self.dimensions.values():
            dimension.validate()

    @classmethod
    def from_dict(cls, data: Mapping) -> "ArciAssessment":
        dimensions = {name: ArciDimension(**value) for name, value in data["dimensions"].items()}
        return cls(dimensions=dimensions, weights=data.get("weights"))

    def evaluate(self) -> ArciResult:
        """Compute a deliberately simple v0.1 weighted score."""
        total_weight = sum(self.weights.values())
        score = sum(self.weights[name] * self.dimensions[name].score for name in self.weights) / total_weight
        confidence = sum(self.weights[name] * self.dimensions[name].confidence for name in self.weights) / total_weight
        adjusted = score * confidence
        uncertainty = 1.0 - confidence
        lower = clamp(score - uncertainty * score, 0.0, 1.0)
        upper = clamp(score + uncertainty * (1.0 - score), 0.0, 1.0)
        return ArciResult(
            score=score,
            confidence=confidence,
            confidence_adjusted_score=adjusted,
            lower_bound=lower,
            upper_bound=upper,
            grade=_grade(adjusted),
            recommendation=_recommendation(score, confidence, adjusted),
            dimensions={name: asdict(value) for name, value in self.dimensions.items()},
            weights=self.weights,
        )


def _grade(value: float) -> str:
    if value >= 0.80:
        return "A"
    if value >= 0.70:
        return "B+"
    if value >= 0.60:
        return "B"
    if value >= 0.50:
        return "C+"
    if value >= 0.40:
        return "C"
    return "research-only"


def _recommendation(score: float, confidence: float, adjusted: float) -> str:
    if confidence < 0.45:
        return "collect_more_data"
    if adjusted >= 0.70:
        return "precursor_mission_justified"
    if adjusted >= 0.50:
        return "targeted_follow_up"
    if score >= 0.65:
        return "reduce_uncertainty_before_commitment"
    return "deprioritize_or_reframe"
