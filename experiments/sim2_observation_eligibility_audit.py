"""Non-generating source audit for the accepted QST-SIM-0002 metric.

This module inspects committed source and result bytes. It deliberately does
not instantiate Simulation or execute the consumed four-case matrix.
"""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
from typing import Any


SCHEMA = "sns.qst-sim-0002.observation-eligibility-audit.v1"
QUEST_ID = "QST-SIM-0002"
SOURCE_PATHS = {
    "protocol": "configs/qst_sim_0002_rotation_policy_comparison.json",
    "experiment": "experiments/sim2_rotation_policy_comparison.py",
    "policies": "src/agents/policies.py",
    "agent": "src/agents/sns_agent.py",
    "world": "src/world/asteroid_world.py",
    "accepted_result": "outputs/qst_sim_0002/rotation_policy_comparison.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _function(tree: ast.AST, name: str) -> ast.FunctionDef:
    matches = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == name]
    if len(matches) != 1:
        raise ValueError(f"expected exactly one function named {name}")
    return matches[0]


def _credit_gate(experiment_source: str) -> dict[str, Any]:
    run_case = _function(ast.parse(experiment_source), "run_case")
    candidates: list[ast.If] = []
    for node in ast.walk(run_case):
        if not isinstance(node, ast.If):
            continue
        if any(
            isinstance(child, ast.Call)
            and isinstance(child.func, ast.Attribute)
            and child.func.attr == "append"
            and isinstance(child.func.value, ast.Name)
            and child.func.value.id == "observations"
            for child in ast.walk(node)
        ):
            candidates.append(node)
    if len(candidates) != 1:
        raise ValueError("expected exactly one observation-credit gate")
    gate = candidates[0]
    credited_roles = sorted(
        {
            node.attr.lower()
            for node in ast.walk(gate.test)
            if isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == "AgentRole"
        }
    )
    references_mode = any(
        (isinstance(node, ast.Attribute) and node.attr == "mode")
        or (isinstance(node, ast.Name) and node.id == "mode")
        for node in ast.walk(gate.test)
    )
    return {
        "predicate": ast.unparse(gate.test),
        "credited_roles": credited_roles,
        "checks_operating_mode": references_mode,
    }


def _returned_modes(policy_source: str, class_name: str) -> list[str]:
    tree = ast.parse(policy_source)
    classes = [node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == class_name]
    if len(classes) != 1:
        raise ValueError(f"expected exactly one policy class named {class_name}")
    decide = _function(classes[0], "decide")
    return sorted(
        {
            node.attr
            for node in ast.walk(decide)
            if isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == "AgentMode"
        }
    )


def _region_inputs(world_source: str) -> dict[str, Any]:
    region = _function(ast.parse(world_source), "region_id")
    return {
        "parameters": [arg.arg for arg in region.args.args if arg.arg != "self"],
        "directly_references_rotation_rate": any(
            isinstance(node, ast.Attribute) and node.attr == "rotation_rate"
            for node in ast.walk(region)
        ),
    }


def audit_repository(root: str | Path, *, accepted_source_commit: str) -> dict[str, Any]:
    """Return a deterministic audit of the frozen metric without simulation."""
    base = Path(root)
    source_files = {name: base / path for name, path in SOURCE_PATHS.items()}
    for path in source_files.values():
        if not path.is_file():
            raise ValueError(f"missing audit source: {path.relative_to(base)}")

    protocol = json.loads(source_files["protocol"].read_text(encoding="utf-8"))
    accepted = json.loads(source_files["accepted_result"].read_text(encoding="utf-8"))
    if protocol.get("quest_id") != QUEST_ID or accepted.get("quest_id") != QUEST_ID:
        raise ValueError("unexpected SIM2 source identity")
    if accepted.get("world_count") != 4 or accepted.get("agent_step_records") != 2880:
        raise ValueError("accepted SIM2 result identity changed")

    gate = _credit_gate(source_files["experiment"].read_text(encoding="utf-8"))
    policy_source = source_files["policies"].read_text(encoding="utf-8")
    region = _region_inputs(source_files["world"].read_text(encoding="utf-8"))
    case_keys = set().union(*(case.keys() for case in accepted["cases"]))
    event_fields = sorted(key for key in case_keys if "event" in key or "observation" in key or "trace" in key)

    return {
        "schema": SCHEMA,
        "quest_id": QUEST_ID,
        "accepted_source_commit": accepted_source_commit,
        "synthetic": True,
        "generation": {"worlds": 0, "records": 0},
        "source_sha256": {name: _sha256(path) for name, path in sorted(source_files.items())},
        "declared_observation_rule": protocol["observation_rule"],
        "implemented_credit_gate": gate,
        "policy_modes_reachable_by_source": {
            "baseline": _returned_modes(policy_source, "BaselinePolicy"),
            "survey": _returned_modes(policy_source, "CoordinatedPolicy"),
        },
        "region_identity": region,
        "accepted_result_event_fields": event_fields,
        "findings": {
            "role_only_credit_confirmed": gate["credited_roles"] == ["scout", "sensor"]
            and not gate["checks_operating_mode"],
            "operational_sensing_eligibility_demonstrated": False,
            "rotation_directly_changes_region_identity": region["directly_references_rotation_rate"],
            "event_level_occupancy_recoverable_from_accepted_result": bool(event_fields),
        },
        "confidence": {
            "internal": {
                "direction": "up",
                "claim": "The accepted synthetic metric credits every scout/sensor step by role and does not test operating mode.",
            },
            "external": {
                "direction": "unknown",
                "claim": "No external sensing-performance or hardware-validity source is evaluated by this internal code audit.",
            },
        },
        "interpretation": (
            "The +10 fresh-bin-minute aggregate remains valid for the prospectively declared role-only synthetic metric, "
            "but it does not demonstrate operational sensing eligibility. Body rotation changes illumination and policy "
            "conditions, while region identity is computed directly from agent theta. The committed aggregate contains no "
            "event trace, so equal endpoint deltas cannot distinguish identical occupancy from summary information loss."
        ),
        "smallest_next_test": (
            "Prospectively freeze event telemetry containing timestamp, role, operating mode, sampled region and an explicit "
            "sensing-eligibility predicate before any future non-repeated SIM2 comparison."
        ),
        "claim_boundary": (
            "Source-semantics audit only; no fifth world, accepted-output rewrite, frozen-evaluator change, physical sensing "
            "claim, mission-value threshold or asteroid-performance conclusion."
        ),
    }


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    output = root / "outputs/qst_sim_0002/observation_eligibility_audit.json"
    result = audit_repository(root, accepted_source_commit="bf51c46d39d3e7318fdeafe1f6ed020a4a45a92c")
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "worlds": 0, "records": 0}, sort_keys=True))


if __name__ == "__main__":
    main()
