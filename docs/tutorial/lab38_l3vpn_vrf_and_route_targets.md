# Lab 38: L3VPN VRF and Route Targets

## Learning objectives

- Implement `l3vpn_vrf_route_targets` in `src/routeforge/runtime/phase2.py`.
- Deliver `vrf_route_install`: VRF route installs when import RT matches.
- Deliver `rt_import_match`: route-target import policy accepts matching RT.
- Deliver `vpnv4_resolve`: VPNv4 route resolves into tenant VRF.
- Validate internal behavior through checkpoints: VRF_ROUTE_INSTALL, RT_IMPORT, VPNV4_RESOLVE.

## Prerequisite recap

- Required prior labs: `lab37_mpls_ldp_label_forwarding`.
- Confirm target mapping before coding with `routeforge show lab38_l3vpn_vrf_and_route_targets`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

VPN route leaking control with route-target policy. Student-mode coding target for this stage is `src/routeforge/runtime/phase2.py` (`l3vpn_vrf_route_targets`).

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/phase2.py`
- Symbol: `l3vpn_vrf_route_targets`
- Why this target: implement the core behavior required by the three lab steps.
- Stage check: `routeforge check lab38`

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab38_l3vpn_vrf_and_route_targets`
3. Edit only `l3vpn_vrf_route_targets` in `src/routeforge/runtime/phase2.py`.
4. Run `routeforge check lab38` until it exits with status `0`.
5. Run `routeforge run lab38_l3vpn_vrf_and_route_targets --state-file "$STATE"` to confirm visible lab behavior and progress state updates.

## Verification commands and expected outputs

```bash
routeforge show lab38_l3vpn_vrf_and_route_targets
routeforge check lab38

STATE=/tmp/routeforge-progress.json
routeforge run lab38_l3vpn_vrf_and_route_targets --state-file "$STATE"
```

Expected outcomes:

- `routeforge show` prints `student.stage`, `student.target`, and `student.symbols` matching this chapter.
- `routeforge check lab38` passes when your implementation is complete for this stage.
- `vrf_route_install` should print `[PASS]` (VRF route installs when import RT matches).
- `rt_import_match` should print `[PASS]` (route-target import policy accepts matching RT).
- `vpnv4_resolve` should print `[PASS]` (VPNv4 route resolves into tenant VRF).
- Run output includes checkpoints: VRF_ROUTE_INSTALL, RT_IMPORT, VPNV4_RESOLVE.

## Debug trace checkpoints and interpretation guidance

Generate trace artifacts when a step fails:

```bash
routeforge run lab38_l3vpn_vrf_and_route_targets --state-file "$STATE" --trace-out /tmp/lab38_l3vpn_vrf_and_route_targets.jsonl
routeforge debug replay --trace /tmp/lab38_l3vpn_vrf_and_route_targets.jsonl
routeforge debug explain --trace /tmp/lab38_l3vpn_vrf_and_route_targets.jsonl --step vrf_route_install
```

Checkpoint guide:

- `VRF_ROUTE_INSTALL`: first expected pipeline milestone.
- `RT_IMPORT`: second expected pipeline milestone.
- `VPNV4_RESOLVE`: third expected pipeline milestone.

## Failure drills and troubleshooting flow

- Intentionally break `l3vpn_vrf_route_targets` in `src/routeforge/runtime/phase2.py` and rerun `routeforge check lab38` to confirm tests catch regressions.
- If `routeforge run lab38_l3vpn_vrf_and_route_targets --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- L3VPN VRF import and resolution behavior.
