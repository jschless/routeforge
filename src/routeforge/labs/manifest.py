"""Ordered lab manifest for RouteForge v1."""

from __future__ import annotations

from typing import TypedDict


class LabEntry(TypedDict):
    id: str
    title: str
    prereqs: list[str]


LABS: list[LabEntry] = [
    {"id": "lab01_frame_and_headers", "title": "Frame and Header Validation", "prereqs": []},
    {"id": "lab02_mac_learning_switch", "title": "MAC Learning Switch", "prereqs": ["lab01_frame_and_headers"]},
    {"id": "lab03_vlan_and_trunks", "title": "VLAN and Trunks", "prereqs": ["lab02_mac_learning_switch"]},
    {"id": "lab04_stp", "title": "Spanning Tree", "prereqs": ["lab03_vlan_and_trunks"]},
    {"id": "lab05_stp_convergence_and_protection", "title": "STP Convergence and Protection", "prereqs": ["lab04_stp"]},
    {"id": "lab06_arp_and_adjacency", "title": "ARP and Adjacency", "prereqs": ["lab05_stp_convergence_and_protection"]},
    {"id": "lab07_ipv4_subnet_and_rib", "title": "IPv4 Subnet and RIB", "prereqs": ["lab06_arp_and_adjacency"]},
    {"id": "lab08_fib_forwarding_pipeline", "title": "FIB Forwarding Pipeline", "prereqs": ["lab07_ipv4_subnet_and_rib"]},
    {"id": "lab09_icmp_and_control_responses", "title": "ICMP and Control Responses", "prereqs": ["lab08_fib_forwarding_pipeline"]},
    {"id": "lab10_ipv4_control_plane_diagnostics", "title": "IPv4 Diagnostics", "prereqs": ["lab09_icmp_and_control_responses"]},
    {"id": "lab11_ospf_adjacency_fsm", "title": "OSPF Adjacency FSM", "prereqs": ["lab10_ipv4_control_plane_diagnostics"]},
    {"id": "lab12_ospf_network_types_and_dr_bdr", "title": "OSPF Network Types and DR/BDR", "prereqs": ["lab11_ospf_adjacency_fsm"]},
    {"id": "lab13_ospf_lsa_flooding_and_lsdb", "title": "OSPF LSA Flooding and LSDB", "prereqs": ["lab12_ospf_network_types_and_dr_bdr"]},
    {"id": "lab14_ospf_spf_and_route_install", "title": "OSPF SPF and Route Install", "prereqs": ["lab13_ospf_lsa_flooding_and_lsdb"]},
    {"id": "lab15_ospf_multi_area_abr", "title": "OSPF Multi-Area ABR", "prereqs": ["lab14_ospf_spf_and_route_install"]},
    {"id": "lab16_udp_tcp_fundamentals", "title": "UDP/TCP Fundamentals", "prereqs": ["lab15_ospf_multi_area_abr"]},
    {"id": "lab17_bfd_for_liveness", "title": "BFD for Liveness", "prereqs": ["lab16_udp_tcp_fundamentals"]},
    {"id": "lab18_acl_pipeline", "title": "ACL Pipeline", "prereqs": ["lab17_bfd_for_liveness"]},
    {"id": "lab19_nat44_stateful_translation", "title": "NAT44 Stateful Translation", "prereqs": ["lab18_acl_pipeline"]},
    {"id": "lab20_qos_marking_and_queueing", "title": "QoS Marking and Queueing", "prereqs": ["lab19_nat44_stateful_translation"]},
    {"id": "lab21_bgp_session_fsm_and_transport", "title": "BGP Session FSM and Transport", "prereqs": ["lab20_qos_marking_and_queueing"]},
    {"id": "lab22_bgp_attributes_and_bestpath", "title": "BGP Attributes and Best Path", "prereqs": ["lab21_bgp_session_fsm_and_transport"]},
    {"id": "lab23_bgp_policy_and_filters", "title": "BGP Policy and Filters", "prereqs": ["lab22_bgp_attributes_and_bestpath"]},
    {"id": "lab24_bgp_scaling_patterns", "title": "BGP Scaling Patterns", "prereqs": ["lab23_bgp_policy_and_filters"]},
    {"id": "lab25_tunnels_and_ipsec", "title": "Tunnels and IPsec", "prereqs": ["lab24_bgp_scaling_patterns"]},
    {"id": "lab26_observability_and_ops", "title": "Observability and Operations", "prereqs": ["lab25_tunnels_and_ipsec"]},
    {"id": "lab27_capstone_incident_drill", "title": "Capstone Incident Drill", "prereqs": ["lab26_observability_and_ops"]},
]


def get_lab(lab_id: str) -> LabEntry | None:
    for entry in LABS:
        if entry["id"] == lab_id:
            return entry
    return None


def prerequisite_chain(lab_id: str) -> list[str]:
    entry = get_lab(lab_id)
    if entry is None:
        raise KeyError(f"unknown lab: {lab_id}")

    ordered: list[str] = []
    seen: set[str] = set()

    def _visit(current_id: str) -> None:
        current = get_lab(current_id)
        if current is None:
            raise KeyError(f"unknown lab: {current_id}")
        for prereq in current["prereqs"]:
            _visit(prereq)
            if prereq not in seen:
                seen.add(prereq)
                ordered.append(prereq)

    _visit(lab_id)
    return ordered


def missing_prereqs(lab_id: str, completed_labs: set[str] | None = None) -> list[str]:
    completed = completed_labs or set()
    return [prereq for prereq in prerequisite_chain(lab_id) if prereq not in completed]
