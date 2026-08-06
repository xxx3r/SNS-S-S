"""Check that the versioned allocation config reproduces the accepted ledger inputs."""
from __future__ import annotations

import json
from pathlib import Path

from experiments.mission_dependency_ledger import build_cases


CONFIG_PATH = Path("configs/qst_stor_0002/mission_dependency_allocations.v1.json")
FIELDS = (
    "name",
    "architecture",
    "node_mass_kg",
    "deployment_mass_kg",
    "navigation_mass_kg",
    "stationkeeping_mass_kg",
    "resilience_mass_kg",
    "host_service_mass_kg",
    "node_power_W",
    "navigation_power_W",
    "stationkeeping_power_W",
    "host_service_power_W",
    "target_rotation_period_h",
    "rotation_limit_h",
)


def load_config_cases(path: Path = CONFIG_PATH) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != "sns.qst-stor-0002.mission-dependency-allocations.v1":
        raise ValueError("unsupported allocation schema")
    if len(payload.get("cases", [])) != 2:
        raise ValueError("expected exactly two allocation cases")
    return payload["cases"]


def _accepted_fields(case: object) -> dict[str, object]:
    """Expose the raw accepted inputs instead of derived to_dict fields."""
    return {field: getattr(case, field) for field in FIELDS}


def build_check() -> dict:
    configured = load_config_cases()
    accepted = build_cases()
    mismatches = []
    for configured_case, accepted_case in zip(configured, accepted, strict=True):
        accepted_fields = _accepted_fields(accepted_case)
        for field in FIELDS:
            if configured_case[field] != accepted_fields[field]:
                mismatches.append(
                    {
                        "case": configured_case["name"],
                        "field": field,
                        "configured": configured_case[field],
                        "accepted": accepted_fields[field],
                    }
                )
    return {
        "schema": "sns.qst-stor-0002.mission-dependency-config-check.v1",
        "allocation_config": str(CONFIG_PATH),
        "matches_accepted_inputs": not mismatches,
        "mismatches": mismatches,
        "limitation": "The accepted experiment still owns loading until governance authorizes replacing its embedded defaults.",
    }


if __name__ == "__main__":
    print(json.dumps(build_check(), indent=2))
