"""Focused reproduction tests for the bounded SIM3 role-mix comparison."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from experiments.sim3_role_mix_comparison import load_and_run, run_comparison


CONFIG_PATH = Path("configs/qst_sim_0003_role_mix.json")
OUTPUT_PATH = Path("outputs/qst_sim_0003/role_mix_comparison.json")


def test_committed_role_mix_output_is_reproducible() -> None:
    expected = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
    assert load_and_run(CONFIG_PATH) == expected


def test_comparison_uses_exactly_two_declared_fixed_arms() -> None:
    payload = load_and_run(CONFIG_PATH)
    baseline, coordinated = payload["arms"]

    assert baseline["arm_id"] == "all_independent"
    assert baseline["policy"] == "baseline"
    assert set(baseline["agent_roles"]) == {"scout"}
    assert baseline["storage_node_fraction"] == 0.0

    assert coordinated["arm_id"] == "fixed_coordinated_storage_mix"
    assert coordinated["policy"] == "coordinated"
    assert coordinated["storage_node_fraction"] == 0.2
    assert coordinated["metrics"]["role_counts"] == {
        "scout": 4,
        "sensor": 2,
        "relay": 2,
        "storage": 2,
    }


def test_bounded_result_preserves_energy_survival_and_coverage_accounting() -> None:
    payload = load_and_run(CONFIG_PATH)
    baseline, coordinated = payload["arms"]

    for arm in (baseline, coordinated):
        metrics = arm["metrics"]
        assert metrics["dead_agent_count"] == 0
        assert metrics["coverage_fraction"] == 1.0
        assert metrics["E_host"] == metrics["delivered_total_Wh"]
        assert metrics["harvested_total_Wh"] >= metrics["delivered_total_Wh"]
        assert metrics["curtailed_total_Wh"] >= 0.0

    assert baseline["metrics"]["delivered_total_Wh"] == 0.0
    assert coordinated["metrics"]["delivered_total_Wh"] == 0.2775
    assert payload["observation"] == "COORDINATED_HOST_DELIVERY_OBSERVED_ON_DECLARED_FIXTURE"


def test_comparison_fails_closed_outside_two_arm_budget() -> None:
    spec = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))

    with pytest.raises(ValueError, match="exactly two"):
        run_comparison({**spec, "arms": spec["arms"][:1]})
    with pytest.raises(ValueError, match="unique"):
        run_comparison({**spec, "arms": [spec["arms"][0], spec["arms"][0]]})

