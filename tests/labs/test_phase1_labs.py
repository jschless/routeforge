from __future__ import annotations

from routeforge.labs.exercises import run_lab


def test_lab01_runs_and_passes() -> None:
    result = run_lab("lab01_frame_and_headers")
    assert result.passed is True
    assert {"PARSE_OK", "PARSE_DROP"} <= set(result.checkpoints)


def test_lab02_runs_and_passes() -> None:
    result = run_lab("lab02_mac_learning_switch")
    assert result.passed is True
    assert {"MAC_LEARN", "L2_FLOOD", "L2_UNICAST_FORWARD"} <= set(result.checkpoints)


def test_lab03_runs_and_passes() -> None:
    result = run_lab("lab03_vlan_and_trunks")
    assert result.passed is True
    assert {"VLAN_CLASSIFY", "VLAN_TAG_PUSH", "VLAN_TAG_POP"} <= set(result.checkpoints)


def test_lab04_runs_and_passes() -> None:
    result = run_lab("lab04_stp")
    assert result.passed is True
    assert {"STP_ROOT_CHANGE", "STP_PORT_ROLE_CHANGE"} <= set(result.checkpoints)


def test_lab05_runs_and_passes() -> None:
    result = run_lab("lab05_stp_convergence_and_protection")
    assert result.passed is True
    assert {"STP_TOPOLOGY_CHANGE", "STP_GUARD_ACTION"} <= set(result.checkpoints)


def test_lab06_runs_and_passes() -> None:
    result = run_lab("lab06_arp_and_adjacency")
    assert result.passed is True
    assert {"ARP_REQUEST_TX", "ARP_REPLY_RX", "ARP_CACHE_UPDATE"} <= set(result.checkpoints)


def test_lab07_runs_and_passes() -> None:
    result = run_lab("lab07_ipv4_subnet_and_rib")
    assert result.passed is True
    assert {"RIB_ROUTE_INSTALL", "ROUTE_LOOKUP", "ROUTE_SELECT"} <= set(result.checkpoints)


def test_lab08_runs_and_passes() -> None:
    result = run_lab("lab08_fib_forwarding_pipeline")
    assert result.passed is True
    assert {"FIB_FORWARD", "FIB_DROP", "TTL_DECREMENT"} <= set(result.checkpoints)


def test_lab09_runs_and_passes() -> None:
    result = run_lab("lab09_icmp_and_control_responses")
    assert result.passed is True
    assert {"ICMP_ECHO_REPLY", "ICMP_UNREACHABLE", "ICMP_TIME_EXCEEDED"} <= set(result.checkpoints)


def test_lab10_runs_and_passes() -> None:
    result = run_lab("lab10_ipv4_control_plane_diagnostics")
    assert result.passed is True
    assert {"EXPLAIN_CHECKPOINT", "DROP_REASON_ASSERT"} <= set(result.checkpoints)


def test_lab11_runs_and_passes() -> None:
    result = run_lab("lab11_ospf_adjacency_fsm")
    assert result.passed is True
    assert {"OSPF_HELLO_RX", "OSPF_NEIGHBOR_CHANGE"} <= set(result.checkpoints)


def test_lab12_runs_and_passes() -> None:
    result = run_lab("lab12_ospf_network_types_and_dr_bdr")
    assert result.passed is True
    assert {"OSPF_DR_ELECT", "OSPF_BDR_ELECT", "OSPF_DR_FAILOVER"} <= set(result.checkpoints)


def test_lab13_runs_and_passes() -> None:
    result = run_lab("lab13_ospf_lsa_flooding_and_lsdb")
    assert result.passed is True
    assert {"OSPF_LSA_INSTALL", "OSPF_LSA_REFRESH", "OSPF_LSA_AGE_OUT"} <= set(result.checkpoints)


def test_lab14_runs_and_passes() -> None:
    result = run_lab("lab14_ospf_spf_and_route_install")
    assert result.passed is True
    assert {"OSPF_SPF_RUN", "RIB_ROUTE_INSTALL"} <= set(result.checkpoints)


def test_lab15_runs_and_passes() -> None:
    result = run_lab("lab15_ospf_multi_area_abr")
    assert result.passed is True
    assert {"OSPF_SUMMARY_ORIGINATE", "OSPF_INTERAREA_ROUTE_INSTALL"} <= set(result.checkpoints)


def test_lab16_runs_and_passes() -> None:
    result = run_lab("lab16_udp_tcp_fundamentals")
    assert result.passed is True
    assert {"FLOW_CLASSIFY", "TCP_STATE_CHANGE", "UDP_VALIDATE"} <= set(result.checkpoints)


def test_lab17_runs_and_passes() -> None:
    result = run_lab("lab17_bfd_for_liveness")
    assert result.passed is True
    assert {"BFD_CONTROL_RX", "BFD_STATE_CHANGE", "BFD_TIMEOUT"} <= set(result.checkpoints)


def test_lab18_runs_and_passes() -> None:
    result = run_lab("lab18_acl_pipeline")
    assert result.passed is True
    assert {"ACL_EVALUATE", "ACL_PERMIT", "ACL_DENY"} <= set(result.checkpoints)


def test_lab19_runs_and_passes() -> None:
    result = run_lab("lab19_nat44_stateful_translation")
    assert result.passed is True
    assert {"NAT_SESSION_CREATE", "NAT_TRANSLATE_OUTBOUND", "NAT_TRANSLATE_INBOUND", "NAT_SESSION_EXPIRE"} <= set(
        result.checkpoints
    )


def test_lab20_runs_and_passes() -> None:
    result = run_lab("lab20_qos_marking_and_queueing")
    assert result.passed is True
    assert {"QOS_REMARK", "QOS_ENQUEUE", "QOS_DEQUEUE"} <= set(result.checkpoints)


def test_lab21_runs_and_passes() -> None:
    result = run_lab("lab21_bgp_session_fsm_and_transport")
    assert result.passed is True
    assert {"BGP_SESSION_CHANGE", "BGP_OPEN_RX"} <= set(result.checkpoints)


def test_lab22_runs_and_passes() -> None:
    result = run_lab("lab22_bgp_attributes_and_bestpath")
    assert result.passed is True
    assert {"BGP_UPDATE_RX", "BGP_BEST_PATH"} <= set(result.checkpoints)


def test_lab23_runs_and_passes() -> None:
    result = run_lab("lab23_bgp_policy_and_filters")
    assert result.passed is True
    assert {"BGP_POLICY_APPLY", "BGP_UPDATE_EXPORT"} <= set(result.checkpoints)


def test_lab24_runs_and_passes() -> None:
    result = run_lab("lab24_bgp_scaling_patterns")
    assert result.passed is True
    assert {"BGP_RR_REFLECT", "BGP_CONVERGENCE_MARK"} <= set(result.checkpoints)


def test_lab25_runs_and_passes() -> None:
    result = run_lab("lab25_tunnels_and_ipsec")
    assert result.passed is True
    assert {"ENCAP_PUSH", "ENCAP_POP", "IPSEC_POLICY_EVALUATE", "IPSEC_SA_LOOKUP"} <= set(result.checkpoints)


def test_lab26_runs_and_passes() -> None:
    result = run_lab("lab26_observability_and_ops")
    assert result.passed is True
    assert {"OPS_READINESS_CHECK", "TELEMETRY_EMIT"} <= set(result.checkpoints)


def test_lab27_runs_and_passes() -> None:
    result = run_lab("lab27_capstone_incident_drill")
    assert result.passed is True
    assert {"SCENARIO_STEP_APPLY", "CONVERGENCE_ASSERT"} <= set(result.checkpoints)
