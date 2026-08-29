"""Command-line entrypoints for the SNS transaction layer."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .audit import build_audit_report, render_audit_markdown
from .contracts import ContractRegistry
from .orchestration import compare_runtime_manifest
from .provenance import build_run_receipt_v2, build_state_snapshot
from .receipts import ReceiptStore, generate_long_log, validate_run_receipt
from .research_graph import ready_frontier
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


def _record_pairs(values: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise ValueError("--record values must use ROLE=PATH")
        role, path = value.split("=", 1)
        if not role or not path or role in result:
            raise ValueError("snapshot record roles must be unique and non-empty")
        result[role] = path
    return result


def cmd_snapshot(args: argparse.Namespace) -> int:
    root = Path(args.root)
    open_prs = []
    if args.open_prs:
        open_prs = json.loads(Path(args.open_prs).read_text(encoding="utf-8"))
    snapshot = build_state_snapshot(
        root,
        source_commit=args.source_commit,
        records=_record_pairs(args.record),
        open_prs=open_prs,
    )
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(destination)
    return 0


def cmd_build_receipt_v2(args: argparse.Namespace) -> int:
    draft = json.loads(Path(args.draft).read_text(encoding="utf-8"))
    snapshot = json.loads(Path(args.snapshot).read_text(encoding="utf-8"))
    receipt = build_run_receipt_v2(
        draft,
        state_snapshot=snapshot,
        receipt_kind=args.kind,
        correction_of=args.correction_of,
    )
    validate_run_receipt(receipt)
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(destination)
    return 0


def cmd_graph_frontier(args: argparse.Namespace) -> int:
    root = Path(args.root)
    graph = json.loads((root / args.graph).read_text(encoding="utf-8"))
    active_ids = [item.strip() for item in args.active_ids.split(",") if item.strip()]
    print(json.dumps(ready_frontier(graph, active_ids=active_ids), indent=2))
    return 0


def cmd_runtime_drift(args: argparse.Namespace) -> int:
    root = Path(args.root)
    manifest = json.loads((root / args.manifest).read_text(encoding="utf-8"))
    observed = json.loads(Path(args.observed).read_text(encoding="utf-8"))
    drift = compare_runtime_manifest(manifest, observed)
    print(json.dumps(drift, indent=2, sort_keys=True))
    return 1 if drift else 0


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

    snapshot = subparsers.add_parser("snapshot-state")
    snapshot.add_argument("--source-commit", required=True)
    snapshot.add_argument("--record", action="append", default=[], help="canonical ROLE=PATH record; repeat")
    snapshot.add_argument("--open-prs", help="JSON list of normalized open PR ownership rows")
    snapshot.add_argument("--output", required=True)
    snapshot.set_defaults(func=cmd_snapshot)

    build_receipt = subparsers.add_parser("build-receipt-v2")
    build_receipt.add_argument("--draft", required=True)
    build_receipt.add_argument("--snapshot", required=True)
    build_receipt.add_argument("--output", required=True)
    build_receipt.add_argument("--kind", choices=["run", "correction"], default="run")
    build_receipt.add_argument("--correction-of")
    build_receipt.set_defaults(func=cmd_build_receipt_v2)

    frontier = subparsers.add_parser("graph-frontier")
    frontier.add_argument("--graph", default="quests/research_graph.json")
    frontier.add_argument("--active-ids", required=True, help="comma-separated active quest IDs")
    frontier.set_defaults(func=cmd_graph_frontier)

    runtime = subparsers.add_parser("runtime-drift")
    runtime.add_argument("--manifest", default="automation/runtime_manifest.json")
    runtime.add_argument("--observed", required=True, help="JSON list from the external scheduler snapshot")
    runtime.set_defaults(func=cmd_runtime_drift)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
