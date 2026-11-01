"""Protocol-freeze tests for the QST-SIM-0002 comparison."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from experiments.sim2_rotation_policy_comparison import load_protocol


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "configs/qst_sim_0002_rotation_policy_comparison.json"


def test_protocol_freezes_exact_four_case_matrix_without_execution() -> None:
    output_root = ROOT / "outputs"
    before = {path.relative_to(ROOT) for path in output_root.rglob("*")}
    protocol = load_protocol(PROTOCOL)
    after = {path.relative_to(ROOT) for path in output_root.rglob("*")}
    assert protocol["comparison"] == {
        "policies": ["baseline", "survey"],
        "rotation_periods_s": [7200.0, 43200.0],
    }
    assert protocol["budgets"]["max_worlds"] == 4
    assert protocol["budgets"]["max_agent_step_records"] == 2880
    assert after == before


@pytest.mark.parametrize(
    ("path", "value", "message"),
    [
        (("comparison", "policies"), ["baseline", "survey", "optimized"], "exactly baseline and survey"),
        (("comparison", "rotation_periods_s"), [7200.0], "exactly the declared rotation regimes"),
        (("budgets", "max_worlds"), 5, "budgets do not match"),
        (("primary_endpoint",), "final_fresh_coverage_fraction", "primary endpoint changed"),
        (("common_fixture", "solar_flux_W_m2"), 900.0, "scientifically active frozen fixture"),
        (("common_fixture", "host_demand_rate_Wh_per_h"), 1.0, "scientifically active frozen fixture"),
        (("common_fixture", "agent_parameters", "move_rate"), 0.0, "scientifically active frozen fixture"),
    ],
)
def test_protocol_rejects_post_freeze_widening(tmp_path: Path, path: tuple[str, ...], value: object, message: str) -> None:
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    target = protocol
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    candidate = tmp_path / "candidate.json"
    candidate.write_text(json.dumps(protocol), encoding="utf-8")
    with pytest.raises(ValueError, match=message):
        load_protocol(candidate)
