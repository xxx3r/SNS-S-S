"""Shared vocabularies for loop and pull-request terminal states."""

from __future__ import annotations

from enum import Enum


class LoopTerminalState(str, Enum):
    DONE = "DONE"
    DONE_WITH_LIMITATIONS = "DONE_WITH_LIMITATIONS"
    BLOCKED_ENVIRONMENT = "BLOCKED_ENVIRONMENT"
    BLOCKED_MISSING_EVIDENCE = "BLOCKED_MISSING_EVIDENCE"
    BLOCKED_CONFLICT = "BLOCKED_CONFLICT"
    VERIFICATION_FAILED = "VERIFICATION_FAILED"
    NEEDS_SCIENTIFIC_DECISION = "NEEDS_SCIENTIFIC_DECISION"
    NEEDS_GOVERNANCE_REVIEW = "NEEDS_GOVERNANCE_REVIEW"
    NEEDS_APPROVAL = "NEEDS_APPROVAL"


class QuestActionType(str, Enum):
    REFINE_EXISTING = "refine_existing"
    PROPOSE_NEW = "propose_new"
    BLOCK = "block"
    RETIRE = "retire"
    MERGE_WITH = "merge_with"
    NO_ACTION = "no_action"


class PRLifecycleState(str, Enum):
    DRAFT_ACTIVE = "draft_active"
    READY_FOR_REVIEW = "ready_for_review"
    CHANGES_REQUESTED = "changes_requested"
    MERGE_READY = "merge_ready"
    MERGED = "merged"
    BLOCKED = "blocked"
    SPLIT_REQUIRED = "split_required"
    SUPERSEDED = "superseded"
    CLOSED_ABANDONED = "closed_abandoned"


class EvidencePolarity(str, Enum):
    SUPPORTS = "supports"
    WEAKENS = "weakens"
    FALSIFIES = "falsifies"
    CONTEXT_ONLY = "context_only"


class BeliefEffect(str, Enum):
    STRENGTHEN = "strengthen"
    WEAKEN = "weaken"
    UNCERTAINTY_INCREASE = "uncertainty_increase"
    UNCERTAINTY_DECREASE = "uncertainty_decrease"
    NO_CHANGE = "no_change"
