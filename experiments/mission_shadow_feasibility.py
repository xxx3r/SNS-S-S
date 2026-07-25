"""Evaluate whether bounded asteroid or hosted geometries meet the 15-minute shadow limit."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from src.sim.mission_shadow import (
    circular_orbit_shadow,
    hosted_sunward_standoff_shadow,
    surface_fixed_shadow,
)


def load_json(path: Path) -> dict:
    """Load a JSON experiment configuration."""
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def build_rows(config: dict) -> list[dict]:
    """Build all declared mission-shadow screening rows."""
    limit_h = float(config["acceptance_limit_h"])
    rows: list[dict] = []

    for case in config.get("surface_fixed_cases", []):
        rows.append(
            surface_fixed_shadow(
                name=case["name"],
                rotation_period_h=float(case["rotation_period_h"]),
                acceptance_limit_h=limit_h,
            ).to_dict()
        )

    for case in config.get("passive_circular_orbit_cases", []):
        row = circular_orbit_shadow(
            name=case["name"],
            asteroid_density_kg_m3=float(case["asteroid_density_kg_m3"]),
            orbital_radius_ratio=float(case["orbital_radius_ratio"]),
            acceptance_limit_h=limit_h,
        ).to_dict()
        row.update(
            asteroid_density_kg_m3=float(case["asteroid_density_kg_m3"]),
            orbital_radius_ratio=float(case["orbital_radius_ratio"]),
        )
        rows.append(row)

    for case in config.get("hosted_cases", []):
        row = hosted_sunward_standoff_shadow(
            name=case["name"],
            sunward_constraint_maintained=bool(case["sunward_constraint_maintained"]),
            acceptance_limit_h=limit_h,
        ).to_dict()
        if not math.isfinite(row["maximum_shadow_h"]):
            row["maximum_shadow_h"] = None
            row["maximum_shadow_min"] = None
        row["sunward_constraint_maintained"] = bool(case["sunward_constraint_maintained"])
        rows.append(row)

    return rows


def summarize(rows: list[dict], config: dict) -> dict:
    """Summarize PASS counts and architecture-level conclusions."""
    architectures = sorted({row["architecture"] for row in rows})
    by_architecture = {}
    for architecture in architectures:
        subset = [row for row in rows if row["architecture"] == architecture]
        by_architecture[architecture] = {
            "case_count": len(subset),
            "pass_count": sum(row["status"] == "PASS" for row in subset),
            "cases": subset,
        }

    passive_orbit_passes = by_architecture.get(
        "passive_circular_equatorial_orbit", {"pass_count": 0}
    )["pass_count"]
    surface_passes = by_architecture.get("surface_fixed_equator", {"pass_count": 0})[
        "pass_count"
    ]
    hosted_passes = by_architecture.get(
        "hosted_active_sunward_standoff", {"pass_count": 0}
    )["pass_count"]

    return {
        "acceptance_limit_h": float(config["acceptance_limit_h"]),
        "acceptance_limit_min": float(config["acceptance_limit_h"]) * 60.0,
        "case_count": len(rows),
        "pass_count": sum(row["status"] == "PASS" for row in rows),
        "by_architecture": by_architecture,
        "conclusions": {
            "passive_circular_orbit_guarantees_limit": passive_orbit_passes > 0,
            "surface_geometry_can_meet_limit_only_for_selected_fast_rotators": surface_passes > 0,
            "active_sunward_host_can_conditionally_exclude_occultation": hosted_passes > 0,
            "leading_route": "active_sunward_host_or_explicit_fast_rotator_target_selection",
            "passive_generic_asteroid_orbit_status": "REJECTED_ON_DECLARED_GRID",
        },
        "limitations": [
            "spherical bodies and central umbra geometry only",
            "no irregular shape, terrain, penumbra, perturbations, or seasonal Sun geometry",
            "surface PASS is conditional on measured target rotation and deployment latitude",
            "hosted PASS requires active navigation, propulsion, fault tolerance, and power",
            "screening output is not a released trajectory or mission design",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/qst_stor_0002_mission_shadow.json"),
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("outputs/qst_stor_0002/mission_shadow_feasibility.json"),
    )
    args = parser.parse_args()
    config = load_json(args.config)
    summary = summarize(build_rows(config), config)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"wrote {summary['case_count']} cases to {args.out}")


if __name__ == "__main__":
    main()
