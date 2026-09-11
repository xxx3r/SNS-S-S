"""Focused tests for the fixed QST-SIM-0003 eclipse/beam sweep."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from experiments.sim3_eclipse_beam_sweep import load_and_run, run_sweep


CONFIG_PATH = Path("configs/qst_sim_0003_eclipse_beam_sweep.json")
OUTPUT_PATH = Path("outputs/qst_sim_0003/eclipse_beam_sweep.json")


def _spec() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def test_committed_sweep_is_reproducible() -> None:
    expected = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
    assert load_and_run(CONFIG_PATH) == expected


def test_sweep_uses_only_the_fixed_cartesian_grid_and_fixture() -> None:
    payload = load_and_run(CONFIG_PATH)
    coordinates = [
        (case["eclipse_fraction"], case["beam_efficiency"])
        for case in payload["cases"]
    ]

    assert payload["case_count"] == 4
    assert coordinates == [(0.05, 0.6), (0.05, 0.8), (0.1, 0.6), (0.1, 0.8)]
    assert {case["storage_node_fraction"] for case in payload["cases"]} == {0.2}
    assert payload["arm"]["arm_id"] == "fixed_coordinated_storage_mix"
    assert payload["fixture"]["duration"] == 21600.0


def test_sweep_reports_energy_survival_curtailment_and_coverage() -> None:
    payload = load_and_run(CONFIG_PATH)

    for case in payload["cases"]:
        metrics = case["metrics"]
        assert metrics["E_host"] == metrics["delivered_total_Wh"]
        assert metrics["dead_agent_count"] >= 0
        assert metrics["curtailed_total_Wh"] >= 0.0
        assert 0.0 <= metrics["coverage_fraction"] <= 1.0
        assert metrics["role_counts"] == {
            "scout": 4,
            "sensor": 2,
            "relay": 2,
            "storage": 2,
        }

    for row in payload["observed_differences"]["beam_efficiency_0.80_minus_0.60"]:
        assert row["metric_deltas"] == {
            "delivered_total_Wh": 0.0925,
            "curtailed_total_Wh": 0.0,
            "dead_agent_count": 0,
            "coverage_fraction": 0.0,
        }

    for row in payload["observed_differences"]["eclipse_fraction_0.10_minus_0.05"]:
        assert row["metric_deltas"] == {
            "delivered_total_Wh": 0.0,
            "curtailed_total_Wh": -708.319947017,
            "dead_agent_count": 0,
            "coverage_fraction": 0.0,
        }


@pytest.mark.parametrize(
    ("field", "values"),
    [
        ("eclipse_fraction", [0.05, 0.1, 0.2]),
        ("beam_efficiency", [0.6, 0.7]),
    ],
)
def test_sweep_rejects_grid_substitution_or_expansion(field: str, values: list[float]) -> None:
    spec = _spec()
    spec["grid"][field] = values

    with pytest.raises(ValueError, match=field):
        run_sweep(spec)


def test_sweep_rejects_role_mix_changes() -> None:
    spec = _spec()
    spec["arm"]["agent_roles"][4] = "scout"

    with pytest.raises(ValueError, match="20% storage-node"):
        run_sweep(spec)
