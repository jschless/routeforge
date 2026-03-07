# Lab 39: BGP EVPN VXLAN Basics

## Learning objectives

- Implement `evpn_vxlan_control` in `src/routeforge/runtime/phase2.py`.
- Deliver `evpn_type2_learn`: EVPN type-2 route is learned for MAC/IP tuple.
- Deliver `evpn_vni_map`: MAC/IP tuple is mapped to VNI context.
- Deliver `evpn_mac_ip_install`: control-plane tuple installs in EVPN table.
- Validate internal behavior through checkpoints: EVPN_TYPE2_LEARN, VNI_MAP_RESOLVE, EVPN_MAC_IP_INSTALL.

## Prerequisite recap

- Required prior labs: `lab38_l3vpn_vrf_and_route_targets`.
- Confirm target mapping before coding with `routeforge show lab39_bgp_evpn_vxlan_basics`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

Overlay control-plane mapping of MAC/IP endpoints to VNI. Student-mode coding target for this stage is `src/routeforge/runtime/phase2.py` (`evpn_vxlan_control`).

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/phase2.py`
- Symbol: `evpn_vxlan_control`
- Why this target: implement the core behavior required by the three lab steps.
- Stage check: `routeforge check lab39`

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab39_bgp_evpn_vxlan_basics`
3. Edit only `evpn_vxlan_control` in `src/routeforge/runtime/phase2.py`.
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

- `EVPN_TYPE2_LEARN`: first expected pipeline milestone.
- `VNI_MAP_RESOLVE`: second expected pipeline milestone.
- `EVPN_MAC_IP_INSTALL`: third expected pipeline milestone.

## Failure drills and troubleshooting flow

- Intentionally break `evpn_vxlan_control` in `src/routeforge/runtime/phase2.py` and rerun `routeforge check lab39` to confirm tests catch regressions.
- If `routeforge run lab39_bgp_evpn_vxlan_basics --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- EVPN type-2 and VXLAN mapping basics.
