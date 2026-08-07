from pathlib import Path

import pytest

from automation.contracts import ContractRegistry, parse_contract


def contract_text(loop_id: str, *, status: str = "active") -> str:
    return f"""---
schema: sns.loop-contract.v1
loop_id: {loop_id}
contract_version: 1.0.0
status: {status}
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
  - DONE_WITH_LIMITATIONS
  - BLOCKED_CONFLICT
  - VERIFICATION_FAILED
retry_budget: 2
---
# Contract
"""


def test_registry_requires_all_five_active_contracts(tmp_path: Path) -> None:
    loops = [
        "daily-governance-triage",
        "daily-research-operator",
        "weekly-evidence-synthesis",
        "monthly-governance",
        "system-audit",
    ]
    for loop in loops:
        (tmp_path / f"{loop}.v1.md").write_text(contract_text(loop), encoding="utf-8")
    registry = ContractRegistry.from_directory(tmp_path)
    registry.validate_required_loops()
    assert registry.active("daily-governance-triage").contract_version == "1.0.0"
    assert registry.active("monthly-governance").contract_version == "1.0.0"


def test_retired_contract_requires_replay_mode(tmp_path: Path) -> None:
    path = tmp_path / "daily.v1.md"
    path.write_text(contract_text("daily-research-operator", status="retired"), encoding="utf-8")
    registry = ContractRegistry([parse_contract(path)])
    with pytest.raises(ValueError, match="replay"):
        registry.resolve("daily-research-operator", "1.0.0")
    assert registry.resolve("daily-research-operator", "1.0.0", replay=True).status == "retired"


def test_contract_must_authorize_receipts(tmp_path: Path) -> None:
    path = tmp_path / "bad.md"
    path.write_text(contract_text("daily-research-operator").replace("  - automation/runs/**", "  - outputs/**"), encoding="utf-8")
    with pytest.raises(ValueError, match="receipts"):
        parse_contract(path)
