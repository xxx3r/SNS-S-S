"""Focused tests for the bounded SIM3 receiver-availability diagnostic."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from experiments.sim3_receiver_availability import load_and_run, run_diagnostic


CONFIG_PATH = Path("configs/qst_sim_0003_receiver_availability.json")
OUTPUT_PATH = Path("outputs/qst_sim_0003/receiver_availability.json")
BASELINE_PATH = Path("outputs/qst_sim_0003/eclipse_beam_sweep.json")


def _spec() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def test_committed_diagnostic_is_reproducible() -> None:
    assert load_and_run(CONFIG_PATH) == json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))


def test_only_two_new_visibility_cases_are_generated() -> None:
    payload = load_and_run(CONFIG_PATH)
    assert payload["case_count"] == 2
    assert payload["new_world_count"] == 2
    assert payload["baseline_worlds_rerun"] == 0
    assert [case["eclipse_fraction"] for case in payload["cases"]] == [0.05, 0.1]
    assert {case["beam_efficiency"] for case in payload["cases"]} == {0.8}
    assert {
        case["diagnostic_receiver_visibility_fraction"] for case in payload["cases"]
    } == {1.0}


def test_report_is_limited_to_routed_metrics() -> None:
    required = {
        "delivered_total_Wh",
        "curtailed_total_Wh",
        "dead_agent_count",
        "coverage_fraction",
    }
    for case in load_and_run(CONFIG_PATH)["cases"]:
        assert set(case["baseline_metrics"]) == required
        assert set(case["diagnostic_metrics"]) == required
        assert set(case["metric_deltas"]) == required


def test_baseline_bytes_are_immutable_input_not_regenerated() -> None:
    baseline_before = BASELINE_PATH.read_bytes()
    load_and_run(CONFIG_PATH)
    assert BASELINE_PATH.read_bytes() == baseline_before


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("eclipse_fraction", [0.05, 0.1, 0.2]),
        ("beam_efficiency", 0.7),
        ("baseline_receiver_visibility_fraction", 0.5),
        ("diagnostic_receiver_visibility_fraction", 0.75),
    ],
)
def test_grid_substitution_or_expansion_fails_closed(field: str, value: object) -> None:
    spec = _spec()
    spec["grid"][field] = value
    with pytest.raises(ValueError):
        run_diagnostic(spec, BASELINE_PATH.read_bytes())


def test_fixture_substitution_fails_closed() -> None:
    spec = _spec()
    spec["fixture"]["host_demand_rate"] = 0.1
    with pytest.raises(ValueError, match="accepted binding"):
        run_diagnostic(spec, BASELINE_PATH.read_bytes())


def test_baseline_substitution_fails_closed() -> None:
    with pytest.raises(ValueError, match="baseline artifact hash"):
        run_diagnostic(_spec(), BASELINE_PATH.read_bytes() + b"\n")


def test_result_does_not_invent_a_materiality_threshold() -> None:
    payload = load_and_run(CONFIG_PATH)
    assert payload["materiality_classification"] == "NOT_DEFINED_BY_ACCEPTED_ROUTE"
    assert "materiality_rule" not in payload
