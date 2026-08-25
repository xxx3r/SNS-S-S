from __future__ import annotations

import pytest

from automation.routing import route_daily_slot


def candidate(
    quest_id: str,
    *,
    priority: str,
    active_index: int,
    eligible: bool = True,
    executable: bool = True,
    blocker_scope: str = "none",
) -> dict[str, object]:
    return {
        "quest_id": quest_id,
        "priority": priority,
        "active_index": active_index,
        "eligible": eligible,
        "executable": executable,
        "blocker_scope": blocker_scope,
    }


def test_local_p0_stop_escalates_and_routes_to_independent_p0() -> None:
    result = route_daily_slot(
        [
            candidate(
                "QST-STOR-0002",
                priority="P0",
                active_index=1,
                executable=False,
                blocker_scope="local",
            ),
            candidate("QST-ARCI-0001", priority="P0", active_index=6),
        ]
    )

    assert result == {
        "decision": "AUTHORIZE",
        "selected_quest_id": "QST-ARCI-0001",
        "escalated_quest_ids": ["QST-STOR-0002"],
        "reason": "highest-priority executable eligible route",
    }


def test_global_or_shared_stop_prevents_alternate_authorization() -> None:
    for scope in ("global", "shared", "protected"):
        result = route_daily_slot(
            [
                candidate(
                    "QST-STOR-0002",
                    priority="P0",
                    active_index=1,
                    executable=False,
                    blocker_scope=scope,
                ),
                candidate("QST-ARCI-0001", priority="P0", active_index=6),
            ]
        )
        assert result["decision"] == "NO_AUTHORIZATION"
        assert result["selected_quest_id"] is None
        assert result["escalated_quest_ids"] == ["QST-STOR-0002"]


def test_valid_live_owner_beats_nominal_priority_route() -> None:
    result = route_daily_slot(
        [
            candidate("QST-STOR-0002", priority="P0", active_index=1),
            candidate("QST-SIM-0002", priority="P1", active_index=2),
        ],
        live_owner_quest_id="QST-SIM-0002",
    )
    assert result["decision"] == "CONTINUE_OWNER"
    assert result["selected_quest_id"] == "QST-SIM-0002"
    assert result["escalated_quest_ids"] == []


def test_priority_then_active_index_is_deterministic() -> None:
    result = route_daily_slot(
        [
            candidate("QST-ARCI-0001", priority="P0", active_index=6),
            candidate("QST-STOR-0002", priority="P0", active_index=1),
            candidate("QST-PV-0001", priority="P1", active_index=4),
        ]
    )
    assert result["decision"] == "AUTHORIZE"
    assert result["selected_quest_id"] == "QST-STOR-0002"


def test_invalid_routing_input_fails_closed() -> None:
    with pytest.raises(ValueError, match="blocker_scope"):
        route_daily_slot(
            [candidate("QST-STOR-0002", priority="P0", active_index=1, blocker_scope="mystery")]
        )
