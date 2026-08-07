from __future__ import annotations

import json
from pathlib import Path

from automation.state import validate_repository_state

CONTRACT = """---
schema: sns.loop-contract.v1
loop_id: {loop}
contract_version: 1.0.0
status: active
owner: SNS-S-S
allowed_triggers:
  - scheduled
  - explicit-human
reads:
  - AGENTS.md
writes:
  - automation/runs/**
terminal_states:
  - DONE
  - BLOCKED_CONFLICT
  - VERIFICATION_FAILED
retry_budget: 1
---
# Contract
"""


def test_repository_validator_enforces_cross_queue_uniqueness(tmp_path: Path) -> None:
    contract_dir = tmp_path / "automation/contracts"
    contract_dir.mkdir(parents=True)
    for loop in (
        "daily-governance-triage",
        "daily-research-operator",
        "weekly-evidence-synthesis",
        "monthly-governance",
        "system-audit",
    ):
        (contract_dir / f"{loop}.v1.md").write_text(CONTRACT.format(loop=loop), encoding="utf-8")
    matrix = {
        "schema": "sns.state-ownership.v1",
        "surfaces": [{
            "path": "quests/active/**", "authority": "monthly-governance",
            "triage": "read", "daily": "read", "weekly": "propose", "monthly": "write", "audit": "observe",
            "reconciliation": "Monthly governance is authoritative."
        }],
    }
    (tmp_path / "automation/state_ownership.json").write_text(json.dumps(matrix), encoding="utf-8")
    for queue in ("active", "completed", "proposed", "blocked"):
        (tmp_path / f"quests/{queue}").mkdir(parents=True)
    (tmp_path / "quests/active/QST-STOR-0002-a.md").write_text("# QST-STOR-0002", encoding="utf-8")
    (tmp_path / "quests/completed/QST-STOR-0002-b.md").write_text("# QST-STOR-0002", encoding="utf-8")
    report = validate_repository_state(tmp_path, strict=False)
    assert not report["valid"]
    assert any("multiple queues" in error for error in report["errors"])
