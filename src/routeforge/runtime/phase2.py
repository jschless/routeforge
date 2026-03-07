"""Backwards-compatibility shim — Phase 2 stubs have moved to dedicated modules.

Import from the new module locations instead:
  - security.py       — DhcpBinding, learn_binding_if_trusted, dhcp_snooping_dai,
                        update_secure_mac_table, port_security_ip_source_guard
  - qos_advanced.py   — apply_policer, wred_decision_profile, qos_police_shape, qos_wred_decision
  - routing_policy.py — tracked_object_result, build_redistribution_tag,
                        redistribute_with_loop_guard, fhrp_track_failover
  - ipv6.py           — derive_slaac_host_id, ospfv3_neighbor_result, ipv6_nd_slaac_ra_guard,
                        ospfv3_adjacency_lsdb, MpbgpPath, rank_mpbgp_path, mpbgp_ipv6_unicast
  - mpls.py           — lfib_mapping, vrf_import_action, evpn_type2_entry, mpls_ldp_lfib,
                        l3vpn_vrf_route_targets, evpn_vxlan_control
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
    "mpbgp_ipv6_unicast",
    "mpls_ldp_lfib",
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
