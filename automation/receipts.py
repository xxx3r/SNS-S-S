"""Immutable run receipts and generated human-readable history."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Mapping

from .contracts import ContractRegistry
from .ids import validate_identifier
from .models import LoopTerminalState

_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_SEMVER_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
_ALLOWED_LOOPS = {
    "daily-research-operator",
    "weekly-evidence-synthesis",
    "monthly-governance",
    "system-audit",
}


def _parse_utc_timestamp(value: str, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field} must be ISO-8601") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{field} must include a timezone")
    return parsed.astimezone(timezone.utc)


def validate_run_receipt(
    receipt: Mapping[str, object],
    *,
    contracts: ContractRegistry | None = None,
) -> None:
    required = {
        "schema",
        "run_id",
        "loop_id",
        "contract_version",
        "trigger",
        "trigger_time",
        "source_commit",
        "state_hash",
        "quest_context",
        "pr_context",
        "consumed_ids",
        "artifacts",
        "checks",
        "belief_effects",
        "terminal_state",
        "next_action",
        "created_at",
    }
    missing = required - set(receipt)
    if missing:
        raise ValueError(f"run receipt missing fields: {', '.join(sorted(missing))}")
    if receipt["schema"] != "sns.loop-run.v1":
        raise ValueError("unsupported run receipt schema")

    run_id = str(receipt["run_id"])
    validate_identifier(run_id, prefix="RUN")
    loop_id = str(receipt["loop_id"])
    if loop_id not in _ALLOWED_LOOPS:
        raise ValueError(f"unknown loop_id: {loop_id}")
    contract_version = str(receipt["contract_version"])
    if not _SEMVER_RE.fullmatch(contract_version):
        raise ValueError("contract_version must be semantic version X.Y.Z")
    if contracts is not None:
        contract = contracts.resolve(loop_id, contract_version)
        if str(receipt["trigger"]) not in contract.allowed_triggers:
            raise ValueError("receipt trigger is not allowed by its contract")

    if not _SHA_RE.fullmatch(str(receipt["source_commit"])):
        raise ValueError("source_commit must be a lowercase 40-character Git SHA")
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", str(receipt["state_hash"])):
        raise ValueError("state_hash must be sha256:<64 lowercase hex>")

    trigger_time = _parse_utc_timestamp(str(receipt["trigger_time"]), "trigger_time")
    created_at = _parse_utc_timestamp(str(receipt["created_at"]), "created_at")
    if created_at < trigger_time:
        raise ValueError("created_at cannot precede trigger_time")

    terminal_states = {state.value for state in LoopTerminalState}
    if str(receipt["terminal_state"]) not in terminal_states:
        raise ValueError("invalid terminal_state")
    next_action = receipt["next_action"]
    if not isinstance(next_action, str) or not next_action.strip():
        raise ValueError("next_action must be one concrete non-empty action")

    for collection in ("consumed_ids", "artifacts", "checks", "belief_effects"):
        if not isinstance(receipt[collection], list):
            raise ValueError(f"{collection} must be a list")
    if not isinstance(receipt["quest_context"], dict):
        raise ValueError("quest_context must be an object")
    if not isinstance(receipt["pr_context"], dict):
        raise ValueError("pr_context must be an object")

    checks = receipt["checks"]
    assert isinstance(checks, list)
    for check in checks:
        if not isinstance(check, dict):
            raise ValueError("each check must be an object")
        if not {"name", "status", "evidence"}.issubset(check):
            raise ValueError("each check requires name, status, and evidence")
        if check["status"] not in {"passed", "failed", "not_run"}:
            raise ValueError("check status must be passed, failed, or not_run")
        if check["status"] != "not_run" and not str(check["evidence"]).strip():
            raise ValueError("executed checks require result evidence")

    correction_of = receipt.get("correction_of")
    if correction_of is not None:
        validate_identifier(str(correction_of), prefix="RUN")
        if correction_of == run_id:
            raise ValueError("a receipt cannot correct itself")


def receipt_relative_path(receipt: Mapping[str, object]) -> Path:
    created = _parse_utc_timestamp(str(receipt["created_at"]), "created_at")
    return Path(f"{created.year:04d}") / f"{created.month:02d}" / f"{receipt['run_id']}.json"


class ReceiptStore:
    """Filesystem store that never overwrites an existing receipt."""

    def __init__(self, root: str | Path, contracts: ContractRegistry | None = None):
        self.root = Path(root)
        self.contracts = contracts

    def write(self, receipt: Mapping[str, object]) -> Path:
        validate_run_receipt(receipt, contracts=self.contracts)
        path = self.root / receipt_relative_path(receipt)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
        try:
            with path.open("x", encoding="utf-8") as handle:
                handle.write(payload)
        except FileExistsError as exc:
            raise FileExistsError(f"immutable receipt already exists: {path}") from exc
        return path

    def load_all(self) -> list[dict[str, object]]:
        receipts: list[dict[str, object]] = []
        seen: set[str] = set()
        for path in sorted(self.root.glob("**/*.json")):
            receipt = json.loads(path.read_text(encoding="utf-8"))
            validate_run_receipt(receipt, contracts=self.contracts)
            run_id = str(receipt["run_id"])
            if run_id in seen:
                raise ValueError(f"duplicate run_id across receipt files: {run_id}")
            seen.add(run_id)
            receipts.append(receipt)
        receipt_ids = {str(receipt["run_id"]) for receipt in receipts}
        for receipt in receipts:
            correction_of = receipt.get("correction_of")
            if correction_of and correction_of not in receipt_ids:
                raise ValueError(f"correction cites missing receipt: {correction_of}")
        return receipts


def generate_long_log(receipts: Iterable[Mapping[str, object]]) -> str:
    ordered = sorted(receipts, key=lambda item: (str(item["created_at"]), str(item["run_id"])))
    lines = [
        "# Generated Autonomous Run Log",
        "",
        "> Generated from immutable `automation/runs/**` receipts. Do not edit by hand.",
        "",
        "| Created (UTC) | Loop | Terminal state | Quest | PR | Run | Next action |",
        "|---|---|---|---|---:|---|---|",
    ]
    for receipt in ordered:
        quest = str(dict(receipt.get("quest_context", {})).get("quest_id", ""))
        pr_number = dict(receipt.get("pr_context", {})).get("pr_number", "")
        lines.append(
            "| {created} | {loop} | {state} | {quest} | {pr} | `{run}` | {next_action} |".format(
                created=receipt["created_at"],
                loop=receipt["loop_id"],
                state=receipt["terminal_state"],
                quest=quest,
                pr=pr_number,
                run=receipt["run_id"],
                next_action=str(receipt["next_action"]).replace("|", "\\|"),
            )
        )
    return "\n".join(lines) + "\n"
