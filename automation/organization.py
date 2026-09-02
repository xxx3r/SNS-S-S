"""September Organization v2.x observability primitives.

These helpers make the September organizational contract executable without
making scientific, quest, belief, memory, or scheduler choices.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import re
from typing import Iterable, Mapping

from .ids import validate_identifier

_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_INHERITANCE_KINDS = {"RUN", "EVID", "BEL", "QA", "artifact"}
_CONTINUITY_VALUES = {"inherited", "independent", "handoff"}


def _timestamp(value: object, field: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field} must be ISO-8601") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{field} must include a timezone")
    return parsed.astimezone(timezone.utc)


def cutoff_ancestry_set(
    cutoff_commit: str,
    cutoff_ancestors: Iterable[str] | None,
) -> set[str]:
    """Return the exact accepted ancestry set for a frozen cutoff commit.

    Callers must provide connector- or git-derived reachable commits. There is
    no temporal-only fallback: missing ancestry evidence fails closed.
    """

    if not _SHA_RE.fullmatch(str(cutoff_commit)):
        raise ValueError("cutoff_commit must be a lowercase 40-character Git SHA")
    if cutoff_ancestors is None:
        raise ValueError("cutoff ancestry evidence is required")
    result = {str(cutoff_commit)}
    for ancestor in cutoff_ancestors:
        value = str(ancestor)
        if not _SHA_RE.fullmatch(value):
            raise ValueError("cutoff ancestry contains an invalid Git SHA")
        result.add(value)
    return result


def _normalise_kind(kind: object) -> str:
    value = str(kind).strip()
    if value.lower() == "artifact":
        return "artifact"
    value = value.upper()
    if value not in _INHERITANCE_KINDS:
        raise ValueError(f"unsupported inheritance kind: {value}")
    return value


def _normalise_reference(kind: object, reference: object, effect: object = None) -> dict[str, str]:
    normalized_kind = _normalise_kind(kind)
    value = str(reference).strip()
    if normalized_kind == "artifact":
        if value.startswith("artifact:"):
            value = value[len("artifact:"):]
        if not value or value.startswith("/") or value.startswith("../") or "/../" in value:
            raise ValueError("artifact inheritance reference must be a relative repository path")
    else:
        validate_identifier(value, prefix=normalized_kind)
    row = {"kind": normalized_kind, "ref": value}
    if effect is not None:
        if not isinstance(effect, str) or not effect.strip():
            raise ValueError("inheritance decision_effect must be a non-empty string")
        row["decision_effect"] = effect.strip()
    return row


def recorded_decision_effect(receipt: Mapping[str, object]) -> str | None:
    direct = receipt.get("decision_effect")
    if isinstance(direct, str) and direct.strip():
        return direct.strip()
    context = receipt.get("quest_context")
    if isinstance(context, Mapping):
        nested = context.get("decision_effect")
        if isinstance(nested, str) and nested.strip():
            return nested.strip()
    return None


def _kind_from_identifier(value: object) -> str | None:
    text = str(value).strip()
    if text.startswith("artifact:"):
        return "artifact"
    for kind in ("RUN", "EVID", "BEL", "QA"):
        if text.startswith(kind + "-"):
            return kind
    return None


def _artifact_path(value: object) -> str | None:
    if isinstance(value, str):
        return value.strip() or None
    if isinstance(value, Mapping):
        path = value.get("path")
        if isinstance(path, str) and path.strip():
            return path.strip()
    return None


def _explicit_inheritance_rows(receipt: Mapping[str, object]) -> list[dict[str, str]]:
    raw = receipt.get("inheritance")
    if raw is None:
        return []
    effect = recorded_decision_effect(receipt)
    rows: list[dict[str, str]] = []
    if isinstance(raw, Mapping):
        for kind, references in raw.items():
            if not isinstance(references, list):
                raise ValueError("inheritance mapping values must be lists")
            for reference in references:
                if isinstance(reference, Mapping):
                    ref = reference.get("ref", reference.get("id", reference.get("path")))
                    row_effect = reference.get("decision_effect", effect)
                else:
                    ref = reference
                    row_effect = effect
                rows.append(_normalise_reference(kind, ref, row_effect))
    elif isinstance(raw, list):
        for reference in raw:
            if not isinstance(reference, Mapping):
                raise ValueError("inheritance list entries must be objects")
            kind = reference.get("kind", reference.get("type"))
            ref = reference.get("ref", reference.get("id", reference.get("path")))
            row_effect = reference.get("decision_effect", effect)
            rows.append(_normalise_reference(kind, ref, row_effect))
    else:
        raise ValueError("inheritance must be a list or typed mapping")
    return rows


def inheritance_references(receipt: Mapping[str, object]) -> list[dict[str, str]]:
    """Return normalized typed prior-state references.

    New receipts should use inheritance objects. The consumed_ids fallback is
    retained so historical v2 receipts become measurable without rewriting
    them; non-lineage authority IDs such as AUTH and DELEG are ignored here.
    """

    rows = _explicit_inheritance_rows(receipt)
    effect = recorded_decision_effect(receipt)
    inherited_ids = receipt.get("inherited_ids", [])
    if inherited_ids is not None:
        if not isinstance(inherited_ids, list):
            raise ValueError("inherited_ids must be a list")
        for value in inherited_ids:
            kind = _kind_from_identifier(value)
            if kind is None:
                raise ValueError("inherited_ids must use RUN, EVID, BEL, QA, or artifact: references")
            reference = str(value)
            if kind == "artifact":
                reference = reference[len("artifact:"):]
            rows.append(_normalise_reference(kind, reference, effect))

    for value in receipt.get("consumed_ids", []):
        kind = _kind_from_identifier(value)
        if kind is None:
            continue
        reference = str(value)
        if kind == "artifact":
            reference = reference[len("artifact:"):]
        rows.append(_normalise_reference(kind, reference, effect))

    unique: dict[tuple[str, str], dict[str, str]] = {}
    for row in rows:
        unique.setdefault((row["kind"], row["ref"]), row)
    return list(unique.values())


def validate_receipt_observability(receipt: Mapping[str, object]) -> None:
    """Validate optional v2.x inheritance and timing fields when present."""

    if "inheritance" in receipt:
        _explicit_inheritance_rows(receipt)
    if "inherited_ids" in receipt:
        inherited_ids = receipt["inherited_ids"]
        if not isinstance(inherited_ids, list):
            raise ValueError("inherited_ids must be a list")
        for value in inherited_ids:
            kind = _kind_from_identifier(value)
            if kind is None:
                raise ValueError("inherited_ids contains an untyped reference")
    if "decision_effect" in receipt and (
        not isinstance(receipt["decision_effect"], str)
        or not receipt["decision_effect"].strip()
    ):
        raise ValueError("decision_effect must be a non-empty string")

    observability = receipt.get("observability")
    if observability is None:
        return
    if not isinstance(observability, Mapping):
        raise ValueError("observability must be an object")
    for field in ("proposal_at", "authorization_at", "first_artifact_at"):
        value = observability.get(field)
        if value is not None:
            _timestamp(value, f"observability.{field}")
    for field in ("administrative_transactions", "scientific_artifacts"):
        if field in observability:
            value = observability[field]
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"observability.{field} must be a non-negative integer")
    continuity = observability.get("continuity")
    if continuity is not None and continuity not in _CONTINUITY_VALUES:
        raise ValueError("observability.continuity is invalid")


def has_lineage_declaration(receipt: Mapping[str, object]) -> bool:
    if inheritance_references(receipt):
        return True
    observability = receipt.get("observability")
    return isinstance(observability, Mapping) and observability.get("continuity") == "independent"


def _produced_references(receipt: Mapping[str, object]) -> dict[str, set[str]]:
    result = {kind: set() for kind in _INHERITANCE_KINDS}
    run_id = receipt.get("run_id")
    if isinstance(run_id, str) and run_id.strip():
        result["RUN"].add(run_id.strip())
    for value in receipt.get("consumed_ids", []):
        kind = _kind_from_identifier(value)
        if kind is None:
            continue
        reference = str(value)
        if kind == "artifact":
            reference = reference[len("artifact:"):]
        result[kind].add(reference)
    for row in inheritance_references(receipt):
        result[row["kind"]].add(row["ref"])
    for value in receipt.get("artifacts", []):
        path = _artifact_path(value)
        if path:
            result["artifact"].add(path)
    return result


def _latency_summary(values: list[float]) -> dict[str, object]:
    if not values:
        return {"count": 0, "min_seconds": None, "max_seconds": None, "mean_seconds": None}
    return {
        "count": len(values),
        "min_seconds": min(values),
        "max_seconds": max(values),
        "mean_seconds": sum(values) / len(values),
    }


def communication_observability(receipts: Iterable[Mapping[str, object]]) -> dict[str, object]:
    proposal_to_authorization: list[float] = []
    authorization_to_artifact: list[float] = []
    administrative_transactions = 0
    scientific_artifacts = 0
    for receipt in receipts:
        validate_receipt_observability(receipt)
        raw = receipt.get("observability")
        if not isinstance(raw, Mapping):
            continue
        proposal_at = raw.get("proposal_at")
        authorization_at = raw.get("authorization_at")
        artifact_at = raw.get("first_artifact_at")
        if proposal_at is not None and authorization_at is not None:
            delta = (_timestamp(authorization_at, "authorization_at") - _timestamp(proposal_at, "proposal_at")).total_seconds()
            if delta < 0:
                raise ValueError("authorization_at cannot precede proposal_at")
            proposal_to_authorization.append(delta)
        if authorization_at is not None and artifact_at is not None:
            delta = (_timestamp(artifact_at, "first_artifact_at") - _timestamp(authorization_at, "authorization_at")).total_seconds()
            if delta < 0:
                raise ValueError("first_artifact_at cannot precede authorization_at")
            authorization_to_artifact.append(delta)
        administrative_transactions += int(raw.get("administrative_transactions", 0))
        scientific_artifacts += int(raw.get("scientific_artifacts", 0))

    ratio = administrative_transactions / scientific_artifacts if scientific_artifacts else None
    return {
        "proposal_to_authorization_latency_seconds": _latency_summary(proposal_to_authorization),
        "authorization_to_first_artifact_latency_seconds": _latency_summary(authorization_to_artifact),
        "administrative_transaction_count": administrative_transactions,
        "scientific_artifact_count": scientific_artifacts,
        "administrative_transactions_per_scientific_artifact": ratio,
    }


def typed_inheritance_metrics(receipts: Iterable[Mapping[str, object]]) -> dict[str, object]:
    ordered = sorted(receipts, key=lambda item: str(item["created_at"]))
    known = {kind: set() for kind in _INHERITANCE_KINDS}
    inherited_receipts = 0
    resolved_reference_count = 0
    unresolved_reference_count = 0
    reference_counts: Counter[str] = Counter()
    lineage_gaps: list[dict[str, object]] = []

    for index, receipt in enumerate(ordered):
        validate_receipt_observability(receipt)
        rows = inheritance_references(receipt)
        effect = recorded_decision_effect(receipt)
        if index:
            if not rows:
                observability = receipt.get("observability")
                continuity = observability.get("continuity") if isinstance(observability, Mapping) else None
                if continuity != "independent" or not effect:
                    lineage_gaps.append({
                        "run_id": str(receipt.get("run_id", "")),
                        "reason": "missing_typed_inheritance_or_decision_effect",
                        "references": [],
                    })
            else:
                unresolved = [row for row in rows if row["ref"] not in known[row["kind"]]]
                if not effect:
                    lineage_gaps.append({
                        "run_id": str(receipt.get("run_id", "")),
                        "reason": "missing_decision_effect",
                        "references": rows,
                    })
                elif unresolved:
                    lineage_gaps.append({
                        "run_id": str(receipt.get("run_id", "")),
                        "reason": "unresolved_inheritance_reference",
                        "references": unresolved,
                    })
                else:
                    inherited_receipts += 1
                    resolved_reference_count += len(rows)
                    reference_counts.update(row["kind"] for row in rows)
                unresolved_reference_count += len(unresolved)
        produced = _produced_references(receipt)
        for kind, values in produced.items():
            known[kind].update(values)

    eligible_count = max(0, len(ordered) - 1)
    return {
        "inherited_receipt_count": inherited_receipts,
        "eligible_receipt_count": eligible_count,
        "rate": inherited_receipts / eligible_count if eligible_count else 0.0,
        "resolved_reference_count": resolved_reference_count,
        "reference_counts": dict(sorted(reference_counts.items())),
        "unresolved_reference_count": unresolved_reference_count,
        "lineage_gap_count": len(lineage_gaps),
        "lineage_gaps": lineage_gaps,
    }


def information_inheritance_rate(receipts: Iterable[Mapping[str, object]]) -> dict[str, object]:
    """Return the legacy run-only diagnostic plus contract-complete metrics."""

    ordered = sorted(receipts, key=lambda item: str(item["created_at"]))
    eligible_ids = {str(item["run_id"]) for item in ordered[:-1]}
    consumed: set[str] = set()
    for receipt in ordered:
        consumed.update(
            str(value)
            for value in receipt.get("consumed_ids", [])
            if str(value) in eligible_ids
        )
    denominator = len(eligible_ids)
    run_only = {
        "inherited_run_count": len(consumed),
        "eligible_run_count": denominator,
        "rate": len(consumed) / denominator if denominator else 0.0,
        "inherited_run_ids": sorted(consumed),
    }
    typed = typed_inheritance_metrics(ordered)
    return {
        **run_only,
        "run_only_diagnostic": run_only,
        "contract_complete": typed,
        "lineage_gaps": typed["lineage_gaps"],
    }
