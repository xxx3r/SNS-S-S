"""Geometry-closed parasitic thermal-conductance budgets for SNS packages.

The model treats each solid path from the warm core to the external shell as a
one-dimensional conductive element with ``G = k A / L``. It is intentionally a
first-order screening model: contact resistance, radiation inside gaps,
multidimensional spreading, temperature dependence, and assembly variation must
be added before interpreting a result as package qualification.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable


@dataclass(frozen=True)
class ConductivePath:
    """One repeated conductive path between the core and external shell."""

    name: str
    category: str
    count: int
    thermal_conductivity_W_m_K: float
    cross_section_area_m2: float
    length_m: float
    evidence_class: str = "assumed"

    def validate(self) -> None:
        if not self.name or not self.category:
            raise ValueError("name and category are required")
        if self.count <= 0:
            raise ValueError("count must be positive")
        if self.thermal_conductivity_W_m_K <= 0:
            raise ValueError("thermal_conductivity_W_m_K must be positive")
        if self.cross_section_area_m2 <= 0:
            raise ValueError("cross_section_area_m2 must be positive")
        if self.length_m <= 0:
            raise ValueError("length_m must be positive")

    @property
    def single_path_conductance_W_K(self) -> float:
        """Return ``k A / L`` for one path."""
        self.validate()
        return (
            self.thermal_conductivity_W_m_K
            * self.cross_section_area_m2
            / self.length_m
        )

    @property
    def total_conductance_W_K(self) -> float:
        """Return conductance for all repeated paths."""
        return self.count * self.single_path_conductance_W_K


@dataclass(frozen=True)
class PackageConductanceBudget:
    """Declared package architecture and its parasitic-conductance target."""

    name: str
    target_parasitic_conductance_W_K: float
    paths: tuple[ConductivePath, ...]
    uncertainty_multiplier: float = 1.0

    def validate(self) -> None:
        if not self.name:
            raise ValueError("name is required")
        if self.target_parasitic_conductance_W_K <= 0:
            raise ValueError("target_parasitic_conductance_W_K must be positive")
        if not self.paths:
            raise ValueError("at least one conductive path is required")
        if self.uncertainty_multiplier < 1.0:
            raise ValueError("uncertainty_multiplier must be at least 1")
        for path in self.paths:
            path.validate()


def evaluate_package_budget(budget: PackageConductanceBudget) -> dict:
    """Evaluate total, margin, dominant paths, and PASS/FAIL for a package."""
    budget.validate()
    rows = []
    nominal_total = sum(path.total_conductance_W_K for path in budget.paths)
    for path in budget.paths:
        rows.append(
            {
                **asdict(path),
                "single_path_conductance_W_K": path.single_path_conductance_W_K,
                "total_conductance_W_K": path.total_conductance_W_K,
                "fraction_of_nominal_total": (
                    path.total_conductance_W_K / nominal_total
                    if nominal_total > 0
                    else 0.0
                ),
            }
        )
    conservative_total = nominal_total * budget.uncertainty_multiplier
    margin = budget.target_parasitic_conductance_W_K - conservative_total
    ranked = sorted(rows, key=lambda row: row["total_conductance_W_K"], reverse=True)
    return {
        "name": budget.name,
        "target_parasitic_conductance_W_K": budget.target_parasitic_conductance_W_K,
        "uncertainty_multiplier": budget.uncertainty_multiplier,
        "nominal_total_conductance_W_K": nominal_total,
        "conservative_total_conductance_W_K": conservative_total,
        "margin_W_K": margin,
        "status": "PASS" if margin >= 0 else "FAIL",
        "dominant_path": ranked[0]["name"],
        "paths": ranked,
    }


def budget_from_dict(data: dict) -> PackageConductanceBudget:
    """Construct a package budget from a JSON-compatible dictionary."""
    return PackageConductanceBudget(
        name=str(data["name"]),
        target_parasitic_conductance_W_K=float(
            data["target_parasitic_conductance_W_K"]
        ),
        uncertainty_multiplier=float(data.get("uncertainty_multiplier", 1.0)),
        paths=tuple(ConductivePath(**path) for path in data["paths"]),
    )


def summarize_categories(path_rows: Iterable[dict]) -> dict[str, float]:
    """Aggregate evaluated path conductance by package category."""
    totals: dict[str, float] = {}
    for row in path_rows:
        category = str(row["category"])
        totals[category] = totals.get(category, 0.0) + float(
            row["total_conductance_W_K"]
        )
    return dict(sorted(totals.items(), key=lambda item: item[1], reverse=True))
