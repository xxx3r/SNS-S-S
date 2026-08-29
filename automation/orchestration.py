"""Desired runtime orchestration and deterministic drift detection."""

from __future__ import annotations

from typing import Mapping, Sequence

_REQUIRED_LOOP_IDS = {
    "daily-governance-triage",
    "daily-research-operator",
    "weekly-evidence-synthesis",
    "monthly-governance",
    "system-audit",
}
_TIMING_MODES = {"exact_schedule", "flexible_schedule", "condition_watch", "explicit_only"}


def render_bootstrap_prompt(loop_id: str) -> str:
    if loop_id not in _REQUIRED_LOOP_IDS:
        raise ValueError(f"unknown SNS loop_id: {loop_id}")
    return (
        f"Operate `xxx3r/SNS-S-S` as loop `{loop_id}`. "
        "First invoke the connected GitHub repository tool; never infer an environment blocker from missing local shell access. "
        "Read accepted `main` and `AGENTS.md`, then resolve the one currently active repository contract whose front matter matches this loop_id; do not hard-code a contract path or version from this platform prompt. "
        "Read only the compact state authorized by stable law and that active contract, including current executable schemas and the canonical runtime/research-graph records when relevant. "
        "Execute one bounded transaction, preserving one-owner and authority boundaries. New run records must use the current repository receipt schema and canonical inspectable state-snapshot law; never substitute a placeholder digest. "
        "Before publication, recheck accepted source, governance/delegation, graph readiness, and live PR ownership, then use repository-hosted validation as the evaluator when local execution is unavailable. "
        "Use Google Drive only when the active contract or a concrete pending decision explicitly requires a relevant SNS artifact. "
        "End by reporting attempted connector operations, created or consumed artifacts/authority, receipt ID, terminal state, limitations, and one exact handoff."
    )


def validate_runtime_manifest(manifest: Mapping[str, object]) -> None:
    if manifest.get("schema") != "sns.runtime-manifest.v1":
        raise ValueError("unsupported runtime manifest schema")
    if not str(manifest.get("timezone", "")).strip():
        raise ValueError("runtime manifest requires timezone")
    if manifest.get("bootstrap_prompt") != "automation/prompts/bootstrap.v1.md":
        raise ValueError("runtime manifest must bind the canonical bootstrap prompt surface")

    loops = manifest.get("loops")
    if not isinstance(loops, list):
        raise ValueError("runtime manifest loops must be a list")
    seen: set[str] = set()
    scheduled_order: dict[str, int] = {}
    for row in loops:
        if not isinstance(row, dict):
            raise ValueError("runtime manifest loop rows must be objects")
        required = {
            "loop_id",
            "automation_title",
            "scheduler_managed",
            "desired_enabled",
            "timing_mode",
            "schedule",
            "order",
        }
        missing = required - set(row)
        if missing:
            raise ValueError(f"runtime loop row missing fields: {', '.join(sorted(missing))}")
        loop_id = str(row["loop_id"])
        if loop_id not in _REQUIRED_LOOP_IDS:
            raise ValueError(f"unknown runtime loop_id: {loop_id}")
        if loop_id in seen:
            raise ValueError(f"duplicate runtime loop_id: {loop_id}")
        seen.add(loop_id)
        if not str(row["automation_title"]).strip():
            raise ValueError("runtime automation_title cannot be empty")
        if not isinstance(row["scheduler_managed"], bool) or not isinstance(row["desired_enabled"], bool):
            raise ValueError("scheduler_managed and desired_enabled must be booleans")
        timing_mode = str(row["timing_mode"])
        if timing_mode not in _TIMING_MODES:
            raise ValueError(f"unknown runtime timing_mode: {timing_mode}")
        schedule = row["schedule"]
        if bool(row["scheduler_managed"]):
            if not isinstance(schedule, str) or "BEGIN:VEVENT" not in schedule or "END:VEVENT" not in schedule:
                raise ValueError(f"scheduler-managed loop requires VEVENT schedule: {loop_id}")
            if timing_mode == "explicit_only":
                raise ValueError("scheduler-managed loop cannot use explicit_only timing")
            scheduled_order[loop_id] = int(row["order"])
        else:
            if schedule is not None:
                raise ValueError("non-scheduler-managed loop must use null schedule")
            if timing_mode != "explicit_only":
                raise ValueError("non-scheduler-managed loop must use explicit_only timing")

    if seen != _REQUIRED_LOOP_IDS:
        missing = _REQUIRED_LOOP_IDS - seen
        raise ValueError(f"runtime manifest missing loops: {', '.join(sorted(missing))}")
    if scheduled_order["daily-governance-triage"] >= scheduled_order["daily-research-operator"]:
        raise ValueError("Pre-Game must precede Daily in orchestration order")


def compare_runtime_manifest(
    manifest: Mapping[str, object],
    observed: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    """Compare desired scheduler state against a normalized live task snapshot."""

    validate_runtime_manifest(manifest)
    observed_by_title = {str(row["title"]): row for row in observed}
    drift: list[dict[str, object]] = []
    loops = manifest["loops"]
    assert isinstance(loops, list)
    for expected in loops:
        assert isinstance(expected, dict)
        if not bool(expected["scheduler_managed"]):
            continue
        title = str(expected["automation_title"])
        actual = observed_by_title.get(title)
        if actual is None:
            drift.append({"loop_id": expected["loop_id"], "field": "presence", "expected": title, "actual": None})
            continue
        comparisons = {
            "is_enabled": bool(expected["desired_enabled"]),
            "schedule": expected["schedule"],
            "timing_mode": expected["timing_mode"],
            "prompt": render_bootstrap_prompt(str(expected["loop_id"])),
        }
        for field, wanted in comparisons.items():
            got = actual.get(field)
            if got != wanted:
                drift.append({"loop_id": expected["loop_id"], "field": field, "expected": wanted, "actual": got})
    return drift
