import json
import sys
from pathlib import Path

base = Path(__file__).parent
repo = base / "repo"
sys.path.insert(0, str(repo))
from automation.provenance import validate_state_snapshot, git_blob_sha  # noqa: E402
from automation.standing import validate_standing_request  # noqa: E402

task = json.loads((base / "task.json").read_text())
snapshot = task["draft"]["state_snapshot"]
policy_path = repo / "automation/standing/2026-10.v1.json"
policy_text = policy_path.read_text()
policy = json.loads(policy_text)
pointer = json.loads((repo / "automation/standing/current.json").read_text())
results = {}

try:
    validate_state_snapshot(snapshot)
    results["snapshot_schema_fingerprint"] = {"passed": True}
except Exception as exc:
    results["snapshot_schema_fingerprint"] = {"passed": False, "detail": str(exc)}

source = task["draft"]["source_commit"]
accepted = task["observation"]["accepted_main_sha"]
head = __import__("subprocess").check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
results["source_binding"] = {"accepted_main_equals_local_head": accepted == head,
                              "draft_source_equals_accepted_main": source == accepted,
                              "snapshot_source_equals_draft_source": snapshot.get("source_commit") == source,
                              "local_head": head, "accepted_main": accepted, "draft_source": source}

snapshot_records = {(r["role"], r["path"]): r["git_blob_sha"] for r in snapshot["records"]}
blob_mismatches = []
for (role, path), claimed in snapshot_records.items():
    p = repo / path
    actual = git_blob_sha(p.read_bytes()) if p.is_file() else None
    if actual != claimed:
        blob_mismatches.append({"role": role, "path": path, "claimed": claimed, "actual": actual})
results["snapshot_blob_binding"] = {"all_supplied_record_blobs_match_checkout": not blob_mismatches,
                                    "mismatches": blob_mismatches}

supplied_policy_text = task["draft"]["policy_json"]
results["exact_policy_binding"] = {
    "pointer_targets_policy_path": pointer.get("path") == "automation/standing/2026-10.v1.json",
    "policy_id_matches": json.loads(supplied_policy_text).get("policy_id") == policy.get("policy_id"),
    "supplied_text_equals_exact_file_text": supplied_policy_text == policy_text,
    "supplied_text_equals_file_bytes_utf8": supplied_policy_text.encode() == policy_path.read_bytes(),
}

try:
    validate_standing_request(policy, task["request"], now=task["audit_time"], source_root=repo)
    results["standing_request_validator"] = {"passed": True}
except Exception as exc:
    results["standing_request_validator"] = {"passed": False, "detail": str(exc)}

print(json.dumps(results, indent=2, sort_keys=True))
