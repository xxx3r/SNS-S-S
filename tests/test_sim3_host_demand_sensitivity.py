"""Tests for the bounded QST-SIM-0003 host-demand diagnostic."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from experiments.sim3_host_demand_sensitivity import load_and_run, run_diagnostic


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "qst_sim_0003_host_demand_sensitivity.json"


def test_host_demand_diagnostic_is_bounded_and_preserves_accounting() -> None:
    result = load_and_run(CONFIG, ROOT)

    assert result["new_world_count"] == 2
    assert result["baseline_worlds_rerun"] == 0
    assert result["observation"] == "DELIVERY_DEMAND_INSENSITIVE_ON_DECLARED_FIXTURE"
    assert [case["host_demand_rate_Wh_per_h"] for case in result["cases"]] == [0.1, 0.4]
    assert result["accepted_baseline"]["host_service_fraction"] == pytest.approx(0.37 / 1.2)

    baseline_delivery = result["accepted_baseline"]["delivered_total_Wh"]
    for case in result["cases"]:
        metrics = case["metrics"]
        assert metrics["host_demand_total_Wh"] == pytest.approx(
            case["host_demand_rate_Wh_per_h"] * 6.0
        )
        assert metrics["host_demand_total_Wh"] == pytest.approx(
            metrics["delivered_total_Wh"] + metrics["unmet_host_demand_Wh"]
        )
        assert metrics["host_service_fraction"] == pytest.approx(
            metrics["delivered_total_Wh"] / metrics["host_demand_total_Wh"]
        )
        assert metrics["delivered_total_Wh"] == pytest.approx(baseline_delivery)
        assert case["delivery_equal_to_baseline_within_tolerance"] is True


def test_host_demand_diagnostic_fails_closed_on_grid_mutation() -> None:
    spec = json.loads(CONFIG.read_text(encoding="utf-8"))
    baseline_bytes = (ROOT / spec["baseline_artifact"]).read_bytes()
    mutated = copy.deepcopy(spec)
    mutated["grid"]["diagnostic_host_demand_rate_Wh_per_h"] = [0.1, 0.3]

    with pytest.raises(ValueError, match="demand grid"):
        run_diagnostic(mutated, baseline_bytes)
