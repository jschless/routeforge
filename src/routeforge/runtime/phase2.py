"""Backwards-compatibility shim — Phase 2 implementations have moved to dedicated modules.

Import from the new module locations instead:
  - security.py       — DhcpBinding, dhcp_snooping_dai, port_security_ip_source_guard
  - qos_advanced.py   — qos_police_shape, qos_wred_decision
  - routing_policy.py — redistribute_with_loop_guard, fhrp_track_failover
  - ipv6.py           — MpbgpPath, ipv6_nd_slaac_ra_guard, ospfv3_adjacency_lsdb, mpbgp_ipv6_unicast
  - mpls.py           — mpls_ldp_lfib, l3vpn_vrf_route_targets, evpn_vxlan_control
"""

from routeforge.runtime.ipv6 import (
    MpbgpPath,
    derive_slaac_host_id,
    ipv6_nd_slaac_ra_guard,
    mpbgp_ipv6_unicast,
    ospfv3_adjacency_lsdb,
    ospfv3_neighbor_result,
    rank_mpbgp_path,
)
from routeforge.runtime.mpls import (
    evpn_type2_entry,
    evpn_vxlan_control,
    l3vpn_vrf_route_targets,
    lfib_mapping,
    mpls_ldp_lfib,
    vrf_import_action,
)
from routeforge.runtime.qos_advanced import (
    apply_policer,
    qos_police_shape,
    qos_wred_decision,
    wred_decision_profile,
)
from routeforge.runtime.routing_policy import (
    build_redistribution_tag,
    fhrp_track_failover,
    redistribute_with_loop_guard,
    tracked_object_result,
)
from routeforge.runtime.security import (
    DhcpBinding,
    dhcp_snooping_dai,
    learn_binding_if_trusted,
    port_security_ip_source_guard,
    update_secure_mac_table,
)

__all__ = [
    "DhcpBinding",
    "MpbgpPath",
    "apply_policer",
    "build_redistribution_tag",
    "derive_slaac_host_id",
    "dhcp_snooping_dai",
    "evpn_type2_entry",
    "evpn_vxlan_control",
    "fhrp_track_failover",
    "ipv6_nd_slaac_ra_guard",
    "l3vpn_vrf_route_targets",
    "learn_binding_if_trusted",
    "lfib_mapping",
    "mpls_ldp_lfib",
    "mpbgp_ipv6_unicast",
    "ospfv3_adjacency_lsdb",
    "ospfv3_neighbor_result",
    "port_security_ip_source_guard",
    "qos_police_shape",
    "qos_wred_decision",
    "rank_mpbgp_path",
    "redistribute_with_loop_guard",
    "tracked_object_result",
    "update_secure_mac_table",
    "vrf_import_action",
    "wred_decision_profile",
]
