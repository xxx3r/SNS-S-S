"""Human-authorized Post-Game role must preserve historical authority and prevent overreach."""
import json
from pathlib import Path
import pytest
from automation.contracts import ContractRegistry
from automation.orchestration import validate_runtime_manifest, render_bootstrap_prompt
from automation.standing import validate_standing_policy, validate_standing_request
from automation.state import validate_ownership_matrix
ROOT = Path(__file__).resolve().parents[1]

def load(path):
    return json.loads((ROOT / path).read_text())

def request(action="implement", path="docs/research/postgame_appraisal.md"):
    return dict(loop_id="post-game-research", action=action, scope="research-tooling",
                acceptance_slice="Independent accepted-quest measurement appraisal",
                paths=[path], budgets=dict(worlds=0, records=0, runtime_s=0, disk_mb=1),
                transaction_count=1, evidence_refs=["SIM3 accepted PR134"])

def test_postgame_contract_runtime_and_slot_order():
    registry=ContractRegistry.from_directory(ROOT / "automation/contracts")
    assert registry.active("post-game-research").contract_version=="2.0.0"
    assert "CURRENT_MAIN_SHA" in render_bootstrap_prompt("post-game-research")
    manifest=load("automation/runtime_manifest.json")
    validate_runtime_manifest(manifest)
    rows={r["loop_id"]:r for r in manifest["loops"]}
    assert rows["daily-governance-triage"]["order"] < rows["daily-research-operator"]["order"] < rows["post-game-research"]["order"]
    assert rows["post-game-research"]["order"] < rows["weekly-evidence-synthesis"]["order"]
    assert sum(bool(r["desired_enabled"]) for r in manifest["loops"] if r["scheduler_managed"]) == 5

def test_postgame_is_a_new_policy_only():
    old=load("automation/standing/2026-10.v1.json")
    continuity=load("automation/standing/2026-11.v1.json")
    trio=load("automation/standing/2026-11.v2.json")
    for policy in (old, continuity, trio):
        validate_standing_policy(policy)
    for field in ("research_scopes","budget_caps","required_checks"):
        assert trio[field] == continuity[field]
    for role in continuity["roles"]:
        assert trio["roles"][role] == continuity["roles"][role]
    assert set(trio["roles"]) == set(continuity["roles"]) | {"post-game-research"}
    assert load("automation/standing/current.json") == {"path":"automation/standing/2026-11.v2.json"}
    validate_standing_request(trio,request(),now="2026-11-02T23:00:00Z")
    with pytest.raises(ValueError,match="unknown standing role"):
        validate_standing_request(continuity,request(),now="2026-11-02T23:00:00Z")

@pytest.mark.parametrize("action,path",[
    ("activate","quests/proposed/QST-NEW-0001.md"),
    ("govern","automation/standing/current.json"),
    ("implement","AGENTS.md"),
    ("implement","automation/contracts/post-game-research.v2.md"),
    ("implement","tests/test_automation_standing_authority.py"),
    ("route","quests/active/README.md"),
])
def test_postgame_rejects_unauthorized_actions(action,path):
    with pytest.raises(ValueError):
        validate_standing_request(load("automation/standing/2026-11.v2.json"),request(action,path),now="2026-11-02T23:00:00Z")

def test_postgame_ownership_is_explicit_and_readonly_on_controls():
    matrix=load("automation/state_ownership.json")
    validate_ownership_matrix(matrix)
    assert all(row.get("postgame") in ("read","write","propose","observe","none") for row in matrix["surfaces"])
    protected={"automation/contracts/**","automation/schemas/**","automation/prompts/**","automation/standing/**","automation/runtime_manifest.json"}
    assert all(row["postgame"]=="read" for row in matrix["surfaces"] if row["path"] in protected)
