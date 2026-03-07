# Lab 07: IPv4 Subnet and RIB

## Learning objectives

- Implement `RibTable.lookup` in `src/routeforge/runtime/l3.py`.
- Deliver `rib_install_and_lpm`: route install and deterministic longest-prefix selection.
- Validate internal behavior through checkpoints: RIB_ROUTE_INSTALL, ROUTE_LOOKUP, ROUTE_SELECT.

## Prerequisite recap

- Required prior labs: lab06_arp_and_adjacency.
- Confirm target mapping before coding with `routeforge show lab07_ipv4_subnet_and_rib`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

### What is the RIB and why LPM?

The Routing Information Base (RIB) is a router's table of all known routes.  When a packet arrives, the router must pick the *best* matching route.  More specific routes (longer prefix) take priority over general routes — this is *Longest Prefix Match (LPM)*.

For example, with these routes installed:
```
10.0.0.0/8    via 192.168.1.1  (default route catch-all)
10.1.0.0/16   via 192.168.1.2  (more specific)
10.1.1.0/24   via 192.168.1.3  (most specific)
```

A packet to `10.1.1.50` matches all three, but `/24` wins — it's the longest (most specific) match.

### Tiebreak chain

When multiple routes have the same prefix length, apply in order:

1. **Lowest admin_distance** — static routes (AD 1) beat OSPF (AD 110) beat BGP (AD 200).
2. **Lowest metric** — within the same protocol, lower metric wins.
3. **Lowest next_hop** — lexicographic string compare for determinism.

### What correct behavior looks like

```python
rib = RibTable()
rib.install(RouteEntry(prefix="10.0.0.0", prefix_len=8,  next_hop="192.168.1.1", ...))
rib.install(RouteEntry(prefix="10.1.1.0", prefix_len=24, next_hop="192.168.1.3", ...))
result = rib.lookup("10.1.1.50")
# result.prefix_len == 24, result.next_hop == "192.168.1.3"
```

Student-mode coding target for this stage is `src/routeforge/runtime/l3.py` (`RibTable.lookup`).

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/l3.py`
- Symbols: `RibTable.lookup`
- Why this target: Perform deterministic LPM route lookup.
- Stage check: `routeforge check lab07`

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab07_ipv4_subnet_and_rib`
3. Edit only the listed symbols in `src/routeforge/runtime/l3.py`.
4. Run `routeforge check lab07` until it exits with status `0`.
5. Run `routeforge run lab07_ipv4_subnet_and_rib --state-file "$STATE"` to confirm visible lab behavior and progress state updates.

## Verification commands and expected outputs

```bash
routeforge show lab07_ipv4_subnet_and_rib
routeforge check lab07

STATE=/tmp/routeforge-progress.json
routeforge run lab07_ipv4_subnet_and_rib --state-file "$STATE"
```

Expected outcomes:

- `routeforge show` prints `student.stage`, `student.target`, and `student.symbols` matching this chapter.
- `routeforge check lab07` passes when your implementation is complete for this stage.
- `rib_install_and_lpm` should print `[PASS]` (route install and deterministic longest-prefix selection).
- Run output includes checkpoints: RIB_ROUTE_INSTALL, ROUTE_LOOKUP, ROUTE_SELECT.

## Debug trace checkpoints and interpretation guidance

Generate trace artifacts when a step fails:

```bash
routeforge run lab07_ipv4_subnet_and_rib --state-file "$STATE" --trace-out /tmp/lab07_ipv4_subnet_and_rib.jsonl
routeforge debug replay --trace /tmp/lab07_ipv4_subnet_and_rib.jsonl
routeforge debug explain --trace /tmp/lab07_ipv4_subnet_and_rib.jsonl --step rib_install_and_lpm
```

Checkpoint guide:

- `RIB_ROUTE_INSTALL`: A route entry was successfully installed in the RIB via `install()`.
  This is pre-populated by the lab scenario — if missing, check the test setup rather than
  your `lookup()` implementation.
- `ROUTE_LOOKUP`: `lookup()` was called for a destination IP.  If missing, the scenario
  didn't reach the lookup step — a prior step likely failed.
- `ROUTE_SELECT`: `lookup()` returned a non-None route that was used for the forwarding
  decision.  If this checkpoint is missing but `ROUTE_LOOKUP` fired, your `lookup()`
  returned `None` when a match should exist.  Check that your prefix matching logic covers
  all candidate routes (don't return early after the first match).

## Failure drills and troubleshooting flow

- Intentionally break one listed symbol in `src/routeforge/runtime/l3.py` and rerun `routeforge check lab07` to confirm tests catch regressions.
- If `routeforge run lab07_ipv4_subnet_and_rib --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- RFC 791 (IPv4).
- RFC 792 (ICMP).
- RFC 826 (ARP).
