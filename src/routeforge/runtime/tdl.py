"""TDL (Test Driven Learning) runtime primitives for side-quest challenges."""

from __future__ import annotations

from ipaddress import IPv4Address
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
