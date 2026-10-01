"""Bind the assumptions document to accepted bytes; generate no sweep."""

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs/qst_meta_0001/beam_link_sweep.json"
DOCUMENT = ROOT / "docs/system/beam_link_assumptions.md"
ACCEPTED_SHA256 = "ac7f807a3cf7bc0f0882956932de62f04751d17925af829edf3701e82cedbd91"


def test_assumptions_bind_exact_accepted_artifact_bytes():
    assert hashlib.sha256(OUTPUT.read_bytes()).hexdigest() == ACCEPTED_SHA256
    document = DOCUMENT.read_text(encoding="utf-8")
    assert ACCEPTED_SHA256 in document
    assert "outputs/qst_meta_0001/beam_link_sweep.json" in document
    assert "2c34d1835223d1c7f44a1fb6f001bf5f6c8d7ec0" in document


def test_documented_boundary_preserves_accepted_grid_and_negative_result():
    artifact = json.loads(OUTPUT.read_bytes())
    points = artifact["sweep"]["points"]
    useful = {(p["steering_angle_deg"], p["pointing_error_deg"])
              for p in points if p["useful_on_declared_synthetic_boundary"]}
    assert len(points) == artifact["summary"]["point_count"] == 12
    assert useful == {(0, 0), (0, 1), (20, 0), (20, 1)}
    assert len(useful) == artifact["summary"]["useful_point_count"] == 4
    assert artifact["summary"]["limited_point_count"] == 8
    negative = next(p for p in points
                    if (p["steering_angle_deg"], p["pointing_error_deg"]) == (60, 3))
    assert negative["net_delivered_energy_Wh"] == -0.034937533525
    assert negative["net_delivered_fraction"] == artifact["summary"]["minimum_net_delivered_fraction"]
    document = DOCUMENT.read_text(encoding="utf-8")
    for value in ("12 points, 4 useful and 8 limited", "-0.034937533525",
                  artifact["summary"]["outcome"]):
        assert value in document


def test_independent_assumptions_and_nonclaims_remain_explicit():
    document = DOCUMENT.read_text(encoding="utf-8")
    for field in ("Steering physics", "Actuation mechanism", "Fabrication route",
                  "Update energy", "Aperture efficiency", "Environment compatibility"):
        assert f"| {field} |" in document
    for boundary in ("deterministic attenuation", "stochastic-pointing",
                     "Aqueous magnetic locomotion is outside the space baseline",
                     "not a hardware", "retained rather than clipped",
                     "No physical power-beam performance is established",
                     "No metasurface architecture", "No hardware readiness",
                     "safe operating", "SYNTH R2 paused"):
        assert boundary in document
