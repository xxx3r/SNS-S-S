"""Repository-local loop contract parsing and activation rules."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .models import LoopTerminalState

_SEMVER_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")


@dataclass(frozen=True)
class Contract:
    schema: str
    loop_id: str
    contract_version: str
    status: str
    owner: str
    allowed_triggers: tuple[str, ...]
    reads: tuple[str, ...]
    writes: tuple[str, ...]
    terminal_states: tuple[str, ...]
    retry_budget: int
    path: Path

    @property
    def key(self) -> tuple[str, str]:
        return self.loop_id, self.contract_version

    @property
    def active(self) -> bool:
        return self.status == "active"


def _parse_scalar(value: str) -> str | int:
    value = value.strip()
    if value.isdigit():
        return int(value)
    return value.strip('"\'')


def _parse_frontmatter(text: str) -> dict[str, object]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("contract must begin with YAML-like front matter")
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration as exc:
        raise ValueError("contract front matter is not terminated") from exc

    result: dict[str, object] = {}
    current_list: str | None = None
    for raw in lines[1:end]:
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw.startswith("  - "):
            if current_list is None:
                raise ValueError(f"list item without key: {raw}")
            values = result.setdefault(current_list, [])
            assert isinstance(values, list)
            values.append(str(_parse_scalar(raw[4:])))
            continue
        if ":" not in raw:
            raise ValueError(f"invalid front-matter line: {raw}")
        key, value = raw.split(":", 1)
        key = key.strip()
        if not key:
            raise ValueError("front-matter key cannot be empty")
        if value.strip():
            result[key] = _parse_scalar(value)
            current_list = None
        else:
            result[key] = []
            current_list = key
    return result


def parse_contract(path: str | Path) -> Contract:
    contract_path = Path(path)
    data = _parse_frontmatter(contract_path.read_text(encoding="utf-8"))
    required = {
        "schema",
        "loop_id",
        "contract_version",
        "status",
        "owner",
        "allowed_triggers",
        "reads",
        "writes",
        "terminal_states",
        "retry_budget",
    }
    missing = required - set(data)
    if missing:
        raise ValueError(f"contract missing fields: {', '.join(sorted(missing))}")

    contract = Contract(
        schema=str(data["schema"]),
        loop_id=str(data["loop_id"]),
        contract_version=str(data["contract_version"]),
        status=str(data["status"]),
        owner=str(data["owner"]),
        allowed_triggers=tuple(str(v) for v in data["allowed_triggers"]),
        reads=tuple(str(v) for v in data["reads"]),
        writes=tuple(str(v) for v in data["writes"]),
        terminal_states=tuple(str(v) for v in data["terminal_states"]),
        retry_budget=int(data["retry_budget"]),
        path=contract_path,
    )
    validate_contract(contract)
    return contract


def validate_contract(contract: Contract) -> None:
    if contract.schema != "sns.loop-contract.v1":
        raise ValueError(f"unsupported contract schema: {contract.schema}")
    if not _SEMVER_RE.fullmatch(contract.contract_version):
        raise ValueError("contract_version must be semantic version X.Y.Z")
    if contract.status not in {"active", "retired", "proposed"}:
        raise ValueError("contract status must be active, retired, or proposed")
    if not contract.allowed_triggers:
        raise ValueError("contract must allow at least one trigger")
    if contract.retry_budget < 0 or contract.retry_budget > 5:
        raise ValueError("retry_budget must be between 0 and 5")
    allowed_states = {state.value for state in LoopTerminalState}
    invalid_states = set(contract.terminal_states) - allowed_states
    if invalid_states:
        raise ValueError(f"unknown terminal states: {', '.join(sorted(invalid_states))}")
    required_states = {
        LoopTerminalState.DONE.value,
        LoopTerminalState.BLOCKED_CONFLICT.value,
        LoopTerminalState.VERIFICATION_FAILED.value,
    }
    if not required_states.issubset(contract.terminal_states):
        raise ValueError("contract omits required done/conflict/verification states")
    if "automation/runs/**" not in contract.writes:
        raise ValueError("every loop contract must authorize immutable run receipts")


class ContractRegistry:
    """Load contracts and enforce one active version per loop."""

    def __init__(self, contracts: Iterable[Contract]):
        self._contracts = tuple(contracts)
        if not self._contracts:
            raise ValueError("contract registry cannot be empty")
        seen: set[tuple[str, str]] = set()
        active: dict[str, Contract] = {}
        for contract in self._contracts:
            if contract.key in seen:
                raise ValueError(f"duplicate contract version: {contract.key}")
            seen.add(contract.key)
            if contract.active:
                if contract.loop_id in active:
                    raise ValueError(f"multiple active contracts for {contract.loop_id}")
                active[contract.loop_id] = contract
        self._active = active

    @classmethod
    def from_directory(cls, directory: str | Path) -> "ContractRegistry":
        paths = sorted(Path(directory).glob("*.md"))
        return cls(parse_contract(path) for path in paths)

    def active(self, loop_id: str) -> Contract:
        try:
            return self._active[loop_id]
        except KeyError as exc:
            raise KeyError(f"no active contract for {loop_id}") from exc

    def resolve(self, loop_id: str, version: str, *, replay: bool = False) -> Contract:
        for contract in self._contracts:
            if contract.key == (loop_id, version):
                if contract.status == "retired" and not replay:
                    raise ValueError("retired contract requires explicit replay mode")
                if contract.status == "proposed":
                    raise ValueError("proposed contract cannot produce run receipts")
                return contract
        raise KeyError(f"unknown contract {loop_id}@{version}")

    def validate_required_loops(self) -> None:
        required = {
            "daily-research-operator",
            "weekly-evidence-synthesis",
            "monthly-governance",
            "system-audit",
        }
        missing = required - set(self._active)
        if missing:
            raise ValueError(f"missing active loop contracts: {', '.join(sorted(missing))}")
