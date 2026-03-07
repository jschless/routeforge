"""TDL (Test Driven Learning) runtime primitives for side-quest challenges."""

from __future__ import annotations

from ipaddress import IPv4Address, ip_network
import re


def validate_yang_path(path: str) -> bool:
    """Return True for simple slash-delimited YANG-style paths."""
    if not path.startswith("/") or path == "/" or "//" in path:
        return False
    segment_re = re.compile(r"^[A-Za-z_][A-Za-z0-9_:-]*$")
    segments = path.strip("/").split("/")
    return all(bool(segment_re.match(segment)) for segment in segments)


def netconf_edit_merge_replace(
    *,
    running: dict[str, object],
    candidate: dict[str, object],
    operation: str,
) -> dict[str, object]:
    """Apply NETCONF-like merge/replace semantics to dictionaries."""
    op = operation.lower()
    if op == "merge":
        merged = dict(running)
        merged.update(candidate)
        return merged
    if op == "replace":
        return dict(candidate)
    raise ValueError("operation must be merge or replace")


def restconf_patch_idempotence(
    *,
    current: dict[str, object],
    patch: dict[str, object],
) -> tuple[dict[str, object], bool]:
    """Apply patch dict and report whether state actually changed."""
    updated = dict(current)
    changed = False
    for key, value in patch.items():
        if updated.get(key) != value:
            updated[key] = value
            changed = True
    return updated, changed


def config_drift_diff(
    *,
    intended: dict[str, object],
    observed: dict[str, object],
) -> dict[str, tuple[object | None, object | None]]:
    """Return key-level intended-vs-observed drift entries."""
    diff: dict[str, tuple[object | None, object | None]] = {}
    for key in sorted(set(intended) | set(observed)):
        lhs = intended.get(key)
        rhs = observed.get(key)
        if lhs != rhs:
            diff[key] = (lhs, rhs)
    return diff


def closed_loop_remediation(
    *,
    telemetry: dict[str, int],
    thresholds: dict[str, int],
) -> dict[str, str]:
    """Return SCALE_OUT / HOLD / SCALE_IN action per metric."""
    actions: dict[str, str] = {}
    for metric, threshold in sorted(thresholds.items()):
        value = telemetry.get(metric, 0)
        if value > threshold:
            actions[metric] = "SCALE_OUT"
        elif value < threshold // 2:
            actions[metric] = "SCALE_IN"
        else:
            actions[metric] = "HOLD"
    return actions


def rpf_check(*, incoming_interface: str, expected_rpf_interface: str) -> bool:
    """Return True only when packet arrives on expected RPF interface."""
    return incoming_interface == expected_rpf_interface


def pim_dr_election(candidates: list[tuple[str, int, str]]) -> str:
    """Elect DR by highest priority then highest interface IP then router-id."""
    if not candidates:
        raise ValueError("at least one candidate is required")
    ordered = sorted(
        candidates,
        key=lambda item: (item[1], int(IPv4Address(item[2])), item[0]),
        reverse=True,
    )
    return ordered[0][0]


def igmp_snooping_membership(
    *,
    table: dict[str, set[str]],
    group: str,
    interface: str,
    action: str,
) -> dict[str, set[str]]:
    """Apply JOIN/LEAVE event to IGMP snooping membership table."""
    updated = {grp: set(interfaces) for grp, interfaces in table.items()}
    op = action.upper()
    if op == "JOIN":
        updated.setdefault(group, set()).add(interface)
        return updated
    if op == "LEAVE":
        members = updated.get(group, set())
        members.discard(interface)
        if members:
            updated[group] = members
        else:
            updated.pop(group, None)
        return updated
    raise ValueError("action must be JOIN or LEAVE")


def rp_mapping(
    *,
    group_ip: str,
    rp_ranges: list[tuple[str, str, str]],
) -> str | None:
    """Return matching RP id for group range list."""
    group = int(IPv4Address(group_ip))
    ordered = sorted(rp_ranges, key=lambda item: (int(IPv4Address(item[0])), item[2]))
    for start, end, rp_id in ordered:
        if int(IPv4Address(start)) <= group <= int(IPv4Address(end)):
            return rp_id
    return None


def multicast_tree_forward(
    *,
    joined_interfaces: set[str],
    ingress_interface: str,
    rpf_passed: bool,
) -> tuple[str, tuple[str, ...]]:
    """Return forwarding action and egress interfaces for multicast tree."""
    if not rpf_passed:
        return "DROP_RPF_FAIL", ()
    egress = tuple(sorted(interface for interface in joined_interfaces if interface != ingress_interface))
    if not egress:
        return "DROP_NO_LISTENERS", ()
    return "FORWARD", egress


def client_join_fsm(*, current_state: str, event: str) -> str:
    """Advance simplified wireless client join state machine."""
    state = current_state.upper()
    ev = event.upper()
    if state == "IDLE" and ev == "AUTH_OK":
        return "AUTHENTICATED"
    if state == "AUTHENTICATED" and ev == "ASSOC_OK":
        return "ASSOCIATED"
    if state == "ASSOCIATED" and ev == "DHCP_OK":
        return "IP_READY"
    if ev == "TIMEOUT":
        return "IDLE"
    return state


def channel_conflict_score(*, channel_a: int, channel_b: int) -> int:
    """Score channel conflict severity from 0 (none) to 100 (full conflict)."""
    gap = abs(channel_a - channel_b)
    if gap == 0:
        return 100
    if gap >= 5:
        return 0
    return 100 - (20 * gap)


def roaming_decision(
    *,
    current_ap: str,
    current_rssi: int,
    candidates: dict[str, int],
    hysteresis_db: int,
) -> str:
    """Return AP choice with hysteresis to avoid flapping."""
    if not candidates:
        return current_ap
    best_ap = max(sorted(candidates), key=lambda ap: candidates[ap])
    best_rssi = candidates[best_ap]
    if best_rssi >= current_rssi + hysteresis_db:
        return best_ap
    return current_ap


def wmm_queue_map(*, dscp: int) -> str:
    """Map DSCP to simplified WMM queue class."""
    if dscp in {46, 48}:
        return "VOICE"
    if dscp >= 34:
        return "VIDEO"
    if dscp >= 10:
        return "BEST_EFFORT"
    return "BACKGROUND"


def wireless_incident_triage(
    *,
    auth_ok: bool,
    dhcp_ok: bool,
    rssi_dbm: int,
    channel_utilization: int,
) -> str:
    """Return dominant root-cause classification for wireless incident signal."""
    if not auth_ok:
        return "AUTH_FAILURE"
    if rssi_dbm < -75:
        return "RF_WEAK_SIGNAL"
    if channel_utilization > 85:
        return "RF_CONGESTION"
    if not dhcp_ok:
        return "DHCP_FAILURE"
    return "HEALTHY"


def prefix_list_match(
    *,
    prefix: str,
    rules: list[tuple[str, str, int | None, int | None]],
) -> tuple[str, str]:
    """Evaluate prefix-list style rules and return PERMIT/DENY decision."""
    route = ip_network(prefix, strict=False)
    for action, base_prefix, ge, le in rules:
        base = ip_network(base_prefix, strict=False)
        if not route.subnet_of(base):
            continue
        if ge is not None and route.prefixlen < ge:
            continue
        if le is not None and route.prefixlen > le:
            continue
        return action.upper(), "RULE_MATCH"
    return "DENY", "NO_MATCH"


def route_map_eval(
    *,
    route: dict[str, object],
    sequences: list[tuple[int, str, bool]],
) -> tuple[str, int | str]:
    """Evaluate route-map sequence matches in deterministic sequence order."""
    del route
    for seq, action, matched in sorted(sequences, key=lambda item: item[0]):
        if matched:
            return action.upper(), seq
    return "DENY", "IMPLICIT_DENY"


def community_policy_apply(
    *,
    current: set[str],
    operation: str,
    values: set[str],
) -> set[str]:
    """Apply add/remove/replace operations to BGP communities."""
    op = operation.upper()
    if op == "ADD":
        return set(current) | set(values)
    if op == "REMOVE":
        return set(current) - set(values)
    if op == "REPLACE":
        return set(values)
    raise ValueError("operation must be ADD, REMOVE, or REPLACE")


def attribute_policy_transform(
    *,
    local_pref: int,
    med: int,
    policy: dict[str, int],
) -> tuple[int, int]:
    """Apply optional local-pref and MED policy overrides."""
    return policy.get("local_pref", local_pref), policy.get("med", med)


def policy_pipeline_decision(
    *,
    prefix: str,
    prefix_rules: list[tuple[str, str, int | None, int | None]],
    route_map_sequences: list[tuple[int, str, bool]],
    communities: set[str],
    community_operation: str,
    community_values: set[str],
    local_pref: int,
    med: int,
    attr_policy: dict[str, int],
) -> tuple[str, str | dict[str, object]]:
    """Run a deterministic routing policy pipeline over one route."""
    prefix_action, _ = prefix_list_match(prefix=prefix, rules=prefix_rules)
    if prefix_action != "PERMIT":
        return "DROP", "PREFIX_DENY"

    route_action, route_ref = route_map_eval(route={"prefix": prefix}, sequences=route_map_sequences)
    if route_action != "PERMIT":
        return "DROP", f"ROUTE_MAP_{route_ref}"

    updated_communities = community_policy_apply(
        current=communities,
        operation=community_operation,
        values=community_values,
    )
    updated_local_pref, updated_med = attribute_policy_transform(
        local_pref=local_pref,
        med=med,
        policy=attr_policy,
    )
    return (
        "ADVERTISE",
        {
            "communities": tuple(sorted(updated_communities)),
            "local_pref": updated_local_pref,
            "med": updated_med,
        },
    )


def ldp_label_allocate(
    *,
    fec: str,
    bindings: dict[str, int],
    start_label: int = 16000,
) -> tuple[dict[str, int], int]:
    """Allocate deterministic LDP labels with stable reuse for existing FECs."""
    updated = dict(bindings)
    if fec in updated:
        return updated, updated[fec]
    next_label = max(updated.values(), default=start_label - 1) + 1
    updated[fec] = next_label
    return updated, next_label


def mpls_forward_action(
    *,
    incoming_labeled: bool,
    penultimate_hop: bool,
    outgoing_label: int | None,
) -> tuple[str, int | None]:
    """Return PUSH/SWAP/POP/DROP action for MPLS forwarding stage."""
    if not incoming_labeled and outgoing_label is not None:
        return "PUSH", outgoing_label
    if penultimate_hop and outgoing_label in {None, 3}:
        return "POP", None
    if outgoing_label is not None:
        return "SWAP", outgoing_label
    return "DROP", None


def vrf_rt_import_export(
    *,
    import_rts: set[str],
    export_rts: set[str],
    route_rt: str,
    direction: str,
) -> tuple[str, str]:
    """Return IMPORT/EXPORT/REJECT action for route-target policy."""
    op = direction.upper()
    if op == "IMPORT":
        return ("IMPORT", route_rt) if route_rt in import_rts else ("REJECT", route_rt)
    if op == "EXPORT":
        return ("EXPORT", route_rt) if route_rt in export_rts else ("REJECT", route_rt)
    raise ValueError("direction must be IMPORT or EXPORT")


def vpnv4_install_decision(*, next_hop_reachable: bool, rt_action: str) -> tuple[str, str]:
    """Return INSTALL/SUPPRESS decision for VPNv4 route install gate."""
    if not next_hop_reachable:
        return "SUPPRESS", "NH_UNREACHABLE"
    if rt_action == "IMPORT":
        return "INSTALL", "NH_REACHABLE"
    return "SUPPRESS", "RT_REJECT"


def l3vpn_trace_forward(
    *,
    next_hop_reachable: bool,
    import_rts: set[str],
    route_rt: str,
    incoming_labeled: bool,
    penultimate_hop: bool,
    outgoing_label: int | None,
) -> tuple[str, tuple[str, ...] | str]:
    """Trace L3VPN import/install/forward stages with deterministic failure reason."""
    rt_action, _ = vrf_rt_import_export(
        import_rts=import_rts,
        export_rts=set(),
        route_rt=route_rt,
        direction="IMPORT",
    )
    install_action, reason = vpnv4_install_decision(next_hop_reachable=next_hop_reachable, rt_action=rt_action)
    if install_action != "INSTALL":
        return "DROP", reason

    mpls_action, label = mpls_forward_action(
        incoming_labeled=incoming_labeled,
        penultimate_hop=penultimate_hop,
        outgoing_label=outgoing_label,
    )
    if mpls_action == "DROP":
        return "DROP", "MPLS_UNRESOLVED"

    checkpoints = ["RT_IMPORT", "VPN_INSTALL", f"MPLS_{mpls_action}"]
    if label is not None:
        checkpoints.append(f"LABEL_{label}")
    return "FORWARD", tuple(checkpoints)


def hsrp_priority_recompute(*, base_priority: int, track_decrement: int, tracked_object_up: bool) -> int:
    """Recompute HSRP priority from tracking object health."""
    if tracked_object_up:
        return base_priority
    return max(0, base_priority - max(0, track_decrement))


def bfd_flap_dampening(
    *,
    flap_count: int,
    suppress_threshold: int,
    hold_down_seconds: int,
    elapsed_seconds: int,
) -> tuple[str, int]:
    """Return SUPPRESS/UNSUPPRESS state with remaining hold-down seconds."""
    if flap_count >= suppress_threshold and elapsed_seconds < hold_down_seconds:
        return "SUPPRESS", hold_down_seconds - elapsed_seconds
    return "UNSUPPRESS", 0


def isis_lsp_pacing(
    *,
    queued_lsps: tuple[str, ...],
    tokens: int,
    replenish: int,
    bucket_max: int,
) -> tuple[tuple[str, ...], tuple[str, ...], int]:
    """Send queued IS-IS LSPs based on deterministic token bucket pacing."""
    available = min(bucket_max, max(0, tokens) + max(0, replenish))
    send_count = min(len(queued_lsps), available)
    sent = queued_lsps[:send_count]
    remaining = queued_lsps[send_count:]
    return sent, remaining, available - send_count


def gr_stale_path_action(*, stale_seconds_remaining: int) -> tuple[str, int]:
    """Return RETAIN_STALE or FLUSH_STALE based on stale-route timer."""
    if stale_seconds_remaining > 0:
        return "RETAIN_STALE", stale_seconds_remaining
    return "FLUSH_STALE", 0


def control_plane_stability_triage(
    *,
    hsrp_priority: int,
    hsrp_min_priority: int,
    bfd_state: str,
    stale_state: str,
) -> tuple[str, str]:
    """Classify control-plane stability incident severity deterministically."""
    if bfd_state == "SUPPRESS" and stale_state == "FLUSH_STALE":
        return "CRITICAL", "CONTROL_PLANE_UNSTABLE"
    if hsrp_priority < hsrp_min_priority:
        return "DEGRADED", "HSRP_PRIORITY_LOW"
    return "HEALTHY", "STABLE"
