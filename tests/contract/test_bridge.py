from __future__ import annotations

from dataclasses import replace

import pytest

from routeforge.runtime.bridge import Bridge, BridgeMessage, BridgeValidationError, validate_message


def _route_install_message() -> BridgeMessage:
    return BridgeMessage(
        schema_version=1,
        message_id="m-1",
        message_type="ROUTE_INSTALL",
        source_sim="CONTROLPLANE",
        target_sim="DATAPLANE",
        sim_time_ms=10,
        priority=100,
        node_id="R1",
        correlation_id="c-1",
        payload={
            "prefix": "10.0.0.0",
            "prefix_len": 24,
            "protocol": "OSPF",
            "next_hop": "192.0.2.1",
            "out_if": "eth0",
            "admin_distance": 110,
            "metric": 10,
        },
    )


def test_validate_message_accepts_valid_route_install() -> None:
    validate_message(_route_install_message())


def test_validate_message_rejects_wrong_direction() -> None:
    message = replace(
        _route_install_message(),
        source_sim="DATAPLANE",
        target_sim="CONTROLPLANE",
    )
    with pytest.raises(BridgeValidationError, match="source_sim"):
        validate_message(message)


def test_validate_message_rejects_unknown_payload_key() -> None:
    payload = dict(_route_install_message().payload)
    payload["surprise"] = "nope"
    message = replace(_route_install_message(), payload=payload)
    with pytest.raises(BridgeValidationError, match="unknown keys"):
        validate_message(message)


def test_bridge_apply_is_idempotent_and_traced() -> None:
    bridge = Bridge()
    message = _route_install_message()

    emit_event = bridge.emit(message)
    assert emit_event.checkpoint == "BRIDGE_EMIT"

    first_apply = bridge.apply(message)
    second_apply = bridge.apply(message)

    assert first_apply is True
    assert second_apply is False
    assert [event.checkpoint for event in bridge.trace_events] == [
        "BRIDGE_EMIT",
        "BRIDGE_APPLY",
    ]
    assert bridge.trace_events[0].correlation_id == bridge.trace_events[1].correlation_id
