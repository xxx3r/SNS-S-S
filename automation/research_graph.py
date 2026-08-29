"""Typed research graph validation and deterministic ready-frontier derivation."""

from __future__ import annotations

import re
from typing import Iterable, Mapping

_PRIORITY_RE = re.compile(r"^P[0-9]+$")
_NODE_TYPES = {"research_quest", "research_infrastructure", "public_synthesis", "route", "experiment", "artifact", "evidence"}
_NODE_STATUSES = {"active", "ready", "blocked", "proposed", "completed", "falsified", "superseded"}
_EDGE_TYPES = {"contains", "requires", "informs", "unlocks", "falsifies", "competes_with", "supports", "supersedes", "revisit_after"}
_ROUTABLE_TYPES = {"research_quest", "research_infrastructure", "public_synthesis"}
_SATISFIED_REQUIREMENT_STATES = {"completed"}


def validate_research_graph(graph: Mapping[str, object]) -> None:
    if graph.get("schema") != "sns.research-graph.v1":
        raise ValueError("unsupported research graph schema")
    nodes = graph.get("nodes")
    edges = graph.get("edges")
    if not isinstance(nodes, list) or not nodes:
        raise ValueError("research graph requires nodes")
    if not isinstance(edges, list):
        raise ValueError("research graph edges must be a list")

    by_id: dict[str, Mapping[str, object]] = {}
    for node in nodes:
        if not isinstance(node, dict):
            raise ValueError("research graph nodes must be objects")
        required = {"id", "type", "status"}
        missing = required - set(node)
        if missing:
            raise ValueError(f"research graph node missing fields: {', '.join(sorted(missing))}")
        node_id = str(node["id"])
        if not node_id or node_id in by_id:
            raise ValueError(f"duplicate or empty research graph node id: {node_id!r}")
        node_type = str(node["type"])
        status = str(node["status"])
        if node_type not in _NODE_TYPES:
            raise ValueError(f"unknown research graph node type: {node_type}")
        if status not in _NODE_STATUSES:
            raise ValueError(f"unknown research graph node status: {status}")
        if node_type in _ROUTABLE_TYPES:
            priority = str(node.get("priority", ""))
            if not _PRIORITY_RE.fullmatch(priority):
                raise ValueError(f"routable graph node requires P<number> priority: {node_id}")
        by_id[node_id] = node

    seen_edges: set[tuple[str, str, str]] = set()
    requires: dict[str, set[str]] = {node_id: set() for node_id in by_id}
    for edge in edges:
        if not isinstance(edge, dict) or set(edge) - {"source", "target", "type", "note"}:
            raise ValueError("research graph edge fields are source, target, type, and optional note")
        if not {"source", "target", "type"}.issubset(edge):
            raise ValueError("research graph edge requires source, target, and type")
        source = str(edge["source"])
        target = str(edge["target"])
        edge_type = str(edge["type"])
        if source not in by_id or target not in by_id:
            raise ValueError(f"research graph edge cites missing endpoint: {source} -> {target}")
        if edge_type not in _EDGE_TYPES:
            raise ValueError(f"unknown research graph edge type: {edge_type}")
        key = (source, target, edge_type)
        if key in seen_edges:
            raise ValueError(f"duplicate research graph edge: {key}")
        seen_edges.add(key)
        if edge_type == "requires":
            if source == target:
                raise ValueError("hard dependency cannot require itself")
            requires[source].add(target)

    # Only the hard dependency subgraph must be acyclic.  Informational and
    # revisit edges may form cycles so research can spiral back to old questions.
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node_id: str) -> None:
        if node_id in visited:
            return
        if node_id in visiting:
            raise ValueError("hard research dependency graph contains a cycle")
        visiting.add(node_id)
        for dependency in sorted(requires[node_id]):
            visit(dependency)
        visiting.remove(node_id)
        visited.add(node_id)

    for node_id in sorted(by_id):
        visit(node_id)


def hard_requirements(graph: Mapping[str, object]) -> dict[str, set[str]]:
    validate_research_graph(graph)
    nodes = graph["nodes"]
    assert isinstance(nodes, list)
    result = {str(node["id"]): set() for node in nodes if isinstance(node, dict)}
    edges = graph["edges"]
    assert isinstance(edges, list)
    for edge in edges:
        assert isinstance(edge, dict)
        if edge["type"] == "requires":
            result[str(edge["source"])].add(str(edge["target"]))
    return result


def ready_frontier(
    graph: Mapping[str, object],
    *,
    active_ids: Iterable[str],
) -> list[str]:
    """Return ready active routable nodes without applying priority.

    Priority is deliberately a later routing concern.  Graph readiness answers
    only whether hard prerequisites are satisfied, which prevents priority order
    from masquerading as dependency structure.
    """

    validate_research_graph(graph)
    active = set(map(str, active_ids))
    nodes = graph["nodes"]
    assert isinstance(nodes, list)
    by_id = {str(node["id"]): node for node in nodes if isinstance(node, dict)}
    requirements = hard_requirements(graph)

    result: list[str] = []
    for node_id in sorted(active):
        node = by_id.get(node_id)
        if node is None:
            raise ValueError(f"active quest missing from research graph: {node_id}")
        if str(node["type"]) not in _ROUTABLE_TYPES:
            continue
        if str(node["status"]) not in {"active", "ready"}:
            continue
        if all(str(by_id[dependency]["status"]) in _SATISFIED_REQUIREMENT_STATES for dependency in requirements[node_id]):
            result.append(node_id)
    return result


def graph_counts(graph: Mapping[str, object]) -> dict[str, int]:
    validate_research_graph(graph)
    nodes = graph["nodes"]
    edges = graph["edges"]
    assert isinstance(nodes, list) and isinstance(edges, list)
    hard_edges = sum(1 for edge in edges if isinstance(edge, dict) and edge.get("type") == "requires")
    return {"nodes": len(nodes), "edges": len(edges), "hard_dependencies": hard_edges}
