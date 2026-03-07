"""Packet-level deterministic simulation for foundational labs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from routeforge.model.packet import BROADCAST_MAC, EthernetFrame
from routeforge.runtime.router import Router


@dataclass(frozen=True)
class EgressFrame:
    interface_name: str
    vlan_id: int | None
    src_mac: str
    dst_mac: str


@dataclass(frozen=True)
class FrameOutcome:
    action: str
    reason: str
    ingress_interface: str
    ingress_vlan: int | None
    egress: tuple[EgressFrame, ...]
    checkpoints: tuple[str, ...]

    def to_trace_record(self, *, step: str, sequence: int) -> dict[str, Any]:
        return {
            "seq": sequence,
            "step": step,
            "action": self.action,
            "reason": self.reason,
            "ingress_interface": self.ingress_interface,
            "ingress_vlan": self.ingress_vlan,
            "egress": [
                {
                    "interface": e.interface_name,
                    "vlan_id": e.vlan_id,
                    "src_mac": e.src_mac,
                    "dst_mac": e.dst_mac,
                }
                for e in self.egress
            ],
            "checkpoints": list(self.checkpoints),
        }


class DataplaneSim:
    def __init__(self, router: Router) -> None:
        self.router = router

    def process_frame(self, *, ingress_interface: str, frame: EthernetFrame) -> FrameOutcome:
        iface = self.router.get_interface(ingress_interface)
        if iface is None:
            return FrameOutcome(
                action="DROP",
                reason="L2_UNKNOWN_INGRESS_IF",
                ingress_interface=ingress_interface,
                ingress_vlan=None,
                egress=(),
                checkpoints=("PARSE_DROP",),
            )

        errors = frame.validate()
        if errors:
            return FrameOutcome(
                action="DROP",
                reason=errors[0],
                ingress_interface=ingress_interface,
                ingress_vlan=None,
                egress=(),
                checkpoints=("PARSE_DROP",),
            )

        ingress_vlan, vlan_error = iface.ingress_vlan(frame.vlan_id)
        if vlan_error is not None:
            return FrameOutcome(
                action="DROP",
                reason=vlan_error,
                ingress_interface=ingress_interface,
                ingress_vlan=None,
                egress=(),
                checkpoints=("PARSE_OK", "VLAN_CLASSIFY", "PARSE_DROP"),
            )
        assert ingress_vlan is not None

        source_mac = frame.normalized().src_mac
        destination_mac = frame.normalized().dst_mac
        self.router.learn_mac(vlan=ingress_vlan, mac=source_mac, interface_name=ingress_interface)

        checkpoints: list[str] = ["PARSE_OK", "VLAN_CLASSIFY", "MAC_LEARN"]

        destination_interface = self.router.lookup_mac(vlan=ingress_vlan, mac=destination_mac)
        flood = destination_mac == BROADCAST_MAC or destination_interface is None

        if flood:
            checkpoints.append("L2_FLOOD")
            egress_ports = self.router.forwarding_ports(vlan=ingress_vlan, ingress_interface=ingress_interface)
            action = "FLOOD"
            reason = "L2_UNKNOWN_UNICAST_FLOOD" if destination_mac != BROADCAST_MAC else "L2_BROADCAST_FLOOD"
        else:
            if destination_interface == ingress_interface:
                return FrameOutcome(
                    action="DROP",
                    reason="L2_SAME_PORT_DESTINATION",
                    ingress_interface=ingress_interface,
                    ingress_vlan=ingress_vlan,
                    egress=(),
                    checkpoints=tuple(checkpoints + ["PARSE_DROP"]),
                )
            egress_ports = [destination_interface]
            checkpoints.append("L2_UNICAST_FORWARD")
            action = "FORWARD"
            reason = "L2_FDB_HIT"

        outgoing_frames: list[EgressFrame] = []
        for port_name in egress_ports:
            port = self.router.get_interface(port_name)
            if port is None:
                continue
            outgoing_vlan, allowed = port.egress_vlan(ingress_vlan)
            if not allowed:
                continue
            if frame.vlan_id is None and outgoing_vlan is not None and "VLAN_TAG_PUSH" not in checkpoints:
                checkpoints.append("VLAN_TAG_PUSH")
            if frame.vlan_id is not None and outgoing_vlan is None and "VLAN_TAG_POP" not in checkpoints:
                checkpoints.append("VLAN_TAG_POP")
            outgoing_frames.append(
                EgressFrame(
                    interface_name=port_name,
                    vlan_id=outgoing_vlan,
                    src_mac=source_mac,
                    dst_mac=destination_mac,
                )
            )

        if not outgoing_frames and action != "DROP":
            return FrameOutcome(
                action="DROP",
                reason="L2_NO_ELIGIBLE_EGRESS",
                ingress_interface=ingress_interface,
                ingress_vlan=ingress_vlan,
                egress=(),
                checkpoints=tuple(checkpoints + ["PARSE_DROP"]),
            )

        return FrameOutcome(
            action=action,
            reason=reason,
            ingress_interface=ingress_interface,
            ingress_vlan=ingress_vlan,
            egress=tuple(outgoing_frames),
            checkpoints=tuple(checkpoints),
        )
