"""Command-line entrypoints for the SNS transaction layer."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .audit import build_audit_report, render_audit_markdown
from .contracts import ContractRegistry
from .receipts import ReceiptStore, generate_long_log
from .semantics import cluster_evidence_events
from .state import validate_repository_state


def _json_records(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    return [json.loads(item.read_text(encoding="utf-8")) for item in sorted(path.glob("**/*.json"))]


def cmd_validate(args: argparse.Namespace) -> int:
    report = validate_repository_state(args.root, strict=False)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["valid"] else 1


def cmd_write_receipt(args: argparse.Namespace) -> int:
    root = Path(args.root)
    registry = ContractRegistry.from_directory(root / "automation/contracts")
    receipt = json.loads(Path(args.receipt).read_text(encoding="utf-8"))
    path = ReceiptStore(root / "automation/runs", contracts=registry).write(receipt)
    print(path)
    return 0


def cmd_generate_log(args: argparse.Namespace) -> int:
    root = Path(args.root)
    registry = ContractRegistry.from_directory(root / "automation/contracts")
    receipts = ReceiptStore(root / "automation/runs", contracts=registry).load_all()
    destination = root / args.output
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(generate_long_log(receipts), encoding="utf-8")
    print(destination)
    return 0


def cmd_audit(args: argparse.Namespace) -> int:
    root = Path(args.root)
    registry = ContractRegistry.from_directory(root / "automation/contracts")
    receipts = ReceiptStore(root / "automation/runs", contracts=registry).load_all()
    evidence = _json_records(root / "calendar/evidence")
    clusters = cluster_evidence_events(evidence) if evidence else {}
    report = build_audit_report(
        receipts,
        cutoff_time=args.cutoff_time,
        cutoff_commit=args.cutoff_commit,
        quest_actions=_json_records(root / "quests/actions"),
        evidence_clusters=clusters,
        pr_lifecycle=_json_records(root / "automation/pr_lifecycle"),
    )
    json_output = root / args.json_output
    md_output = root / args.markdown_output
    json_output.parent.mkdir(parents=True, exist_ok=True)
    md_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_output.write_text(render_audit_markdown(report), encoding="utf-8")
    print(json_output)
    print(md_output)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="repository root")
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate = subparsers.add_parser("validate-repository")
    validate.set_defaults(func=cmd_validate)
    write = subparsers.add_parser("write-receipt")
    write.add_argument("receipt")
    write.set_defaults(func=cmd_write_receipt)
    log = subparsers.add_parser("generate-long-log")
    log.add_argument("--output", default="automation/reports/generated_long_log.md")
    log.set_defaults(func=cmd_generate_log)
    audit = subparsers.add_parser("audit")
    audit.add_argument("--cutoff-time", required=True)
    audit.add_argument("--cutoff-commit", required=True)
    audit.add_argument("--json-output", default="automation/reports/metrics/system_audit.json")
    audit.add_argument("--markdown-output", default="automation/reports/system_audit.md")
    audit.set_defaults(func=cmd_audit)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
