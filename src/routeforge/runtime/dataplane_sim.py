"""Packet-level deterministic simulation for foundational labs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from routeforge.model.packet import EthernetFrame
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


@dataclass(frozen=True)
class ForwardingPlan:
    action: str
    reason: str
    egress_ports: tuple[str, ...]
    checkpoint: str


@dataclass(frozen=True)
class EgressVlanPlan:
    allowed: bool
    egress_vlan_id: int | None
    checkpoint: str | None


class DataplaneSim:
    def __init__(self, router: Router) -> None:
        self.router = router

    def _determine_forwarding_plan(
        self,
        *,
        ingress_interface: str,
        ingress_vlan: int,
        destination_mac: str,
    ) -> ForwardingPlan:
        # TODO(student): implement deterministic L2 forwarding plan decisions.
        raise NotImplementedError("TODO: implement DataplaneSim._determine_forwarding_plan")

    def _determine_egress_vlan_plan(
        self,
        *,
        ingress_vlan: int,
        ingress_tag: int | None,
        egress_port_name: str,
    ) -> EgressVlanPlan:
        # TODO(student): implement deterministic egress VLAN admission and tag rewrite plan.
        raise NotImplementedError("TODO: implement DataplaneSim._determine_egress_vlan_plan")

    def process_frame(
        self, *, ingress_interface: str, frame: EthernetFrame
    ) -> FrameOutcome:
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
        self.router.learn_mac(
            vlan=ingress_vlan, mac=source_mac, interface_name=ingress_interface
        )

        checkpoints: list[str] = ["PARSE_OK", "VLAN_CLASSIFY", "MAC_LEARN"]

        plan = self._determine_forwarding_plan(
            ingress_interface=ingress_interface,
            ingress_vlan=ingress_vlan,
            destination_mac=destination_mac,
        )
        if plan.action == "DROP":
            return FrameOutcome(
                action="DROP",
                reason=plan.reason,
                ingress_interface=ingress_interface,
                ingress_vlan=ingress_vlan,
                egress=(),
                checkpoints=tuple(checkpoints + [plan.checkpoint]),
            )

        checkpoints.append(plan.checkpoint)
        egress_ports = list(plan.egress_ports)
        action = plan.action
        reason = plan.reason

        outgoing_frames: list[EgressFrame] = []
        for port_name in egress_ports:
            plan = self._determine_egress_vlan_plan(
                ingress_vlan=ingress_vlan,
                ingress_tag=frame.vlan_id,
                egress_port_name=port_name,
            )
            if not plan.allowed:
                continue
            if plan.checkpoint is not None and plan.checkpoint not in checkpoints:
                checkpoints.append(plan.checkpoint)
            outgoing_frames.append(
                EgressFrame(
                    interface_name=port_name,
                    vlan_id=plan.egress_vlan_id,
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
