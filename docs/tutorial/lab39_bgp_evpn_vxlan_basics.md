# Lab 39: BGP EVPN VXLAN Basics

## Learning objectives

- Implement `evpn_type2_entry, evpn_vxlan_control` in `src/routeforge/runtime/mpls.py`.
- Deliver `evpn_type2_learn`: EVPN type-2 route is learned for MAC/IP tuple.
- Deliver `evpn_vni_map`: MAC/IP tuple is mapped to VNI context.
- Deliver `evpn_mac_ip_install`: control-plane tuple installs in EVPN table.
- Validate internal behavior through checkpoints: EVPN_TYPE2_LEARN, VNI_MAP_RESOLVE, EVPN_MAC_IP_INSTALL.

## Prerequisite recap

- Required prior labs: `lab38_l3vpn_vrf_and_route_targets`.
- Confirm target mapping before coding with `routeforge show lab39_bgp_evpn_vxlan_basics`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

Traditional data-center networks extend VLANs across switches using spanning tree, which does not scale beyond a few hundred switches and ties the failure domain to a single broadcast domain. VXLAN (Virtual Extensible LAN) solves this by encapsulating L2 Ethernet frames inside UDP packets, so any two servers can share a virtual segment regardless of their physical location in the fabric.

Key terms:

- **VXLAN**: an encapsulation standard that wraps an Ethernet frame in a UDP packet with an 8-byte VXLAN header. The outer IP/UDP header carries the frame across a routed underlay.
- **VNI (VXLAN Network Identifier)**: a 24-bit integer that identifies a virtual segment, analogous to a VLAN ID but with a much larger address space (up to ~16 million segments).
- **VTEP (VXLAN Tunnel Endpoint)**: a device (physical switch or hypervisor) that encapsulates and decapsulates VXLAN traffic. Each VTEP has an IP address on the underlay network.
- **EVPN (Ethernet VPN)**: a BGP address family that distributes MAC and IP reachability information between VTEPs, replacing flood-and-learn with a control-plane-driven approach.
- **Type-2 route**: the most common EVPN route type, advertising a single MAC address (and optionally its IP binding) along with the VNI it belongs to.

A minimal VTEP-to-VTEP topology:

```
  Host-A (MAC-A, IP-A)          Host-B (MAC-B, IP-B)
       |                               |
  [VTEP-1, VNI 1000]   BGP EVPN  [VTEP-2, VNI 1000]
       |    <--- Type-2 route --->     |
       |    MAC-B|IP-B|VNI 1000        |
       |                               |
       +--------[ IP underlay ]--------+
           VXLAN UDP encap/decap
```

When VTEP-2 advertises a Type-2 route for Host-B, VTEP-1 receives it over BGP. Before installing it, VTEP-1 checks whether VNI 1000 is locally configured (i.e., in `known_vnis`). If so, it installs the `MAC-B|IP-B|VNI 1000` entry and can now encapsulate frames destined for Host-B directly to VTEP-2. If the VNI is unknown — not a segment this VTEP participates in — the route is rejected.

`evpn_type2_entry` builds the canonical key string `mac|ip|vni` used throughout the control plane. `evpn_vxlan_control` applies the VNI admission check and returns either `("INSTALL", key)` or `("REJECT", "")`. This lab exercises the boundary between overlay control-plane filtering and forwarding-table installation.

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/mpls.py`
- Symbols: `evpn_type2_entry, evpn_vxlan_control`
- Why this target: build deterministic type-2 key and enforce known-VNI install policy.
- Stage check: `routeforge check lab39`

Function contract for this stage:

- Symbol: `evpn_type2_entry(*, mac: str, ip: str, vni: int) -> str`
- Required behavior: return deterministic key in `mac|ip|vni` format
- Symbol: `evpn_vxlan_control(*, mac: str, ip: str, vni: int, known_vnis: set[int]) -> tuple[Literal["INSTALL", "REJECT"], str]`
- Required behavior: install only for known VNI and return REJECT with empty payload otherwise

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab39_bgp_evpn_vxlan_basics`
3. Edit only `evpn_type2_entry, evpn_vxlan_control` in `src/routeforge/runtime/mpls.py`.
4. Run `routeforge check lab39` until it exits with status `0`.
5. Run `routeforge run lab39_bgp_evpn_vxlan_basics --state-file "$STATE"` to confirm visible lab behavior and progress state updates.

## Verification commands and expected outputs

```bash
routeforge show lab39_bgp_evpn_vxlan_basics
routeforge check lab39

STATE=/tmp/routeforge-progress.json
routeforge run lab39_bgp_evpn_vxlan_basics --state-file "$STATE"
```

Expected outcomes:

- `routeforge show` prints `student.stage`, `student.target`, and `student.symbols` matching this chapter.
- `routeforge check lab39` passes when your implementation is complete for this stage.
- `evpn_type2_learn` should print `[PASS]` (EVPN type-2 route is learned for MAC/IP tuple).
- `evpn_vni_map` should print `[PASS]` (MAC/IP tuple is mapped to VNI context).
- `evpn_mac_ip_install` should print `[PASS]` (control-plane tuple installs in EVPN table).
- Run output includes checkpoints: EVPN_TYPE2_LEARN, VNI_MAP_RESOLVE, EVPN_MAC_IP_INSTALL.

## Debug trace checkpoints and interpretation guidance

Generate trace artifacts when a step fails:

```bash
routeforge run lab39_bgp_evpn_vxlan_basics --state-file "$STATE" --trace-out /tmp/lab39_bgp_evpn_vxlan_basics.jsonl
routeforge debug replay --trace /tmp/lab39_bgp_evpn_vxlan_basics.jsonl
routeforge debug explain --trace /tmp/lab39_bgp_evpn_vxlan_basics.jsonl --step evpn_type2_learn
```

Checkpoint guide:

- `EVPN_TYPE2_LEARN`: fires when the deterministic `mac|ip|vni` tuple is built for the incoming EVPN type-2 route. If this checkpoint is missing, `evpn_type2_entry` did not produce the expected key.
- `VNI_MAP_RESOLVE`: fires when the scenario resolves the incoming tuple against the local VNI context. If this checkpoint is missing, the VNI admission path was skipped before the install decision.
- `EVPN_MAC_IP_INSTALL`: fires when a BGP EVPN MAC/IP entry is installed into the local forwarding table — meaning the incoming VNI was found in `known_vnis` and the entry key was constructed and accepted. If this checkpoint is missing on a route that should be installed, the VNI membership check is returning false. Verify that `known_vnis` is treated as a set of integers and that the VNI argument is an `int` (not a string). Also confirm that `evpn_type2_entry` returns the key as `f"{mac}|{ip}|{vni}"` — a malformed key string will cause the install assertion to fail even after `EVPN_MAC_IP_INSTALL` fires.

## Failure drills and troubleshooting flow

- Intentionally break `evpn_type2_entry` or `evpn_vxlan_control` in `src/routeforge/runtime/mpls.py` and rerun `routeforge check lab39` to confirm tests catch regressions.
- If `routeforge run lab39_bgp_evpn_vxlan_basics --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- EVPN type-2 and VXLAN mapping basics.
