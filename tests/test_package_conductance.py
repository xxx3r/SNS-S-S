from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from experiments.package_conductance_budget import run_package_conductance_budget  # noqa: E402
from src.sim.package_conductance import (  # noqa: E402
    ConductivePath,
    PackageConductanceBudget,
    evaluate_package_budget,
)


def test_path_uses_k_a_over_l_and_repetition():
    path = ConductivePath(
        name="wire",
        category="wiring",
        count=2,
        thermal_conductivity_W_m_K=100.0,
        cross_section_area_m2=1e-10,
        length_m=0.002,
    )
    assert path.single_path_conductance_W_K == pytest.approx(5e-6)
    assert path.total_conductance_W_K == pytest.approx(1e-5)


def test_uncertainty_multiplier_controls_gate():
    path = ConductivePath("support", "supports", 1, 1.0, 1e-8, 1e-3)
    nominal = PackageConductanceBudget("nominal", 1.1e-5, (path,), 1.0)
    conservative = PackageConductanceBudget("conservative", 1.1e-5, (path,), 1.5)
    assert evaluate_package_budget(nominal)["status"] == "PASS"
    assert evaluate_package_budget(conservative)["status"] == "FAIL"


def test_declared_package_fails_target_and_identifies_adhesive(tmp_path):
    config = ROOT / "configs" / "qst_stor_0002_package_conductance.json"
    result = run_package_conductance_budget(config, tmp_path)

    assert result["status"] == "FAIL"
    assert result["dominant_path"] == "core_to_shell_adhesive_bonds"
    assert result["nominal_total_conductance_W_K"] == pytest.approx(1.1305e-4)
    assert result["conservative_total_conductance_W_K"] == pytest.approx(1.69575e-4)
    assert result["conservative_total_conductance_W_K"] > 3 * result[
        "target_parasitic_conductance_W_K"
    ]
    assert (tmp_path / "package_conductance_summary.json").exists()
    assert (tmp_path / "package_conductance_paths.csv").exists()
    payload = json.loads((tmp_path / "package_conductance_summary.json").read_text())
    assert payload["category_totals_W_K"]["adhesives"] == pytest.approx(6e-5)
