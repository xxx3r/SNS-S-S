"""November continuity must preserve October research authority exactly."""
import json
from pathlib import Path
from automation.standing import validate_standing_policy, validate_standing_request

ROOT = Path(__file__).resolve().parents[1]

def test_november_policy_is_strict_continuity():
    old = json.loads((ROOT / "automation/standing/2026-10.v1.json").read_text())
    new = json.loads((ROOT / "automation/standing/2026-11.v1.json").read_text())
    validate_standing_policy(new)
    assert new["authority"] == "explicit-human"
    assert new["expires_at"] == "2026-12-01T07:00:00Z"
    for field in ("research_scopes", "roles", "budget_caps", "required_checks"):
        assert new[field] == old[field], field
    assert json.loads((ROOT / "automation/standing/current.json").read_text()) == {"path": "automation/standing/2026-11.v1.json"}

def test_november_standing_execution_requires_valid_time():
    policy = json.loads((ROOT / "automation/standing/2026-11.v1.json").read_text())
    req = {"loop_id": "daily-research-operator", "action": "implement", "scope": "swarm-power",
           "acceptance_slice": "Independently accepted SIM2 measurement", "paths": ["experiments/sim2_probe.py"],
           "budgets": {"worlds": 0, "records": 0, "runtime_s": 0, "disk_mb": 1},
           "transaction_count": 1, "evidence_refs": ["Active SIM2 accepted scope"]}
    validate_standing_request(policy, req, now="2026-11-02T19:00:00Z")
    import pytest
    with pytest.raises(ValueError, match="not current"):
        validate_standing_request(policy, req, now="2026-12-01T07:00:00Z")
