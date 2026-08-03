"""Generate the matched QST-STOR-0002 mission dependency ledger."""
from __future__ import annotations

import json
from pathlib import Path

from src.sim.mission_dependency import DependencyCase, compare_min_materials


def build_cases() -> tuple[DependencyCase, DependencyCase]:
    surface = DependencyCase(
        name="measured_fast_rotator_surface",
        architecture="fast_rotator_surface",
        node_mass_kg=0.000789,
        deployment_mass_kg=0.002,
        navigation_mass_kg=0.0,
        stationkeeping_mass_kg=0.0,
        resilience_mass_kg=0.0,
        host_service_mass_kg=0.0,
        node_power_W=0.002,
        navigation_power_W=0.0,
        stationkeeping_power_W=0.0,
        host_service_power_W=0.0,
        target_rotation_period_h=0.5,
        rotation_limit_h=0.5,
        assumptions=(
            "target rotation is measured before deployment",
            "two grams are allocated to attachment and release",
            "terrain and latitude do not extend the inherited shadow bound",
        ),
    )
    hosted = DependencyCase(
        name="active_sunward_hosted",
        architecture="active_sunward_hosted",
        node_mass_kg=0.000789,
        deployment_mass_kg=0.002,
        navigation_mass_kg=0.2,
        stationkeeping_mass_kg=0.5,
        resilience_mass_kg=0.2,
        host_service_mass_kg=0.1,
        node_power_W=0.002,
        navigation_power_W=3.0,
        stationkeeping_power_W=5.0,
        host_service_power_W=2.0,
        target_rotation_period_h=None,
        rotation_limit_h=0.5,
        assumptions=(
            "supporting allocations are screening values",
            "the host maintains the required geometry",
            "failure probability and illuminated-state rejection are outside scope",
        ),
    )
    return surface, hosted


def build_artifact() -> dict:
    surface, hosted = build_cases()
    return {
        "schema": "sns.qst-stor-0002.mission-dependency-ledger.v1",
        "cases": [surface.to_dict(), hosted.to_dict()],
        "comparison": compare_min_materials(surface, hosted),
        "limitations": [
            "Values are explicit screening allocations, not a released design.",
            "Target scarcity and survey cost are not converted into mass.",
            "Irregular geometry, reliability, and illuminated-state heat rejection remain omitted.",
        ],
    }


def main() -> None:
    out = Path("outputs/qst_stor_0002/mission_dependency_ledger.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(build_artifact(), indent=2) + "\n", encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
