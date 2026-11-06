"""SNS November Wheel v3: authority is narrow and historical policies remain replayable."""
import json
from pathlib import Path
import pytest
from automation.standing import validate_standing_policy, validate_standing_request
from automation.orchestration import render_bootstrap_prompt
ROOT=Path(__file__).resolve().parents[1]
def load(n): return json.loads((ROOT/"automation/standing"/n).read_text())
def req(role,action,path,worlds=0):
    return {"loop_id":role,"action":action,"scope":"research-tooling",
        "acceptance_slice":"Accepted in-scope scientific diagnostics","paths":[path],
        "budgets":{"worlds":worlds,"records":0,"runtime_s":0,"disk_mb":1},
        "transaction_count":1,"evidence_refs":["accepted quest and cited source"]}
def test_v3_preserves_safety_and_historical_v2():
    old=load("2026-11.v2.json"); new=load("2026-11.v3.json")
    validate_standing_policy(old);validate_standing_policy(new)
    assert new["authority"]=="explicit-human"
    for field in ("research_scopes","budget_caps","required_checks","expires_at"):
        assert new[field]==old[field]
    for role in ("daily-research-operator","post-game-research","monthly-governance"):
        assert new["roles"][role]==old["roles"][role]
    assert load("current.json")=={"path":"automation/standing/2026-11.v3.json"}
def test_weekly_literature_not_quest_activation():
    old=load("2026-11.v2.json");new=load("2026-11.v3.json")
    r=req("weekly-evidence-synthesis","literature","calendar/evidence/nov-source.json")
    validate_standing_request(new,r,now="2026-11-08T17:00:00Z")
    with pytest.raises(ValueError,match="outside role authority"):
        validate_standing_request(old,r,now="2026-11-08T17:00:00Z")
    for action in ("activate","terminalize"):
        with pytest.raises(ValueError,match="outside role authority"):
            validate_standing_request(new,req("weekly-evidence-synthesis",action,"quests/active/new.md"),now="2026-11-08T17:00:00Z")
def test_pre_game_only_non_generating_docs_tests():
    old=load("2026-11.v2.json");new=load("2026-11.v3.json")
    r=req("daily-governance-triage","implement","docs/research/eligibility.md")
    validate_standing_request(new,r,now="2026-11-07T13:00:00Z")
    with pytest.raises(ValueError,match="outside role authority"):
        validate_standing_request(old,r,now="2026-11-07T13:00:00Z")
    with pytest.raises(ValueError,match="cannot generate worlds"):
        validate_standing_request(new,req("daily-governance-triage","implement","docs/research/probe.md",worlds=1),now="2026-11-07T13:00:00Z")
    for path in ("src/agents/sns_agent.py","experiments/sim2_rotation_policy_comparison.py","tests/test_automation_standing_authority.py"):
        with pytest.raises(ValueError):
            validate_standing_request(new,req("daily-governance-triage","implement",path),now="2026-11-07T13:00:00Z")
def test_program_map_levels_dual_confidence_and_source_freshness():
    txt=(ROOT/"docs/research/SNS_RESEARCH_WHEEL_V3.md").read_text().lower()
    for term in ("materials science and structural design","energy absorption and conversion",
        "energy storage and transmission","communication and control systems",
        "propulsion and orbit maintenance","advanced manufacturing techniques",
        "operational workflow and safety","simulation and testing",
        "[formula]","[mechanism]","[implementation]","external confidence","internal confidence",
        "fifth world","sealed holdout"):
        assert term in txt
    for role in ("daily-governance-triage","daily-research-operator","post-game-research","weekly-evidence-synthesis"):
        prompt=render_bootstrap_prompt(role)
        assert "SNS_RESEARCH_WHEEL_V3.md" in prompt
        assert "CURRENT_MAIN_SHA" in prompt
