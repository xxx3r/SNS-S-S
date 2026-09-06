from __future__ import annotations

import json
from pathlib import Path

import pytest

from automation.research_graph import ready_frontier, validate_research_graph
from automation.routing import route_daily_slot_from_graph
from automation.state import validate_active_membership


def test_repository_graph_covers_all_active_quests() -> None:
    graph = json.loads(Path("quests/research_graph.json").read_text(encoding="utf-8"))
    active_ids = validate_active_membership(Path('.'), graph)
    assert set(ready_frontier(graph, active_ids=active_ids)) <= active_ids


def test_membership_allows_retirement_and_unready_active_quest(tmp_path: Path) -> None:
    active = tmp_path / "quests/active"
    active.mkdir(parents=True)
    (active / "README.md").write_text("1. [QST-NEW-0001: New](QST-NEW-0001-new.md)\n")
    (active / "QST-NEW-0001-new.md").write_text("# QST-NEW-0001")
    graph = {"schema": "sns.research-graph.v1", "nodes": [
        {"id": "QST-OLD-0001", "type": "research_quest", "status": "completed", "priority": "P0"},
        {"id": "QST-NEW-0001", "type": "research_quest", "status": "active", "priority": "P1"},
        {"id": "FREEZE", "type": "artifact", "status": "proposed"},
    ], "edges": [{"source": "QST-NEW-0001", "target": "FREEZE", "type": "requires"}]}
    ids = validate_active_membership(tmp_path, graph)
    assert ids == {"QST-NEW-0001"}
    assert ready_frontier(graph, active_ids=ids) == []
    graph["nodes"][0]["status"] = "active"
    with pytest.raises(ValueError, match="graph membership disagree"):
        validate_active_membership(tmp_path, graph)
    graph["nodes"][0]["status"] = "completed"
    (active / "README.md").write_text("1. [QST-NEW-0001: New](missing.md)\n")
    with pytest.raises(ValueError, match="invalid quest link"):
        validate_active_membership(tmp_path, graph)


def test_hard_dependency_cycle_fails_closed() -> None:
    graph = {
        "schema": "sns.research-graph.v1",
        "nodes": [
            {"id": "A", "type": "research_quest", "status": "active", "priority": "P0"},
            {"id": "B", "type": "research_quest", "status": "active", "priority": "P0"},
        ],
        "edges": [
            {"source": "A", "target": "B", "type": "requires"},
            {"source": "B", "target": "A", "type": "requires"},
        ],
    }
    with pytest.raises(ValueError, match="cycle"):
        validate_research_graph(graph)


def test_revisit_cycle_is_allowed_but_does_not_create_hard_dependency() -> None:
    graph = {
        "schema": "sns.research-graph.v1",
        "nodes": [
            {"id": "A", "type": "research_quest", "status": "active", "priority": "P0"},
            {"id": "B", "type": "research_quest", "status": "active", "priority": "P1"},
        ],
        "edges": [
            {"source": "A", "target": "B", "type": "revisit_after"},
            {"source": "B", "target": "A", "type": "informs"},
        ],
    }
    validate_research_graph(graph)
    assert set(ready_frontier(graph, active_ids=["A", "B"])) == {"A", "B"}


def test_router_applies_graph_readiness_before_priority() -> None:
    graph = {
        "schema": "sns.research-graph.v1",
        "nodes": [
            {"id": "A", "type": "research_quest", "status": "active", "priority": "P0"},
            {"id": "B", "type": "research_quest", "status": "active", "priority": "P1"},
            {"id": "EVID-X", "type": "evidence", "status": "proposed"},
        ],
        "edges": [{"source": "A", "target": "EVID-X", "type": "requires"}],
    }
    candidates = [
        {"quest_id": "A", "priority": "P0", "active_index": 1, "eligible": True, "executable": True, "blocker_scope": "none"},
        {"quest_id": "B", "priority": "P1", "active_index": 2, "eligible": True, "executable": True, "blocker_scope": "none"},
    ]
    result = route_daily_slot_from_graph(candidates, research_graph=graph, active_quest_ids=["A", "B"])
    assert result["decision"] == "AUTHORIZE"
    assert result["selected_quest_id"] == "B"
    assert result["graph_ready_frontier"] == ["B"]
