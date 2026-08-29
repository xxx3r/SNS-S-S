from __future__ import annotations

import json
from pathlib import Path

import pytest

from automation.research_graph import ready_frontier, validate_research_graph
from automation.routing import route_daily_slot_from_graph


def test_repository_graph_covers_all_active_quests() -> None:
    graph = json.loads(Path("quests/research_graph.json").read_text(encoding="utf-8"))
    active_ids = {
        "QST-STOR-0002",
        "QST-SIM-0002",
        "QST-SIM-0003",
        "QST-PV-0001",
        "QST-META-0001",
        "QST-ARCI-0001",
        "QST-CALENDAR-0001",
        "QST-FUND-0001",
    }
    validate_research_graph(graph)
    assert set(ready_frontier(graph, active_ids=active_ids)) == active_ids


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
