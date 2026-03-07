"""Executable lab scenarios for early foundational labs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Protocol

from routeforge.model.packet import ETHERTYPE_IPV4, EthernetFrame, IPv4Header
from routeforge.runtime.dataplane_sim import DataplaneSim
from routeforge.runtime.l3 import (
    ForwardingDecision,
    IcmpControlDecision,
    IPv4Packet,
    RibTable,
    RouteEntry,
    explain_drop,
    forward_packet,
    icmp_control,
)
from routeforge.runtime.interface import Interface
from routeforge.runtime.adjacency import ArpAdjacencyTable
from routeforge.runtime.router import Router
from routeforge.runtime.transport import TcpFsm, classify_flow, validate_udp
from routeforge.runtime.bfd import BfdSession
from routeforge.runtime.policy_acl import AclRule, evaluate_acl
from routeforge.runtime.nat44 import Nat44Table
from routeforge.runtime.qos import QosEngine
from routeforge.runtime.bgp import (
    BgpPath,
    apply_export_policy,
    bgp_session_transition,
    convergence_mark,
    route_reflect,
    select_best_path,
)
from routeforge.runtime.capstone import ScenarioState, apply_step, convergence_assert
from routeforge.runtime.observability import emit_telemetry, readiness_check
from routeforge.runtime.tunnel_ipsec import decapsulate, encapsulate, evaluate_ipsec_policy, lookup_sa
from routeforge.runtime.ospf import (
    AreaRoute,
    DrCandidate,
    LsaRecord,
    Lsdb,
    elect_dr_bdr,
    failover_dr_bdr,
    neighbor_hello_transition,
    neighbor_state_changed,
    next_hop_for_destination,
    originate_summaries,
    run_spf,
)
from routeforge.runtime.stp import (
    Bridge,
    BridgeID,
    Link,
    PortRef,
    bpdu_guard_decision,
    compute_stp,
    remove_link,
    role_changes,
)


class TraceableOutcome(Protocol):
    checkpoints: tuple[str, ...]

    def to_trace_record(self, *, step: str, sequence: int) -> dict[str, Any]:
        ...


@dataclass(frozen=True)
class LabStepResult:
    name: str
    passed: bool
    detail: str
    outcome: TraceableOutcome


@dataclass(frozen=True)
class LabRunResult:
    lab_id: str
    passed: bool
    steps: tuple[LabStepResult, ...]
    checkpoints: tuple[str, ...]
    trace_records: tuple[dict[str, Any], ...]


@dataclass(frozen=True)
class StpOutcome:
    action: str
    reason: str
    root_node_id: str
    port_roles: dict[tuple[str, str], str]
    checkpoints: tuple[str, ...]

    def to_trace_record(self, *, step: str, sequence: int) -> dict[str, Any]:
        return {
            "seq": sequence,
            "step": step,
            "action": self.action,
            "reason": self.reason,
            "root_node_id": self.root_node_id,
            "port_roles": [f"{node}:{port}={role}" for (node, port), role in sorted(self.port_roles.items())],
            "checkpoints": list(self.checkpoints),
        }


@dataclass(frozen=True)
class ArpOutcome:
    action: str
    reason: str
    next_hop_ip: str
    checkpoints: tuple[str, ...]
    released_packets: tuple[str, ...] = ()

    def to_trace_record(self, *, step: str, sequence: int) -> dict[str, Any]:
        return {
            "seq": sequence,
            "step": step,
            "action": self.action,
            "reason": self.reason,
            "next_hop_ip": self.next_hop_ip,
            "released_packets": list(self.released_packets),
            "checkpoints": list(self.checkpoints),
        }


@dataclass(frozen=True)
class L3Outcome:
    action: str
    reason: str
    destination_ip: str
    checkpoints: tuple[str, ...]
    details: dict[str, Any]

    def to_trace_record(self, *, step: str, sequence: int) -> dict[str, Any]:
        return {
            "seq": sequence,
            "step": step,
            "action": self.action,
            "reason": self.reason,
            "destination_ip": self.destination_ip,
            "details": self.details,
            "checkpoints": list(self.checkpoints),
        }


@dataclass(frozen=True)
class OspfOutcome:
    action: str
    reason: str
    checkpoints: tuple[str, ...]
    details: dict[str, Any]

    def to_trace_record(self, *, step: str, sequence: int) -> dict[str, Any]:
        return {
            "seq": sequence,
            "step": step,
            "action": self.action,
            "reason": self.reason,
            "details": self.details,
            "checkpoints": list(self.checkpoints),
        }


@dataclass(frozen=True)
class FeatureOutcome:
    action: str
    reason: str
    checkpoints: tuple[str, ...]
    details: dict[str, Any]

    def to_trace_record(self, *, step: str, sequence: int) -> dict[str, Any]:
        return {
            "seq": sequence,
            "step": step,
            "action": self.action,
            "reason": self.reason,
            "details": self.details,
            "checkpoints": list(self.checkpoints),
        }


def _unique_checkpoints(outcomes: list[TraceableOutcome]) -> tuple[str, ...]:
    seen: set[str] = set()
    ordered: list[str] = []
    for outcome in outcomes:
        for checkpoint in outcome.checkpoints:
            if checkpoint not in seen:
                seen.add(checkpoint)
                ordered.append(checkpoint)
    return tuple(ordered)


def _result(lab_id: str, steps: list[LabStepResult]) -> LabRunResult:
    outcomes = [step.outcome for step in steps]
    checkpoints = _unique_checkpoints(outcomes)
    traces = tuple(
        step.outcome.to_trace_record(step=step.name, sequence=index + 1)
        for index, step in enumerate(steps)
    )
    return LabRunResult(
        lab_id=lab_id,
        passed=all(step.passed for step in steps),
        steps=tuple(steps),
        checkpoints=checkpoints,
        trace_records=traces,
    )


def _lab01() -> LabRunResult:
    router = Router(node_id="R1")
    router.add_interface(Interface(name="eth0", mode="access", access_vlan=1))
    router.add_interface(Interface(name="eth1", mode="access", access_vlan=1))
    sim = DataplaneSim(router)

    valid_frame = EthernetFrame(
        src_mac="00:11:22:33:44:55",
        dst_mac="00:11:22:33:44:66",
        ethertype=ETHERTYPE_IPV4,
        payload=IPv4Header(src_ip="192.0.2.10", dst_ip="192.0.2.20"),
    )
    valid_outcome = sim.process_frame(ingress_interface="eth0", frame=valid_frame)
    valid_passed = valid_outcome.action == "FLOOD" and "PARSE_OK" in valid_outcome.checkpoints

    invalid_frame = EthernetFrame(
        src_mac="zz:11:22:33:44:55",
        dst_mac="00:11:22:33:44:66",
        ethertype=ETHERTYPE_IPV4,
        payload=IPv4Header(src_ip="192.0.2.10", dst_ip="192.0.2.20"),
    )
    invalid_outcome = sim.process_frame(ingress_interface="eth0", frame=invalid_frame)
    invalid_passed = invalid_outcome.action == "DROP" and "PARSE_DROP" in invalid_outcome.checkpoints

    return _result(
        "lab01_frame_and_headers",
        [
            LabStepResult(
                name="valid_frame_parses",
                passed=valid_passed,
                detail="valid frame is accepted and forwarded/flooded",
                outcome=valid_outcome,
            ),
            LabStepResult(
                name="invalid_frame_drops",
                passed=invalid_passed,
                detail="invalid frame is rejected with parse-drop checkpoint",
                outcome=invalid_outcome,
            ),
        ],
    )


def _score_student_bool_cases(
    *,
    function_name: str,
    function: Callable[..., bool],
    cases: list[tuple[tuple[Any, ...], bool]],
) -> tuple[bool, str, dict[str, Any]]:
    failures: list[str] = []
    for index, (args, expected) in enumerate(cases, start=1):
        try:
            actual = function(*args)
        except NotImplementedError as exc:
            return (
                False,
                f"not implemented: {function_name} ({exc})",
                {"error": "NotImplementedError", "function": function_name},
            )
        except Exception as exc:  # pragma: no cover - defensive student-facing guardrail
            return (
                False,
                f"runtime error: {function_name} -> {type(exc).__name__}: {exc}",
                {"error": type(exc).__name__, "function": function_name},
            )
        if not isinstance(actual, bool):
            return (
                False,
                f"{function_name} must return bool (got {type(actual).__name__})",
                {"error": "INVALID_RETURN_TYPE", "function": function_name},
            )
        if actual != expected:
            failures.append(f"case{index}: expected={expected} got={actual}")

    if failures:
        return (
            False,
            f"{function_name} failed: {'; '.join(failures)}",
            {"function": function_name, "failures": failures},
        )
    return (
        True,
        f"{function_name} passed {len(cases)} case(s)",
        {"function": function_name, "cases": len(cases)},
    )


def _lab01_student() -> LabRunResult:
    try:
        from routeforge.student import lab01 as student_lab01
    except Exception as exc:  # pragma: no cover - defensive student-facing guardrail
        import_outcome = FeatureOutcome(
            action="ERROR",
            reason="STUDENT_MODULE_IMPORT_FAILED",
            checkpoints=("PARSE_DROP",),
            details={"error": f"{type(exc).__name__}: {exc}", "module": "routeforge.student.lab01"},
        )
        return _result(
            "lab01_frame_and_headers",
            [
                LabStepResult(
                    name="student_module_import",
                    passed=False,
                    detail="failed to import student module",
                    outcome=import_outcome,
                )
            ],
        )

    mac_passed, mac_detail, mac_details = _score_student_bool_cases(
        function_name="validate_mac",
        function=student_lab01.validate_mac,
        cases=[
            (("00:11:22:33:44:55",), True),
            (("zz:11:22:33:44:55",), False),
            (("00:11:22:33:44",), False),
        ],
    )
    ip_passed, ip_detail, ip_details = _score_student_bool_cases(
        function_name="validate_ipv4",
        function=student_lab01.validate_ipv4,
        cases=[
            (("192.0.2.10",), True),
            (("203.0.113.20",), True),
            (("999.0.2.10",), False),
        ],
    )
    ttl_passed, ttl_detail, ttl_details = _score_student_bool_cases(
        function_name="validate_ttl",
        function=student_lab01.validate_ttl,
        cases=[
            ((64,), True),
            ((1,), True),
            ((0,), False),
        ],
    )
    frame_passed, frame_detail, frame_details = _score_student_bool_cases(
        function_name="frame_should_parse",
        function=student_lab01.frame_should_parse,
        cases=[
            (("00:11:22:33:44:55", "00:11:22:33:44:66", "192.0.2.10", "192.0.2.20", 64), True),
            (("zz:11:22:33:44:55", "00:11:22:33:44:66", "192.0.2.10", "192.0.2.20", 64), False),
            (("00:11:22:33:44:55", "00:11:22:33:44:66", "192.0.2.10", "999.0.2.20", 64), False),
            (("00:11:22:33:44:55", "00:11:22:33:44:66", "192.0.2.10", "192.0.2.20", 0), False),
        ],
    )

    hint = "edit src/routeforge/student/lab01.py to implement TODO functions"
    return _result(
        "lab01_frame_and_headers",
        [
            LabStepResult(
                name="student_validate_mac",
                passed=mac_passed,
                detail=f"{mac_detail} ({hint})",
                outcome=FeatureOutcome(
                    action="GRADE",
                    reason="STUDENT_MAC_VALIDATION",
                    checkpoints=(),
                    details=mac_details,
                ),
            ),
            LabStepResult(
                name="student_validate_ipv4",
                passed=ip_passed,
                detail=f"{ip_detail} ({hint})",
                outcome=FeatureOutcome(
                    action="GRADE",
                    reason="STUDENT_IPV4_VALIDATION",
                    checkpoints=(),
                    details=ip_details,
                ),
            ),
            LabStepResult(
                name="student_validate_ttl",
                passed=ttl_passed,
                detail=f"{ttl_detail} ({hint})",
                outcome=FeatureOutcome(
                    action="GRADE",
                    reason="STUDENT_TTL_VALIDATION",
                    checkpoints=(),
                    details=ttl_details,
                ),
            ),
            LabStepResult(
                name="student_frame_parse_decision",
                passed=frame_passed,
                detail=f"{frame_detail} ({hint})",
                outcome=FeatureOutcome(
                    action="GRADE",
                    reason="STUDENT_PARSE_GATE",
                    checkpoints=("PARSE_OK", "PARSE_DROP"),
                    details=frame_details,
                ),
            ),
        ],
    )


def _lab02() -> LabRunResult:
    router = Router(node_id="R1")
    router.add_interface(Interface(name="eth0", mode="access", access_vlan=1))
    router.add_interface(Interface(name="eth1", mode="access", access_vlan=1))
    router.add_interface(Interface(name="eth2", mode="access", access_vlan=1))
    sim = DataplaneSim(router)

    first = sim.process_frame(
        ingress_interface="eth0",
        frame=EthernetFrame(
            src_mac="00:aa:00:00:00:01",
            dst_mac="00:bb:00:00:00:01",
            ethertype=ETHERTYPE_IPV4,
            payload=IPv4Header(src_ip="198.51.100.1", dst_ip="198.51.100.2"),
        ),
    )
    first_ports = sorted(frame.interface_name for frame in first.egress)
    first_passed = first.action == "FLOOD" and first_ports == ["eth1", "eth2"]

    second = sim.process_frame(
        ingress_interface="eth1",
        frame=EthernetFrame(
            src_mac="00:bb:00:00:00:01",
            dst_mac="00:aa:00:00:00:01",
            ethertype=ETHERTYPE_IPV4,
            payload=IPv4Header(src_ip="198.51.100.2", dst_ip="198.51.100.1"),
        ),
    )
    second_ports = [frame.interface_name for frame in second.egress]
    second_passed = second.action == "FORWARD" and second_ports == ["eth0"]

    return _result(
        "lab02_mac_learning_switch",
        [
            LabStepResult(
                name="unknown_unicast_flood",
                passed=first_passed,
                detail="unknown unicast floods to all non-ingress ports",
                outcome=first,
            ),
            LabStepResult(
                name="known_unicast_forward",
                passed=second_passed,
                detail="MAC learning enables deterministic unicast forwarding",
                outcome=second,
            ),
        ],
    )


def _lab03() -> LabRunResult:
    router = Router(node_id="R1")
    router.add_interface(Interface(name="eth0", mode="access", access_vlan=10))
    router.add_interface(Interface(name="eth1", mode="trunk", native_vlan=1, allowed_vlans={1, 10, 20}))
    router.add_interface(Interface(name="eth2", mode="access", access_vlan=20))
    sim = DataplaneSim(router)

    to_trunk = sim.process_frame(
        ingress_interface="eth0",
        frame=EthernetFrame(
            src_mac="00:10:00:00:00:01",
            dst_mac="00:10:00:00:00:ff",
            ethertype=ETHERTYPE_IPV4,
            payload=IPv4Header(src_ip="203.0.113.10", dst_ip="203.0.113.20"),
        ),
    )
    trunk_tags = [frame.vlan_id for frame in to_trunk.egress if frame.interface_name == "eth1"]
    to_trunk_passed = to_trunk.action == "FLOOD" and trunk_tags == [10]

    to_access = sim.process_frame(
        ingress_interface="eth1",
        frame=EthernetFrame(
            src_mac="00:20:00:00:00:01",
            dst_mac="00:20:00:00:00:ff",
            ethertype=ETHERTYPE_IPV4,
            payload=IPv4Header(src_ip="203.0.113.30", dst_ip="203.0.113.40"),
            vlan_id=20,
        ),
    )
    access_tags = [frame.vlan_id for frame in to_access.egress if frame.interface_name == "eth2"]
    to_access_passed = to_access.action == "FLOOD" and access_tags == [None]

    return _result(
        "lab03_vlan_and_trunks",
        [
            LabStepResult(
                name="access_to_trunk_tag_push",
                passed=to_trunk_passed,
                detail="access VLAN traffic is tagged when sent over trunk",
                outcome=to_trunk,
            ),
            LabStepResult(
                name="trunk_to_access_tag_pop",
                passed=to_access_passed,
                detail="tagged trunk traffic is untagged on matching access port",
                outcome=to_access,
            ),
        ],
    )


def _lab04() -> LabRunResult:
    bridges = [
        Bridge(node_id="S1", bridge_id=BridgeID(priority=32768, mac="00:00:00:00:00:01")),
        Bridge(node_id="S2", bridge_id=BridgeID(priority=32768, mac="00:00:00:00:00:02")),
        Bridge(node_id="S3", bridge_id=BridgeID(priority=32768, mac="00:00:00:00:00:03")),
    ]
    links = [
        Link(a=PortRef("S1", "Gi0/1"), b=PortRef("S2", "Gi0/1"), cost=4),
        Link(a=PortRef("S1", "Gi0/2"), b=PortRef("S3", "Gi0/1"), cost=4),
        Link(a=PortRef("S2", "Gi0/2"), b=PortRef("S3", "Gi0/2"), cost=4),
    ]
    result = compute_stp(bridges, links)

    root_step = StpOutcome(
        action="SELECT",
        reason="STP_ROOT_ELECTED",
        root_node_id=result.root_node_id,
        port_roles=result.port_roles,
        checkpoints=("STP_ROOT_CHANGE",),
    )
    root_passed = result.root_node_id == "S1"

    role_step = StpOutcome(
        action="SELECT",
        reason="STP_PORT_ROLES_COMPUTED",
        root_node_id=result.root_node_id,
        port_roles=result.port_roles,
        checkpoints=("STP_PORT_ROLE_CHANGE",),
    )
    role_passed = (
        result.port_roles.get(("S2", "Gi0/2")) == "DESIGNATED"
        and result.port_roles.get(("S3", "Gi0/2")) == "ALTERNATE"
        and result.port_roles.get(("S2", "Gi0/1")) == "ROOT"
        and result.port_roles.get(("S3", "Gi0/1")) == "ROOT"
    )

    return _result(
        "lab04_stp",
        [
            LabStepResult(
                name="stp_root_election",
                passed=root_passed,
                detail="lowest bridge ID is selected as deterministic root",
                outcome=root_step,
            ),
            LabStepResult(
                name="stp_port_roles",
                passed=role_passed,
                detail="root/designated/alternate roles are assigned deterministically",
                outcome=role_step,
            ),
        ],
    )


def _lab05() -> LabRunResult:
    bridges = [
        Bridge(node_id="S1", bridge_id=BridgeID(priority=32768, mac="00:00:00:00:00:01")),
        Bridge(node_id="S2", bridge_id=BridgeID(priority=32768, mac="00:00:00:00:00:02")),
        Bridge(node_id="S3", bridge_id=BridgeID(priority=32768, mac="00:00:00:00:00:03")),
    ]
    base_links = [
        Link(a=PortRef("S1", "Gi0/1"), b=PortRef("S2", "Gi0/1"), cost=4),
        Link(a=PortRef("S1", "Gi0/2"), b=PortRef("S3", "Gi0/1"), cost=4),
        Link(a=PortRef("S2", "Gi0/2"), b=PortRef("S3", "Gi0/2"), cost=4),
    ]
    before = compute_stp(bridges, base_links)
    after = compute_stp(
        bridges,
        remove_link(base_links, a=("S1", "Gi0/2"), b=("S3", "Gi0/1")),
    )
    changes = role_changes(before, after)

    topo_outcome = StpOutcome(
        action="SELECT",
        reason="STP_TOPOLOGY_RECONVERGED",
        root_node_id=after.root_node_id,
        port_roles=after.port_roles,
        checkpoints=("STP_TOPOLOGY_CHANGE",),
    )
    topology_passed = (
        len(changes) > 0
        and after.root_node_id == "S1"
        and after.root_port_by_node.get("S3") == "Gi0/2"
    )

    guard = bpdu_guard_decision(port=("S2", "Gi0/10"), edge_port=True, bpdu_received=True)
    guard_outcome = StpOutcome(
        action="DROP",
        reason=guard.reason,
        root_node_id=after.root_node_id,
        port_roles=after.port_roles,
        checkpoints=("STP_GUARD_ACTION",),
    )
    guard_passed = guard.action == "ERRDISABLE"

    return _result(
        "lab05_stp_convergence_and_protection",
        [
            LabStepResult(
                name="stp_topology_change",
                passed=topology_passed,
                detail="link failure triggers deterministic STP re-convergence",
                outcome=topo_outcome,
            ),
            LabStepResult(
                name="stp_guard_action",
                passed=guard_passed,
                detail="BPDU guard puts an edge port into errdisable state",
                outcome=guard_outcome,
            ),
        ],
    )


def _lab06() -> LabRunResult:
    table = ArpAdjacencyTable()
    next_hop = "192.0.2.1"

    send_request = table.queue_packet(next_hop_ip=next_hop, packet_id="pkt-1")
    request_outcome = ArpOutcome(
        action="QUEUE",
        reason="ARP_MISS",
        next_hop_ip=next_hop,
        checkpoints=("ARP_REQUEST_TX",),
    )
    request_passed = send_request and table.lookup(next_hop) is None

    released = table.resolve(next_hop_ip=next_hop, mac="00:de:ad:be:ef:01")
    reply_outcome = ArpOutcome(
        action="INSTALL",
        reason="ARP_RESOLVED",
        next_hop_ip=next_hop,
        checkpoints=("ARP_REPLY_RX", "ARP_CACHE_UPDATE"),
        released_packets=tuple(released),
    )
    reply_passed = table.lookup(next_hop) == "00:de:ad:be:ef:01" and released == ["pkt-1"]

    return _result(
        "lab06_arp_and_adjacency",
        [
            LabStepResult(
                name="arp_request_and_queue",
                passed=request_passed,
                detail="ARP miss queues packet and emits request",
                outcome=request_outcome,
            ),
            LabStepResult(
                name="arp_reply_and_cache_update",
                passed=reply_passed,
                detail="ARP reply installs cache entry and releases pending packets",
                outcome=reply_outcome,
            ),
        ],
    )


def _lab07() -> LabRunResult:
    rib = RibTable()
    rib.install(
        RouteEntry(
            prefix="10.0.0.0",
            prefix_len=8,
            next_hop="192.0.2.1",
            out_if="eth0",
            protocol="static",
            admin_distance=1,
            metric=20,
        )
    )
    rib.install(
        RouteEntry(
            prefix="10.1.0.0",
            prefix_len=16,
            next_hop="192.0.2.2",
            out_if="eth1",
            protocol="ospf",
            admin_distance=110,
            metric=10,
        )
    )

    selected = rib.lookup("10.1.2.3")
    outcome = L3Outcome(
        action="SELECT",
        reason="LPM_MATCH",
        destination_ip="10.1.2.3",
        checkpoints=("RIB_ROUTE_INSTALL", "ROUTE_LOOKUP", "ROUTE_SELECT"),
        details={
            "selected_prefix": f"{selected.prefix}/{selected.prefix_len}" if selected else "none",
            "out_if": selected.out_if if selected else "none",
        },
    )
    passed = selected is not None and selected.prefix_len == 16 and selected.out_if == "eth1"

    return _result(
        "lab07_ipv4_subnet_and_rib",
        [
            LabStepResult(
                name="rib_install_and_lpm",
                passed=passed,
                detail="route install and deterministic longest-prefix selection",
                outcome=outcome,
            )
        ],
    )


def _forward_outcome(packet: IPv4Packet, decision: ForwardingDecision, checkpoints: tuple[str, ...]) -> L3Outcome:
    return L3Outcome(
        action=decision.action,
        reason=decision.reason,
        destination_ip=packet.dst_ip,
        checkpoints=checkpoints,
        details={
            "ttl_after": decision.ttl_after,
            "out_if": decision.out_if,
            "next_hop": decision.next_hop,
        },
    )


def _lab08() -> LabRunResult:
    rib = RibTable()
    rib.install(
        RouteEntry(
            prefix="203.0.113.0",
            prefix_len=24,
            next_hop="192.0.2.9",
            out_if="eth2",
            protocol="ospf",
            admin_distance=110,
            metric=5,
        )
    )

    forward_packet_input = IPv4Packet(src_ip="198.51.100.10", dst_ip="203.0.113.10", ttl=5)
    decision_ok = forward_packet(forward_packet_input, rib.lookup(forward_packet_input.dst_ip))
    ok_outcome = _forward_outcome(forward_packet_input, decision_ok, ("TTL_DECREMENT", "FIB_FORWARD"))
    ok_passed = decision_ok.action == "FORWARD" and decision_ok.ttl_after == 4

    drop_packet_input = IPv4Packet(src_ip="198.51.100.10", dst_ip="198.18.0.10", ttl=4)
    decision_drop = forward_packet(drop_packet_input, rib.lookup(drop_packet_input.dst_ip))
    drop_outcome = _forward_outcome(drop_packet_input, decision_drop, ("FIB_DROP",))
    drop_passed = decision_drop.action == "DROP" and decision_drop.reason == "NO_ROUTE"

    return _result(
        "lab08_fib_forwarding_pipeline",
        [
            LabStepResult(
                name="fib_forward_and_ttl",
                passed=ok_passed,
                detail="FIB hit forwards packet and decrements TTL",
                outcome=ok_outcome,
            ),
            LabStepResult(
                name="fib_drop_no_route",
                passed=drop_passed,
                detail="FIB miss drops packet with deterministic reason",
                outcome=drop_outcome,
            ),
        ],
    )


def _icmp_outcome(packet: IPv4Packet, decision: IcmpControlDecision, checkpoint: str) -> L3Outcome:
    return L3Outcome(
        action=decision.action,
        reason=decision.reason,
        destination_ip=packet.dst_ip,
        checkpoints=(checkpoint,),
        details={"icmp_type": decision.icmp_type},
    )


def _lab09() -> LabRunResult:
    rib = RibTable()
    rib.install(
        RouteEntry(
            prefix="203.0.113.0",
            prefix_len=24,
            next_hop="192.0.2.1",
            out_if="eth0",
            protocol="connected",
            admin_distance=0,
            metric=0,
        )
    )

    echo_packet = IPv4Packet(src_ip="198.51.100.1", dst_ip="203.0.113.5", ttl=64, icmp_type="echo_request")
    echo_decision = icmp_control(echo_packet, rib.lookup(echo_packet.dst_ip))
    echo_outcome = _icmp_outcome(echo_packet, echo_decision, "ICMP_ECHO_REPLY")
    echo_passed = echo_decision.icmp_type == "echo_reply"

    unreachable_packet = IPv4Packet(src_ip="198.51.100.1", dst_ip="198.18.0.9", ttl=64, icmp_type="echo_request")
    unreachable_decision = icmp_control(unreachable_packet, rib.lookup(unreachable_packet.dst_ip))
    unreachable_outcome = _icmp_outcome(unreachable_packet, unreachable_decision, "ICMP_UNREACHABLE")
    unreachable_passed = unreachable_decision.icmp_type == "unreachable"

    ttl_packet = IPv4Packet(src_ip="198.51.100.1", dst_ip="203.0.113.5", ttl=1, icmp_type="echo_request")
    ttl_decision = icmp_control(ttl_packet, rib.lookup(ttl_packet.dst_ip))
    ttl_outcome = _icmp_outcome(ttl_packet, ttl_decision, "ICMP_TIME_EXCEEDED")
    ttl_passed = ttl_decision.icmp_type == "time_exceeded"

    return _result(
        "lab09_icmp_and_control_responses",
        [
            LabStepResult(
                name="icmp_echo_reply",
                passed=echo_passed,
                detail="ICMP echo request returns deterministic echo reply",
                outcome=echo_outcome,
            ),
            LabStepResult(
                name="icmp_unreachable",
                passed=unreachable_passed,
                detail="missing route produces ICMP unreachable",
                outcome=unreachable_outcome,
            ),
            LabStepResult(
                name="icmp_time_exceeded",
                passed=ttl_passed,
                detail="TTL expiry produces ICMP time exceeded",
                outcome=ttl_outcome,
            ),
        ],
    )


def _lab10() -> LabRunResult:
    rib = RibTable()
    rib.install(
        RouteEntry(
            prefix="203.0.113.0",
            prefix_len=24,
            next_hop="192.0.2.1",
            out_if="eth0",
            protocol="connected",
            admin_distance=0,
            metric=0,
        )
    )

    packet = IPv4Packet(src_ip="198.51.100.10", dst_ip="203.0.113.10", ttl=1)
    decision = forward_packet(packet, rib.lookup(packet.dst_ip))
    explanation = explain_drop(decision)

    explain_outcome = L3Outcome(
        action="EXPLAIN",
        reason="DIAGNOSTICS_READY",
        destination_ip=packet.dst_ip,
        checkpoints=("EXPLAIN_CHECKPOINT",),
        details={"explain": explanation},
    )
    explain_passed = "drop_reason=TTL_EXPIRED" in explanation

    assert_outcome = L3Outcome(
        action="ASSERT",
        reason="DROP_REASON_VERIFIED",
        destination_ip=packet.dst_ip,
        checkpoints=("DROP_REASON_ASSERT",),
        details={"expected": "TTL_EXPIRED", "actual": decision.reason},
    )
    assert_passed = decision.reason == "TTL_EXPIRED"

    return _result(
        "lab10_ipv4_control_plane_diagnostics",
        [
            LabStepResult(
                name="diagnostic_explain",
                passed=explain_passed,
                detail="explain output exposes deterministic drop reason",
                outcome=explain_outcome,
            ),
            LabStepResult(
                name="diagnostic_assert_reason",
                passed=assert_passed,
                detail="drop reason assertion matches expected behavior",
                outcome=assert_outcome,
            ),
        ],
    )


def _lab11() -> LabRunResult:
    state = "DOWN"
    after_hello = neighbor_hello_transition(current_state=state, hello_received=True, dead_timer_expired=False)
    final_state = neighbor_hello_transition(
        current_state=neighbor_hello_transition(current_state=after_hello, hello_received=True, dead_timer_expired=False),
        hello_received=True,
        dead_timer_expired=False,
    )

    hello_outcome = OspfOutcome(
        action="RECEIVE",
        reason="HELLO_RX",
        checkpoints=("OSPF_HELLO_RX",),
        details={"previous_state": state, "current_state": after_hello},
    )
    hello_passed = after_hello == "INIT"

    neighbor_outcome = OspfOutcome(
        action="TRANSITION",
        reason="NEIGHBOR_FSM",
        checkpoints=("OSPF_NEIGHBOR_CHANGE",),
        details={"previous_state": state, "current_state": final_state},
    )
    neighbor_passed = final_state == "FULL" and neighbor_state_changed(state, final_state)

    return _result(
        "lab11_ospf_adjacency_fsm",
        [
            LabStepResult(
                name="ospf_hello_rx",
                passed=hello_passed,
                detail="hello packet advances neighbor from DOWN to INIT",
                outcome=hello_outcome,
            ),
            LabStepResult(
                name="ospf_neighbor_fsm_full",
                passed=neighbor_passed,
                detail="neighbor state machine converges deterministically to FULL",
                outcome=neighbor_outcome,
            ),
        ],
    )


def _lab12() -> LabRunResult:
    candidates = [
        DrCandidate(router_id="1.1.1.1", priority=100),
        DrCandidate(router_id="2.2.2.2", priority=90),
        DrCandidate(router_id="3.3.3.3", priority=80),
    ]
    dr, bdr = elect_dr_bdr(candidates)
    dr_outcome = OspfOutcome(
        action="ELECT",
        reason="DR_BDR_ELECTED",
        checkpoints=("OSPF_DR_ELECT", "OSPF_BDR_ELECT"),
        details={"dr": dr, "bdr": bdr},
    )
    dr_passed = dr == "1.1.1.1" and bdr == "2.2.2.2"

    failover_dr, failover_bdr = failover_dr_bdr(candidates, active_router_ids={"2.2.2.2", "3.3.3.3"})
    failover_outcome = OspfOutcome(
        action="ELECT",
        reason="DR_FAILOVER",
        checkpoints=("OSPF_DR_FAILOVER",),
        details={"dr": failover_dr, "bdr": failover_bdr},
    )
    failover_passed = failover_dr == "2.2.2.2"

    return _result(
        "lab12_ospf_network_types_and_dr_bdr",
        [
            LabStepResult(
                name="ospf_dr_bdr_election",
                passed=dr_passed,
                detail="DR/BDR selection follows deterministic priority and router-id ordering",
                outcome=dr_outcome,
            ),
            LabStepResult(
                name="ospf_dr_failover",
                passed=failover_passed,
                detail="BDR is promoted to DR when original DR fails",
                outcome=failover_outcome,
            ),
        ],
    )


def _lab13() -> LabRunResult:
    lsdb = Lsdb(max_age=3)
    key = ("10.0.0.0/24", "1.1.1.1")
    installed = lsdb.install(
        LsaRecord(
            lsa_id=key[0],
            advertising_router=key[1],
            sequence=1,
            age=0,
            payload={"links": ["2.2.2.2"]},
        )
    )
    install_outcome = OspfOutcome(
        action="INSTALL",
        reason="LSA_INSTALLED",
        checkpoints=("OSPF_LSA_INSTALL",),
        details={"lsa": key, "sequence": installed.sequence},
    )
    install_passed = key in lsdb.records

    refreshed = lsdb.refresh(key)
    refresh_outcome = OspfOutcome(
        action="REFRESH",
        reason="LSA_REFRESHED",
        checkpoints=("OSPF_LSA_REFRESH",),
        details={"lsa": key, "sequence": refreshed.sequence},
    )
    refresh_passed = refreshed.sequence == 2 and refreshed.age == 0

    lsdb.age_tick(1)
    lsdb.age_tick(1)
    expired = lsdb.age_tick(1)
    age_outcome = OspfOutcome(
        action="REMOVE",
        reason="LSA_AGED_OUT",
        checkpoints=("OSPF_LSA_AGE_OUT",),
        details={"expired": expired},
    )
    age_passed = key in expired and key not in lsdb.records

    return _result(
        "lab13_ospf_lsa_flooding_and_lsdb",
        [
            LabStepResult(
                name="ospf_lsa_install",
                passed=install_passed,
                detail="new LSA is installed into LSDB",
                outcome=install_outcome,
            ),
            LabStepResult(
                name="ospf_lsa_refresh",
                passed=refresh_passed,
                detail="LSA refresh increments sequence and resets age",
                outcome=refresh_outcome,
            ),
            LabStepResult(
                name="ospf_lsa_age_out",
                passed=age_passed,
                detail="max-age LSAs are removed deterministically",
                outcome=age_outcome,
            ),
        ],
    )


def _lab14() -> LabRunResult:
    graph = {
        "1.1.1.1": [("2.2.2.2", 10), ("3.3.3.3", 30)],
        "2.2.2.2": [("1.1.1.1", 10), ("3.3.3.3", 5)],
        "3.3.3.3": [("1.1.1.1", 30), ("2.2.2.2", 5)],
    }
    spf = run_spf(graph, root_router_id="1.1.1.1")
    next_hop = next_hop_for_destination(spf, destination_router_id="3.3.3.3")

    spf_outcome = OspfOutcome(
        action="RUN",
        reason="SPF_COMPLETE",
        checkpoints=("OSPF_SPF_RUN",),
        details={"cost_to_3.3.3.3": spf.cost_by_router.get("3.3.3.3"), "next_hop": next_hop},
    )
    spf_passed = spf.cost_by_router.get("3.3.3.3") == 15 and next_hop == "2.2.2.2"

    rib = RibTable()
    rib.install(
        RouteEntry(
            prefix="10.30.0.0",
            prefix_len=16,
            next_hop="192.0.2.2",
            out_if="eth1",
            protocol="ospf",
            admin_distance=110,
            metric=spf.cost_by_router.get("3.3.3.3", 9999),
        )
    )
    installed = rib.lookup("10.30.1.1")
    rib_outcome = OspfOutcome(
        action="INSTALL",
        reason="RIB_PROGRAMMED",
        checkpoints=("RIB_ROUTE_INSTALL",),
        details={"selected_prefix": f"{installed.prefix}/{installed.prefix_len}" if installed else "none"},
    )
    rib_passed = installed is not None and installed.prefix_len == 16

    return _result(
        "lab14_ospf_spf_and_route_install",
        [
            LabStepResult(
                name="ospf_spf_run",
                passed=spf_passed,
                detail="SPF produces deterministic cost and next-hop selection",
                outcome=spf_outcome,
            ),
            LabStepResult(
                name="ospf_route_install",
                passed=rib_passed,
                detail="SPF outcome installs route into RIB",
                outcome=rib_outcome,
            ),
        ],
    )


def _lab15() -> LabRunResult:
    area_routes = [
        AreaRoute(area_id=1, prefix="10.10.1.0", prefix_len=24, cost=20),
        AreaRoute(area_id=1, prefix="10.10.2.0", prefix_len=24, cost=30),
        AreaRoute(area_id=2, prefix="10.20.1.0", prefix_len=24, cost=15),
    ]
    summaries = originate_summaries(area_routes)
    summary_outcome = OspfOutcome(
        action="ORIGINATE",
        reason="SUMMARY_CREATED",
        checkpoints=("OSPF_SUMMARY_ORIGINATE",),
        details={"summaries": [f"{route.prefix}/{route.prefix_len}" for route in summaries]},
    )
    summary_passed = len(summaries) == 2

    rib = RibTable()
    for summary in summaries:
        rib.install(
            RouteEntry(
                prefix=summary.prefix,
                prefix_len=summary.prefix_len,
                next_hop="192.0.2.254",
                out_if="eth9",
                protocol="ospf_interarea",
                admin_distance=110,
                metric=summary.cost,
            )
        )
    installed = rib.lookup("10.20.42.1")
    install_outcome = OspfOutcome(
        action="INSTALL",
        reason="INTERAREA_ROUTE_INSTALLED",
        checkpoints=("OSPF_INTERAREA_ROUTE_INSTALL",),
        details={"selected_prefix": f"{installed.prefix}/{installed.prefix_len}" if installed else "none"},
    )
    install_passed = installed is not None and installed.protocol == "ospf_interarea"

    return _result(
        "lab15_ospf_multi_area_abr",
        [
            LabStepResult(
                name="ospf_summary_originate",
                passed=summary_passed,
                detail="ABR originates deterministic summaries from non-backbone areas",
                outcome=summary_outcome,
            ),
            LabStepResult(
                name="ospf_interarea_install",
                passed=install_passed,
                detail="summary routes are installed as inter-area reachability",
                outcome=install_outcome,
            ),
        ],
    )


def _lab16() -> LabRunResult:
    flow = classify_flow(
        src_ip="198.51.100.10",
        dst_ip="203.0.113.20",
        src_port=12345,
        dst_port=179,
        protocol="tcp",
    )
    flow_outcome = FeatureOutcome(
        action="CLASSIFY",
        reason="FLOW_IDENTIFIED",
        checkpoints=("FLOW_CLASSIFY",),
        details={"protocol": flow.protocol, "5tuple": f"{flow.src_ip}:{flow.src_port}->{flow.dst_ip}:{flow.dst_port}"},
    )
    flow_passed = flow.protocol == "TCP"

    tcp = TcpFsm()
    tcp.on_event("ACTIVE_OPEN")
    state = tcp.on_event("SYN_ACK_RX")
    tcp_outcome = FeatureOutcome(
        action="TRANSITION",
        reason="TCP_FSM",
        checkpoints=("TCP_STATE_CHANGE",),
        details={"state": state, "history": tcp.history},
    )
    tcp_passed = state == "ESTABLISHED"

    udp_valid = validate_udp(length_bytes=64, checksum_valid=True)
    udp_outcome = FeatureOutcome(
        action="VALIDATE",
        reason="UDP_HEADER_CHECK",
        checkpoints=("UDP_VALIDATE",),
        details={"valid": udp_valid},
    )
    udp_passed = udp_valid

    return _result(
        "lab16_udp_tcp_fundamentals",
        [
            LabStepResult(
                name="flow_classify",
                passed=flow_passed,
                detail="5-tuple flow classification is deterministic",
                outcome=flow_outcome,
            ),
            LabStepResult(
                name="tcp_state_change",
                passed=tcp_passed,
                detail="TCP state machine reaches ESTABLISHED",
                outcome=tcp_outcome,
            ),
            LabStepResult(
                name="udp_validate",
                passed=udp_passed,
                detail="UDP header validation accepts valid datagram",
                outcome=udp_outcome,
            ),
        ],
    )


def _lab17() -> LabRunResult:
    session = BfdSession(detect_mult=3)
    state = session.receive_control()
    rx_outcome = FeatureOutcome(
        action="RECEIVE",
        reason="BFD_CONTROL_PACKET",
        checkpoints=("BFD_CONTROL_RX", "BFD_STATE_CHANGE"),
        details={"state": state},
    )
    rx_passed = state == "UP"

    session.tick(control_received=False)
    session.tick(control_received=False)
    timeout_state = session.tick(control_received=False)
    timeout_outcome = FeatureOutcome(
        action="TIMEOUT",
        reason="BFD_DETECT_MULT_EXCEEDED",
        checkpoints=("BFD_TIMEOUT",),
        details={"state": timeout_state, "missed_intervals": session.missed_intervals},
    )
    timeout_passed = timeout_state == "DOWN"

    return _result(
        "lab17_bfd_for_liveness",
        [
            LabStepResult(
                name="bfd_control_rx",
                passed=rx_passed,
                detail="BFD control packet raises session to UP",
                outcome=rx_outcome,
            ),
            LabStepResult(
                name="bfd_timeout",
                passed=timeout_passed,
                detail="missing control packets trigger deterministic timeout",
                outcome=timeout_outcome,
            ),
        ],
    )


def _lab18() -> LabRunResult:
    rules = [
        AclRule(action="permit", src_prefix="10.0.0.0", src_prefix_len=8),
        AclRule(action="deny", src_prefix="0.0.0.0", src_prefix_len=0),
    ]
    permit_action = evaluate_acl(rules=rules, src_ip="10.10.10.10")
    permit_outcome = FeatureOutcome(
        action="EVALUATE",
        reason="ACL_FIRST_MATCH",
        checkpoints=("ACL_EVALUATE", "ACL_PERMIT"),
        details={"src_ip": "10.10.10.10", "action": permit_action},
    )
    permit_passed = permit_action == "permit"

    deny_action = evaluate_acl(rules=rules, src_ip="198.51.100.10")
    deny_outcome = FeatureOutcome(
        action="EVALUATE",
        reason="ACL_FIRST_MATCH",
        checkpoints=("ACL_EVALUATE", "ACL_DENY"),
        details={"src_ip": "198.51.100.10", "action": deny_action},
    )
    deny_passed = deny_action == "deny"

    return _result(
        "lab18_acl_pipeline",
        [
            LabStepResult(
                name="acl_permit",
                passed=permit_passed,
                detail="permit rule matches before implicit deny",
                outcome=permit_outcome,
            ),
            LabStepResult(
                name="acl_deny",
                passed=deny_passed,
                detail="non-matching traffic is denied deterministically",
                outcome=deny_outcome,
            ),
        ],
    )


def _lab19() -> LabRunResult:
    nat = Nat44Table(public_ip="203.0.113.254")
    created = nat.outbound_translate(inside_ip="10.0.0.10", inside_port=12345, protocol="tcp", now=0)
    create_outcome = FeatureOutcome(
        action="CREATE",
        reason="NAT_SESSION_CREATED",
        checkpoints=("NAT_SESSION_CREATE", "NAT_TRANSLATE_OUTBOUND"),
        details={"outside": f"{created.outside_ip}:{created.outside_port}"},
    )
    create_passed = created.outside_port >= 10000

    inbound = nat.inbound_translate(outside_port=created.outside_port, protocol="tcp", now=5)
    inbound_outcome = FeatureOutcome(
        action="TRANSLATE",
        reason="NAT_INBOUND_MATCH",
        checkpoints=("NAT_TRANSLATE_INBOUND",),
        details={"inside": f"{inbound.inside_ip}:{inbound.inside_port}" if inbound else "none"},
    )
    inbound_passed = inbound is not None and inbound.inside_ip == "10.0.0.10"

    expired = nat.expire(now=100, timeout=30)
    expire_outcome = FeatureOutcome(
        action="EXPIRE",
        reason="NAT_IDLE_TIMEOUT",
        checkpoints=("NAT_SESSION_EXPIRE",),
        details={"expired_count": len(expired)},
    )
    expire_passed = len(expired) == 1

    return _result(
        "lab19_nat44_stateful_translation",
        [
            LabStepResult(
                name="nat_session_create",
                passed=create_passed,
                detail="outbound flow creates deterministic NAT session",
                outcome=create_outcome,
            ),
            LabStepResult(
                name="nat_inbound_translate",
                passed=inbound_passed,
                detail="return flow matches existing NAT session",
                outcome=inbound_outcome,
            ),
            LabStepResult(
                name="nat_session_expire",
                passed=expire_passed,
                detail="idle NAT session ages out deterministically",
                outcome=expire_outcome,
            ),
        ],
    )


def _lab20() -> LabRunResult:
    qos = QosEngine()
    dscp = qos.remark_dscp(traffic_class="voice")
    remark_outcome = FeatureOutcome(
        action="REMARK",
        reason="QOS_CLASS_MARK",
        checkpoints=("QOS_REMARK",),
        details={"dscp": dscp},
    )
    remark_passed = dscp == 46

    queue_name = qos.enqueue(packet_id="pkt-voice-1", dscp=dscp)
    enqueue_outcome = FeatureOutcome(
        action="ENQUEUE",
        reason="QOS_QUEUE_ADMIT",
        checkpoints=("QOS_ENQUEUE",),
        details={"queue": queue_name},
    )
    enqueue_passed = queue_name == "high"

    packet, queue = qos.dequeue()
    dequeue_outcome = FeatureOutcome(
        action="DEQUEUE",
        reason="QOS_SCHEDULER",
        checkpoints=("QOS_DEQUEUE",),
        details={"packet": packet, "queue": queue},
    )
    dequeue_passed = packet == "pkt-voice-1" and queue == "high"

    return _result(
        "lab20_qos_marking_and_queueing",
        [
            LabStepResult(
                name="qos_remark",
                passed=remark_passed,
                detail="traffic class is remarked to deterministic DSCP",
                outcome=remark_outcome,
            ),
            LabStepResult(
                name="qos_enqueue",
                passed=enqueue_passed,
                detail="remarked packet is admitted to expected queue",
                outcome=enqueue_outcome,
            ),
            LabStepResult(
                name="qos_dequeue",
                passed=dequeue_passed,
                detail="scheduler dequeues packet in deterministic order",
                outcome=dequeue_outcome,
            ),
        ],
    )


def _lab21() -> LabRunResult:
    state = "IDLE"
    state = bgp_session_transition(current_state=state, event="TCP_CONNECTED")
    open_state = bgp_session_transition(current_state=state, event="OPEN_RX")
    established_state = bgp_session_transition(current_state=open_state, event="KEEPALIVE_RX")

    open_outcome = FeatureOutcome(
        action="RECEIVE",
        reason="BGP_OPEN",
        checkpoints=("BGP_OPEN_RX", "BGP_SESSION_CHANGE"),
        details={
            "state_after_open": open_state,
            "state_after_keepalive": established_state,
        },
    )
    open_passed = open_state == "OPENSENT" and established_state == "ESTABLISHED"

    reset_state = bgp_session_transition(current_state=established_state, event="HOLD_TIMER_EXPIRE")
    reset_outcome = FeatureOutcome(
        action="TIMEOUT",
        reason="BGP_HOLD_EXPIRE",
        checkpoints=("BGP_SESSION_CHANGE",),
        details={"state_after_timeout": reset_state},
    )
    reset_passed = reset_state == "IDLE"

    return _result(
        "lab21_bgp_session_fsm_and_transport",
        [
            LabStepResult(
                name="bgp_open_and_establish",
                passed=open_passed,
                detail="BGP OPEN and KEEPALIVE events transition the session to ESTABLISHED",
                outcome=open_outcome,
            ),
            LabStepResult(
                name="bgp_hold_timer_reset",
                passed=reset_passed,
                detail="hold timer expiry returns the BGP session to IDLE",
                outcome=reset_outcome,
            ),
        ],
    )


def _lab22() -> LabRunResult:
    paths = [
        BgpPath(
            prefix="203.0.113.0",
            prefix_len=24,
            next_hop="192.0.2.11",
            neighbor_id="2.2.2.2",
            local_pref=200,
            as_path=(65010, 65100),
            med=50,
            origin="igp",
        ),
        BgpPath(
            prefix="203.0.113.0",
            prefix_len=24,
            next_hop="192.0.2.12",
            neighbor_id="3.3.3.3",
            local_pref=200,
            as_path=(65020, 65100, 65200),
            med=10,
            origin="igp",
        ),
        BgpPath(
            prefix="203.0.113.0",
            prefix_len=24,
            next_hop="192.0.2.13",
            neighbor_id="4.4.4.4",
            local_pref=150,
            as_path=(65030, 65100),
            med=5,
            origin="igp",
        ),
    ]
    update_outcome = FeatureOutcome(
        action="RECEIVE",
        reason="BGP_UPDATE_BATCH",
        checkpoints=("BGP_UPDATE_RX",),
        details={"prefix": "203.0.113.0/24", "candidate_paths": len(paths)},
    )
    update_passed = len(paths) == 3

    best = select_best_path(paths)
    best_outcome = FeatureOutcome(
        action="SELECT",
        reason="BGP_BESTPATH",
        checkpoints=("BGP_BEST_PATH",),
        details={"next_hop": best.next_hop, "neighbor_id": best.neighbor_id, "local_pref": best.local_pref},
    )
    best_passed = best.neighbor_id == "2.2.2.2"

    return _result(
        "lab22_bgp_attributes_and_bestpath",
        [
            LabStepResult(
                name="bgp_update_receive",
                passed=update_passed,
                detail="BGP update set is ingested for best-path selection",
                outcome=update_outcome,
            ),
            LabStepResult(
                name="bgp_best_path_select",
                passed=best_passed,
                detail="deterministic best-path logic selects expected candidate",
                outcome=best_outcome,
            ),
        ],
    )


def _lab23() -> LabRunResult:
    paths = [
        BgpPath(
            prefix="203.0.113.0",
            prefix_len=24,
            next_hop="192.0.2.11",
            neighbor_id="2.2.2.2",
            local_pref=200,
            as_path=(65010, 65100),
            med=50,
            origin="igp",
        ),
        BgpPath(
            prefix="198.51.100.0",
            prefix_len=24,
            next_hop="192.0.2.12",
            neighbor_id="3.3.3.3",
            local_pref=200,
            as_path=(65020, 65100),
            med=10,
            origin="igp",
        ),
    ]
    exported = apply_export_policy(
        paths=paths,
        denied_prefixes={"203.0.113.0/24"},
        local_pref_override=250,
    )
    policy_outcome = FeatureOutcome(
        action="APPLY",
        reason="BGP_EXPORT_POLICY",
        checkpoints=("BGP_POLICY_APPLY",),
        details={"exported_count": len(exported)},
    )
    policy_passed = len(exported) == 1 and exported[0].prefix == "198.51.100.0"

    export_outcome = FeatureOutcome(
        action="EXPORT",
        reason="BGP_UPDATE_OUTBOUND",
        checkpoints=("BGP_UPDATE_EXPORT",),
        details={
            "prefixes": [f"{path.prefix}/{path.prefix_len}" for path in exported],
            "local_prefs": [path.local_pref for path in exported],
        },
    )
    export_passed = all(path.local_pref == 250 for path in exported)

    return _result(
        "lab23_bgp_policy_and_filters",
        [
            LabStepResult(
                name="bgp_policy_apply",
                passed=policy_passed,
                detail="export policy filters denied prefixes deterministically",
                outcome=policy_outcome,
            ),
            LabStepResult(
                name="bgp_update_export",
                passed=export_passed,
                detail="allowed routes are exported with policy-applied attributes",
                outcome=export_outcome,
            ),
        ],
    )


def _lab24() -> LabRunResult:
    learned = {
        "C1": ["10.10.10.0/24", "10.10.20.0/24"],
        "C2": [],
        "C3": [],
    }
    reflected = route_reflect(learned=learned, source_client="C1")
    reflect_outcome = FeatureOutcome(
        action="REFLECT",
        reason="BGP_ROUTE_REFLECTION",
        checkpoints=("BGP_RR_REFLECT",),
        details=reflected,
    )
    reflect_passed = reflected.get("C2") == learned["C1"] and reflected.get("C3") == learned["C1"]

    before = {client: ",".join(prefixes) for client, prefixes in sorted(reflected.items())}
    after = {client: ",".join(prefixes) for client, prefixes in sorted(route_reflect(learned=learned, source_client="C1").items())}
    stable = convergence_mark(before=before, after=after)
    convergence_outcome = FeatureOutcome(
        action="ASSERT",
        reason="BGP_CONVERGENCE",
        checkpoints=("BGP_CONVERGENCE_MARK",),
        details={"stable": stable},
    )
    convergence_passed = stable

    primary = BgpPath(
        prefix="10.10.10.0",
        prefix_len=24,
        next_hop="192.0.2.21",
        neighbor_id="5.5.5.5",
        local_pref=200,
        as_path=(65100, 65200),
        med=20,
        origin="igp",
    )
    secondary = BgpPath(
        prefix="10.10.10.0",
        prefix_len=24,
        next_hop="192.0.2.22",
        neighbor_id="6.6.6.6",
        local_pref=200,
        as_path=(65100, 65200),
        med=20,
        origin="igp",
    )
    multipath = sorted(path.next_hop for path in (primary, secondary) if path.local_pref == primary.local_pref and path.as_path == primary.as_path)
    multipath_outcome = FeatureOutcome(
        action="SELECT",
        reason="BGP_MULTIPATH",
        checkpoints=("BGP_MULTIPATH_SELECT",),
        details={"next_hops": multipath},
    )
    multipath_passed = multipath == ["192.0.2.21", "192.0.2.22"]

    return _result(
        "lab24_bgp_scaling_patterns",
        [
            LabStepResult(
                name="bgp_route_reflection",
                passed=reflect_passed,
                detail="route-reflector reflects client routes to non-originating clients",
                outcome=reflect_outcome,
            ),
            LabStepResult(
                name="bgp_convergence_mark",
                passed=convergence_passed,
                detail="steady-state reflection output is stable across iterations",
                outcome=convergence_outcome,
            ),
            LabStepResult(
                name="bgp_multipath_select",
                passed=multipath_passed,
                detail="equal-cost/equal-policy paths are selected for multipath install",
                outcome=multipath_outcome,
            ),
        ],
    )


def _lab25() -> LabRunResult:
    tunneled = encapsulate(
        payload_id="pkt-42",
        inner_src="10.1.0.10",
        inner_dst="10.2.0.20",
        tunnel_src="192.0.2.1",
        tunnel_dst="192.0.2.2",
    )
    push_outcome = FeatureOutcome(
        action="ENCAPSULATE",
        reason="TUNNEL_PUSH",
        checkpoints=("ENCAP_PUSH",),
        details={"outer_src": tunneled.outer_src, "outer_dst": tunneled.outer_dst},
    )
    push_passed = tunneled.outer_src == "192.0.2.1" and tunneled.outer_dst == "192.0.2.2"

    payload_id, inner_src, inner_dst = decapsulate(tunneled)
    pop_outcome = FeatureOutcome(
        action="DECAPSULATE",
        reason="TUNNEL_POP",
        checkpoints=("ENCAP_POP",),
        details={"payload_id": payload_id, "inner_src": inner_src, "inner_dst": inner_dst},
    )
    pop_passed = payload_id == "pkt-42" and inner_dst == "10.2.0.20"

    policy = evaluate_ipsec_policy(destination_ip=inner_dst, protected_prefixes=("10.2.0.0/16",))
    policy_outcome = FeatureOutcome(
        action="EVALUATE",
        reason="IPSEC_POLICY",
        checkpoints=("IPSEC_POLICY_EVALUATE",),
        details={"destination_ip": inner_dst, "policy_action": policy},
    )
    policy_passed = policy == "PROTECT"

    spi = lookup_sa(sa_db={"192.0.2.2": 1001}, peer_ip=tunneled.outer_dst)
    sa_outcome = FeatureOutcome(
        action="LOOKUP",
        reason="IPSEC_SA",
        checkpoints=("IPSEC_SA_LOOKUP",),
        details={"peer_ip": tunneled.outer_dst, "spi": spi},
    )
    sa_passed = spi == 1001

    return _result(
        "lab25_tunnels_and_ipsec",
        [
            LabStepResult(
                name="tunnel_encap_push",
                passed=push_passed,
                detail="inner payload is encapsulated with deterministic outer tunnel headers",
                outcome=push_outcome,
            ),
            LabStepResult(
                name="tunnel_decap_pop",
                passed=pop_passed,
                detail="tunnel decapsulation restores original inner packet metadata",
                outcome=pop_outcome,
            ),
            LabStepResult(
                name="ipsec_policy_evaluate",
                passed=policy_passed,
                detail="destination-prefix policy deterministically selects PROTECT action",
                outcome=policy_outcome,
            ),
            LabStepResult(
                name="ipsec_sa_lookup",
                passed=sa_passed,
                detail="security association lookup returns expected SPI for tunnel peer",
                outcome=sa_outcome,
            ),
        ],
    )


def _lab26() -> LabRunResult:
    readiness = readiness_check(
        checks={
            "bgp_session_up": True,
            "ospf_neighbors_full": True,
            "qos_scheduler_active": True,
        }
    )
    readiness_outcome = FeatureOutcome(
        action="CHECK",
        reason="OPS_READINESS",
        checkpoints=("OPS_READINESS_CHECK",),
        details={"ready": readiness.ready, "failed_checks": list(readiness.failed_checks)},
    )
    readiness_passed = readiness.ready

    telemetry = emit_telemetry(
        component="edge-r1",
        counters={"packets_forwarded": 1200, "packets_dropped": 12},
        timestamp_s=1_700_000_000,
    )
    telemetry_outcome = FeatureOutcome(
        action="EMIT",
        reason="OPS_TELEMETRY",
        checkpoints=("TELEMETRY_EMIT",),
        details=telemetry,
    )
    telemetry_passed = telemetry["counters"] == {"packets_dropped": 12, "packets_forwarded": 1200}

    return _result(
        "lab26_observability_and_ops",
        [
            LabStepResult(
                name="ops_readiness_check",
                passed=readiness_passed,
                detail="service health checks produce deterministic readiness status",
                outcome=readiness_outcome,
            ),
            LabStepResult(
                name="ops_telemetry_emit",
                passed=telemetry_passed,
                detail="telemetry export emits sorted counter payload for reproducible parsing",
                outcome=telemetry_outcome,
            ),
        ],
    )


def _lab27() -> LabRunResult:
    baseline = ScenarioState(label="baseline", routes={"203.0.113.0/24": "bgp_primary"}, alarms=())
    failure = apply_step(
        baseline,
        label="incident_link_failure",
        route_updates={"203.0.113.0/24": "ospf_backup"},
        raise_alarms=("BFD_DOWN",),
    )
    apply_outcome = FeatureOutcome(
        action="APPLY",
        reason="INCIDENT_STEP",
        checkpoints=("SCENARIO_STEP_APPLY",),
        details={"label": failure.label, "routes": failure.routes, "alarms": list(failure.alarms)},
    )
    apply_passed = failure.routes.get("203.0.113.0/24") == "ospf_backup" and failure.alarms == ("BFD_DOWN",)

    recovered = apply_step(
        failure,
        label="incident_recovered",
        route_updates={"203.0.113.0/24": "bgp_primary"},
        clear_alarms=("BFD_DOWN",),
    )
    converged = convergence_assert(
        state=recovered,
        expected_routes={"203.0.113.0/24": "bgp_primary"},
        expected_alarms=(),
    )
    stable = convergence_mark(before=baseline.routes, after=recovered.routes)
    assert_outcome = FeatureOutcome(
        action="ASSERT",
        reason="INCIDENT_CONVERGED",
        checkpoints=("CONVERGENCE_ASSERT",),
        details={"converged": converged, "stable": stable, "alarms": list(recovered.alarms)},
    )
    assert_passed = converged and stable

    return _result(
        "lab27_capstone_incident_drill",
        [
            LabStepResult(
                name="scenario_step_apply",
                passed=apply_passed,
                detail="incident step applies deterministic failover route and alarm state",
                outcome=apply_outcome,
            ),
            LabStepResult(
                name="scenario_convergence_assert",
                passed=assert_passed,
                detail="recovery step clears alarms and returns control plane to baseline",
                outcome=assert_outcome,
            ),
        ],
    )


LAB_RUNNERS: dict[str, Callable[[], LabRunResult]] = {
    "lab01_frame_and_headers": _lab01,
    "lab02_mac_learning_switch": _lab02,
    "lab03_vlan_and_trunks": _lab03,
    "lab04_stp": _lab04,
    "lab05_stp_convergence_and_protection": _lab05,
    "lab06_arp_and_adjacency": _lab06,
    "lab07_ipv4_subnet_and_rib": _lab07,
    "lab08_fib_forwarding_pipeline": _lab08,
    "lab09_icmp_and_control_responses": _lab09,
    "lab10_ipv4_control_plane_diagnostics": _lab10,
    "lab11_ospf_adjacency_fsm": _lab11,
    "lab12_ospf_network_types_and_dr_bdr": _lab12,
    "lab13_ospf_lsa_flooding_and_lsdb": _lab13,
    "lab14_ospf_spf_and_route_install": _lab14,
    "lab15_ospf_multi_area_abr": _lab15,
    "lab16_udp_tcp_fundamentals": _lab16,
    "lab17_bfd_for_liveness": _lab17,
    "lab18_acl_pipeline": _lab18,
    "lab19_nat44_stateful_translation": _lab19,
    "lab20_qos_marking_and_queueing": _lab20,
    "lab21_bgp_session_fsm_and_transport": _lab21,
    "lab22_bgp_attributes_and_bestpath": _lab22,
    "lab23_bgp_policy_and_filters": _lab23,
    "lab24_bgp_scaling_patterns": _lab24,
    "lab25_tunnels_and_ipsec": _lab25,
    "lab26_observability_and_ops": _lab26,
    "lab27_capstone_incident_drill": _lab27,
}

STUDENT_LAB_RUNNERS: dict[str, Callable[[], LabRunResult]] = {
    "lab01_frame_and_headers": _lab01_student,
}


def run_lab(lab_id: str) -> LabRunResult:
    runner = LAB_RUNNERS.get(lab_id)
    if runner is None:
        raise KeyError(lab_id)
    return runner()


def run_student_lab(lab_id: str) -> LabRunResult:
    runner = STUDENT_LAB_RUNNERS.get(lab_id)
    if runner is None:
        raise KeyError(lab_id)
    return runner()
