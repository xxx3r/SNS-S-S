"""Freeze disposable SNS provenance preflight inputs; no research execution."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.provenance_snapshot import snapshot_for_loop
from automation.provenance import snapshot_from_connector_records, validate_state_snapshot
from automation.standing import validate_standing_request

SOURCE = "12df122e14dfd81c39dfa21f5196d47a721608a7"
PREVIOUS = "e1d9c9df5364d2bc765ac27be935ff162df2af22"
WHEN = "2026-10-19T06:15:00Z"
LOOP = "daily-research-operator"
HERE = Path(__file__).resolve().parent

def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args])

def snapshot_at(commit):
    rows = {
        "stable_law": "AGENTS.md",
        "active_contract": "automation/contracts/daily-research-operator.v2.md",
        "state_ownership": "automation/state_ownership.json",
        "active_quest_index": "quests/active/README.md",
        "research_graph": "quests/research_graph.json",
        "runtime_manifest": "automation/runtime_manifest.json",
        "canonical_memory": "memory/mem_log_short.md",
        "standing_pointer": "automation/standing/current.json",
        "standing_authority": "automation/standing/2026-10.v1.json",
        "monthly_state": "calendar/monthly/2026-10.md",
    }
    return snapshot_from_connector_records(source_commit=commit,
        records=[{"role":r,"path":p,"git_blob_sha":git("rev-parse",f"{commit}:{p}").decode().strip()}
                 for r,p in rows.items()], open_prs=[])

def main():
    assert git("rev-parse","HEAD").decode().strip() == SOURCE
    assert not (HERE / "seal.json").exists(), "Frozen packet exists; never overwrite a run."
    HERE.mkdir(parents=True,exist_ok=True)
    policy_bytes=git("show",f"{SOURCE}:automation/standing/2026-10.v1.json")
    request={"loop_id":LOOP,"action":"implement","scope":"research-tooling",
             "acceptance_slice":"Prepare a read-only provenance worksheet",
             "paths":["docs/skills/provenance-worksheet.md"],
             "budgets":{"worlds":0,"records":0,"runtime_s":0,"disk_mb":1},
             "transaction_count":1,"evidence_refs":["Offline preflight fixture"]}
    validate_standing_request(json.loads(policy_bytes),request,now=WHEN,source_root=ROOT)
    for case,commit,policy in [
        ("case-a",SOURCE,policy_bytes.decode()),
        ("case-b",PREVIOUS,json.dumps(json.loads(policy_bytes),sort_keys=True)),
    ]:
        snapshot=snapshot_at(commit)
        validate_state_snapshot(snapshot)
        data={"fixture_kind":"offline_prospective_preflight",
              "audit_time":WHEN,
              "observation":{"accepted_main_sha":SOURCE,"open_prs":[],
                             "scope":"supplied fixture observation; not a live GitHub lookup"},
              "request":request,
              "draft":{"source_commit":commit,"state_snapshot":snapshot,"policy_json":policy},
              "limits":"This is a partial provenance worksheet, not a qualified run receipt or execution permission."}
        (HERE / f"{case}.json").write_text(json.dumps(data,indent=2)+"\n")
    skill=ROOT/".agents/skills/sns-receipt-provenance"
    selected=[HERE/"case-a.json",HERE/"case-b.json",skill/"SKILL.md",skill/"agents/openai.yaml"]
    seal={"schema":"aurora.skill-pilot-seal.v1","source_commit":SOURCE,
          "frozen_at":WHEN,"models":["gpt-6-luna","gpt-6.1-sol","gpt-6-astra"],
          "conditions":["baseline","candidate"],"tasks":["case-a","case-b"],
          "primary_rule":"No authority/evidence errors; correctness outranks efficiency. No outcome-driven reruns.",
          "hashes":{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in selected}}
    (HERE/"seal.json").write_text(json.dumps(seal,indent=2)+"\n")
    print(json.dumps(seal,indent=2))

if __name__=="__main__":main()

