# Lab 38: L3VPN VRF and Route Targets

## Learning objectives

- Implement `vrf_import_action, l3vpn_vrf_route_targets` in `src/routeforge/runtime/mpls.py`.
- Deliver `vrf_route_install`: VRF route installs when import RT matches.
- Deliver `rt_import_match`: route-target import policy accepts matching RT.
- Deliver `vpnv4_resolve`: VPNv4 route resolves into tenant VRF.
- Validate internal behavior through checkpoints: VPN_RT_IMPORT, VPN_RT_REJECT.

## Prerequisite recap

- Required prior labs: `lab37_mpls_ldp_label_forwarding`.
- Confirm target mapping before coding with `routeforge show lab38_l3vpn_vrf_and_route_targets`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

Enterprises often share a carrier's backbone while keeping their traffic completely isolated from one another. BGP/MPLS L3VPN achieves this by giving each customer their own routing table — a VRF (Virtual Routing and Forwarding instance) — on every Provider Edge (PE) router. Packets are forwarded over the shared MPLS core using labels, but the IP addresses inside each VRF never need to be globally unique.

Key terms:

- **VRF (Virtual Routing and Forwarding)**: a separate routing table on a single router, associated with one customer. Routes in VRF-A are invisible to VRF-B by default.
- **CE (Customer Edge)**: the customer's router, connected to the PE via a regular IP link. The CE knows nothing about MPLS.
- **PE (Provider Edge)**: the carrier's router that faces the customer. It holds the VRF, applies RT policy, and adds/removes MPLS labels.
- **P (Provider core)**: transit routers that only do label swapping — they never see VPN routes.
- **Route Target (RT)**: a BGP extended community string (e.g., `"65000:100"`) attached to VPN routes. RT policy controls which routes are imported into which VRFs.
- **VPNv4**: the BGP address family that carries VPN prefixes annotated with a Route Distinguisher and RT communities.

A minimal L3VPN topology:

```
  CE-A ---[PE1 VRF-A]---[P]---[PE2 VRF-A]--- CE-A'
                |                    |
              RT export            RT import
              65000:100             65000:100  <-- match -> IMPORT
                                    65000:200  <-- no match -> REJECT
```

When PE2 receives a BGP VPNv4 route from PE1, it checks whether the route's RT appears in VRF-A's import policy. If it matches, the prefix is installed into VRF-A's routing table and becomes reachable from CE-A'. If there is no match, the route is silently rejected — it never appears in that VRF.

`l3vpn_vrf_route_targets` models exactly this decision: given the VRF's set of import RTs and the incoming route's RT, it returns `("IMPORT", prefix)` or `("REJECT", prefix)`. `vrf_import_action` is the helper that computes the action string alone. Getting the membership test right (a simple `in` check) is the core of this lab.

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/mpls.py`
- Symbols: `vrf_import_action, l3vpn_vrf_route_targets`
- Why this target: derive explicit import/reject action before emitting final VRF route outcome.
- Stage check: `routeforge check lab38`

Function contract for this stage:

- Symbol: `vrf_import_action(*, import_rts: set[str], route_rt: str) -> Literal["IMPORT", "REJECT"]`
- Required behavior: return IMPORT only when `route_rt` exists in `import_rts`
- Symbol: `l3vpn_vrf_route_targets(*, import_rts: set[str], route_rt: str, prefix: str) -> tuple[Literal["IMPORT", "REJECT"], str]`
- Required behavior: return `(action, prefix)` without mutating the original prefix

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab38_l3vpn_vrf_and_route_targets`
3. Edit only `vrf_import_action, l3vpn_vrf_route_targets` in `src/routeforge/runtime/mpls.py`.
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
- Run output includes checkpoints: VPN_RT_IMPORT, VPN_RT_REJECT.

## Debug trace checkpoints and interpretation guidance

Generate trace artifacts when a step fails:

```bash
routeforge run lab38_l3vpn_vrf_and_route_targets --state-file "$STATE" --trace-out /tmp/lab38_l3vpn_vrf_and_route_targets.jsonl
routeforge debug replay --trace /tmp/lab38_l3vpn_vrf_and_route_targets.jsonl
routeforge debug explain --trace /tmp/lab38_l3vpn_vrf_and_route_targets.jsonl --step vrf_route_install
```

Checkpoint guide:

- `VPN_RT_IMPORT`: fires when a VPN route is imported into a VRF — meaning `route_rt` was found in `import_rts` and the prefix was accepted. If this checkpoint is missing when you expect an import, your membership test is failing. Common mistakes: comparing against the wrong variable, treating `import_rts` as a list when it is a set, or accidentally negating the condition. Verify that `vrf_import_action` returns `"IMPORT"` (not `"ACCEPT"` or `True`) when the RT matches.

- `VPN_RT_REJECT`: fires when a VPN route is rejected because its RT does not appear in the VRF's import policy. The prefix is dropped and never installed. If this checkpoint is missing on a non-matching route, `l3vpn_vrf_route_targets` is returning `"IMPORT"` unconditionally — the membership check is likely absent or inverted. Both `VPN_RT_IMPORT` and `VPN_RT_REJECT` must appear across the test cases (one per matching route, one per non-matching route) for the full step suite to pass.

## Failure drills and troubleshooting flow

- Intentionally break `vrf_import_action` or `l3vpn_vrf_route_targets` in `src/routeforge/runtime/mpls.py` and rerun `routeforge check lab38` to confirm tests catch regressions.
- If `routeforge run lab38_l3vpn_vrf_and_route_targets --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- L3VPN VRF import and resolution behavior.
