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

    def _select_known_unicast_egress(self, *, ingress_interface: str, destination_interface: str) -> tuple[list[str], str]:
        # TODO(student): implement deterministic known-unicast forwarding selection.
        raise NotImplementedError("TODO: implement DataplaneSim._select_known_unicast_egress")

    def _vlan_translation_checkpoint(self, *, ingress_vlan_id: int | None, egress_vlan_id: int | None) -> str | None:
        # Keep no-translation paths working for earlier labs.
        if ingress_vlan_id is None and egress_vlan_id is None:
            return None
        if ingress_vlan_id is not None and egress_vlan_id is not None:
            return None
        # TODO(student): emit VLAN_TAG_PUSH / VLAN_TAG_POP for translation paths.
        raise NotImplementedError("TODO: implement DataplaneSim._vlan_translation_checkpoint")
        return None

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
            assert destination_interface is not None
            try:
                egress_ports, reason = self._select_known_unicast_egress(
                    ingress_interface=ingress_interface,
                    destination_interface=destination_interface,
                )
            except ValueError as exc:
                if str(exc) != "L2_SAME_PORT_DESTINATION":
                    raise
                return FrameOutcome(
                    action="DROP",
                    reason="L2_SAME_PORT_DESTINATION",
                    ingress_interface=ingress_interface,
                    ingress_vlan=ingress_vlan,
                    egress=(),
                    checkpoints=tuple(checkpoints + ["PARSE_DROP"]),
                )
            checkpoints.append("L2_UNICAST_FORWARD")
            action = "FORWARD"

        outgoing_frames: list[EgressFrame] = []
        for port_name in egress_ports:
            port = self.router.get_interface(port_name)
            if port is None:
                continue
            outgoing_vlan, allowed = port.egress_vlan(ingress_vlan)
            if not allowed:
                continue
            translation_checkpoint = self._vlan_translation_checkpoint(
                ingress_vlan_id=frame.vlan_id,
                egress_vlan_id=outgoing_vlan,
            )
            if translation_checkpoint is not None and translation_checkpoint not in checkpoints:
                checkpoints.append(translation_checkpoint)
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
