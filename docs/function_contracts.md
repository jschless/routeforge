# Function Contracts

This reference is the canonical quick lookup for student target signatures and required checkpoints.

| Stage | Lab | Target Signatures | Required MUST Checkpoints |
| --- | --- | --- | --- |
| 1 | `lab01_frame_and_headers` | `is_valid_mac(value: 'str') -> 'bool' -> bool<br>IPv4Header.validate(self) -> 'list[str]' -> list[str]<br>EthernetFrame.validate(self) -> 'list[str]' -> list[str]` | `PARSE_OK, PARSE_DROP` |
| 2 | `lab02_mac_learning_switch` | `DataplaneSim._determine_forwarding_plan(self, *, ingress_interface: 'str', ingress_vlan: 'int', destination_mac: 'str') -> 'ForwardingPlan' -> ForwardingPlan` | `MAC_LEARN, L2_FLOOD, L2_UNICAST_FORWARD` |
| 3 | `lab03_vlan_and_trunks` | `DataplaneSim._determine_egress_vlan_plan(self, *, ingress_vlan: 'int', ingress_tag: 'int \| None', egress_port_name: 'str') -> 'EgressVlanPlan' -> EgressVlanPlan` | `VLAN_CLASSIFY, VLAN_TAG_PUSH, VLAN_TAG_POP` |
| 4 | `lab04_stp` | `compute_stp(bridges: 'list[Bridge]', links: 'list[Link]') -> 'STPResult' -> STPResult` | `STP_ROOT_CHANGE, STP_PORT_ROLE_CHANGE` |
| 5 | `lab05_stp_convergence_and_protection` | `role_changes(previous: 'STPResult', current: 'STPResult') -> 'dict[tuple[str, str], tuple[str, str]]' -> dict[tuple[str, str], tuple[str, str]]<br>bpdu_guard_decision(*, port: 'tuple[str, str]', edge_port: 'bool', bpdu_received: 'bool') -> 'GuardDecision' -> GuardDecision` | `STP_TOPOLOGY_CHANGE, STP_GUARD_ACTION` |
| 6 | `lab06_arp_and_adjacency` | `ArpAdjacencyTable.resolve(self, *, next_hop_ip: 'str', mac: 'str') -> 'list[str]' -> list[str]` | `ARP_REQUEST_TX, ARP_REPLY_RX, ARP_CACHE_UPDATE` |
| 7 | `lab07_ipv4_subnet_and_rib` | `RibTable.lookup(self, destination_ip: 'str') -> 'RouteEntry \| None' -> RouteEntry \| None` | `RIB_ROUTE_INSTALL, ROUTE_LOOKUP, ROUTE_SELECT` |
| 8 | `lab08_fib_forwarding_pipeline` | `forward_packet(packet: 'IPv4Packet', route: 'RouteEntry \| None') -> 'ForwardingDecision' -> ForwardingDecision` | `FIB_FORWARD, FIB_DROP, TTL_DECREMENT` |
| 9 | `lab09_icmp_and_control_responses` | `icmp_control(packet: 'IPv4Packet', route: 'RouteEntry \| None') -> 'IcmpControlDecision' -> IcmpControlDecision` | `ICMP_ECHO_REPLY, ICMP_UNREACHABLE, ICMP_TIME_EXCEEDED` |
| 10 | `lab10_ipv4_control_plane_diagnostics` | `explain_drop(decision: 'ForwardingDecision') -> 'str' -> str` | `EXPLAIN_CHECKPOINT, DROP_REASON_ASSERT` |
| 11 | `lab11_ospf_adjacency_fsm` | `neighbor_hello_transition(*, current_state: 'str', hello_received: 'bool', dead_timer_expired: 'bool') -> 'str' -> str` | `OSPF_HELLO_RX, OSPF_NEIGHBOR_CHANGE` |
| 12 | `lab12_ospf_network_types_and_dr_bdr` | `failover_dr_bdr(candidates: 'list[DrCandidate]', *, active_router_ids: 'set[str]') -> 'tuple[str, str \| None]' -> tuple[str, str \| None]` | `OSPF_DR_ELECT, OSPF_BDR_ELECT, OSPF_DR_FAILOVER` |
| 13 | `lab13_ospf_lsa_flooding_and_lsdb` | `Lsdb.age_tick(self, seconds: 'int' = 1) -> 'list[tuple[str, str]]' -> list[tuple[str, str]]` | `OSPF_LSA_INSTALL, OSPF_LSA_REFRESH, OSPF_LSA_AGE_OUT` |
| 14 | `lab14_ospf_spf_and_route_install` | `run_spf(graph: 'dict[str, list[tuple[str, int]]]', *, root_router_id: 'str') -> 'SpfResult' -> SpfResult` | `OSPF_SPF_RUN, RIB_ROUTE_INSTALL` |
| 15 | `lab15_ospf_multi_area_abr` | `originate_summaries(routes: 'list[AreaRoute]') -> 'list[AreaRoute]' -> list[AreaRoute]` | `OSPF_SUMMARY_ORIGINATE, OSPF_INTERAREA_ROUTE_INSTALL` |
| 16 | `lab16_udp_tcp_fundamentals` | `validate_udp(*, length_bytes: 'int', checksum_valid: 'bool') -> 'bool' -> bool` | `FLOW_CLASSIFY, TCP_STATE_CHANGE, UDP_VALIDATE` |
| 17 | `lab17_bfd_for_liveness` | `BfdSession.tick(self, *, control_received: 'bool') -> 'str' -> str` | `BFD_CONTROL_RX, BFD_STATE_CHANGE, BFD_TIMEOUT` |
| 18 | `lab18_acl_pipeline` | `evaluate_acl(*, rules: 'list[AclRule]', src_ip: 'str') -> 'str' -> str` | `ACL_EVALUATE, ACL_PERMIT, ACL_DENY` |
| 19 | `lab19_nat44_stateful_translation` | `Nat44Table.inbound_translate(self, *, outside_port: 'int', protocol: 'str', now: 'int') -> 'NatSession \| None' -> NatSession \| None` | `NAT_SESSION_CREATE, NAT_TRANSLATE_OUTBOUND, NAT_TRANSLATE_INBOUND, NAT_SESSION_EXPIRE` |
| 20 | `lab20_qos_marking_and_queueing` | `QosEngine.dequeue(self) -> 'tuple[str \| None, str \| None]' -> tuple[str \| None, str \| None]` | `QOS_REMARK, QOS_ENQUEUE, QOS_DEQUEUE` |
| 21 | `lab21_bgp_session_fsm_and_transport` | `bgp_session_transition(*, current_state: 'str', event: 'str') -> 'str' -> str` | `BGP_SESSION_CHANGE, BGP_OPEN_RX` |
| 22 | `lab22_bgp_attributes_and_bestpath` | `select_best_path(paths: 'list[BgpPath]') -> 'BgpPath' -> BgpPath` | `BGP_UPDATE_RX, BGP_BEST_PATH` |
| 23 | `lab23_bgp_policy_and_filters` | `apply_export_policy(*, paths: 'list[BgpPath]', denied_prefixes: 'set[str]', local_pref_override: 'int \| None' = None) -> 'list[BgpPath]' -> list[BgpPath]` | `BGP_POLICY_APPLY, BGP_UPDATE_EXPORT` |
| 24 | `lab24_bgp_scaling_patterns` | `route_reflect(*, learned: 'dict[str, list[str]]', source_client: 'str') -> 'dict[str, list[str]]' -> dict[str, list[str]]` | `BGP_RR_REFLECT, BGP_CONVERGENCE_MARK` |
| 25 | `lab25_tunnels_and_ipsec` | `evaluate_ipsec_policy(*, destination_ip: 'str', protected_prefixes: 'tuple[str, ...]') -> 'str' -> str` | `ENCAP_PUSH, ENCAP_POP, IPSEC_POLICY_EVALUATE, IPSEC_SA_LOOKUP` |
| 26 | `lab26_observability_and_ops` | `emit_telemetry(*, component: 'str', counters: 'dict[str, int]', timestamp_s: 'int') -> 'dict[str, object]' -> dict[str, object]` | `OPS_READINESS_CHECK, TELEMETRY_EMIT` |
| 27 | `lab27_capstone_incident_drill` | `apply_step(state: 'ScenarioState', *, label: 'str', route_updates: 'dict[str, str] \| None' = None, clear_alarms: 'tuple[str, ...]' = (), raise_alarms: 'tuple[str, ...]' = ()) -> 'ScenarioState' -> ScenarioState` | `SCENARIO_STEP_APPLY, CONVERGENCE_ASSERT` |
| 28 | `lab28_dhcp_snooping_and_dai` | `dhcp_snooping_dai(*, trusted_port: 'bool', binding: 'DhcpBinding \| None', arp_mac: 'str', arp_ip: 'str') -> 'tuple[DhcpBinding \| None, str]' -> tuple[DhcpBinding \| None, str]` | `DHCP_BINDING_LEARN, DAI_VALIDATE, DAI_DROP` |
| 29 | `lab29_port_security_and_ip_source_guard` | `port_security_ip_source_guard(*, max_macs: 'int', learned_macs: 'tuple[str, ...]', source_mac: 'str', source_ip_allowed: 'bool') -> 'tuple[tuple[str, ...], str]' -> tuple[tuple[str, ...], str]` | `PORTSEC_LEARN, PORTSEC_VIOLATION, IPSG_DENY` |
| 30 | `lab30_qos_policing_and_shaping` | `qos_police_shape(*, offered_kbps: 'int', cir_kbps: 'int', shape_rate_kbps: 'int') -> 'tuple[int, int]' -> tuple[int, int]` | `QOS_POLICE, QOS_SHAPE_QUEUE, QOS_SHAPE_RELEASE` |
| 31 | `lab31_qos_congestion_avoidance_wred` | `qos_wred_decision(*, queue_depth: 'int', min_threshold: 'int', max_threshold: 'int', ecn_capable: 'bool') -> 'str' -> str` | `QOS_WRED_PROFILE, QOS_ECN_MARK, QOS_WRED_DROP` |
| 32 | `lab32_route_redistribution_and_loop_prevention` | `redistribute_with_loop_guard(*, source_prefix: 'str', source_protocol: 'str', existing_tags: 'set[str]') -> 'tuple[set[str], str]' -> tuple[set[str], str]` | `REDIST_IMPORT, TAG_SET, LOOP_SUPPRESS` |
| 33 | `lab33_fhrp_tracking_and_failover` | `fhrp_track_failover(*, active_router: 'str', standby_router: 'str', tracked_object_up: 'bool') -> 'str' -> str` | `FHRP_ACTIVE_CHANGE, TRACK_DOWN, FHRP_PREEMPT` |
| 34 | `lab34_ipv6_nd_slaac_and_ra_guard` | `ipv6_nd_slaac_ra_guard(*, ra_trusted: 'bool', source_link_local: 'str', prefix: 'str') -> 'tuple[str, str]' -> tuple[str, str]` | `ND_NEIGHBOR_LEARN, SLAAC_PREFIX_APPLY, RA_GUARD_DROP` |
| 35 | `lab35_ospfv3_adjacency_and_lsdb` | `ospfv3_adjacency_lsdb(*, hello_ok: 'bool', lsa_id: 'str', lsdb: 'set[str]') -> 'tuple[str, set[str]]' -> tuple[str, set[str]]` | `OSPFV3_HELLO_RX, OSPFV3_NEIGHBOR_FULL, OSPFV3_LSA_INSTALL` |
| 36 | `lab36_mpbgp_ipv6_unicast` | `mpbgp_ipv6_unicast(paths: 'list[MpbgpPath]') -> 'MpbgpPath' -> MpbgpPath` | `BGP_MP_UPDATE_RX, BGP_AF_SELECT, BGP_MP_BESTPATH` |
| 37 | `lab37_mpls_ldp_label_forwarding` | `mpls_ldp_lfib(*, fec: 'str', local_label: 'int', outgoing_label: 'int') -> 'tuple[str, int, int]' -> tuple[str, int, int]` | `LDP_LABEL_ALLOC, LFIB_PROGRAM, MPLS_SWAP_FORWARD` |
| 38 | `lab38_l3vpn_vrf_and_route_targets` | `l3vpn_vrf_route_targets(*, import_rts: 'set[str]', route_rt: 'str', prefix: 'str') -> 'tuple[str, str]' -> tuple[str, str]` | `VRF_ROUTE_INSTALL, RT_IMPORT, VPNV4_RESOLVE` |
| 39 | `lab39_bgp_evpn_vxlan_basics` | `evpn_vxlan_control(*, mac: 'str', ip: 'str', vni: 'int', known_vnis: 'set[int]') -> 'tuple[str, str]' -> tuple[str, str]` | `EVPN_TYPE2_LEARN, VNI_MAP_RESOLVE, EVPN_MAC_IP_INSTALL` |
