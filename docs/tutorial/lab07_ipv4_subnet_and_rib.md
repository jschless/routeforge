# Lab 07: IPv4 Subnet and RIB

## Learning objectives

- Install connected/static routes into a simple RIB model.
- Perform deterministic longest-prefix-match route lookup.
- Verify route selection checkpoints.

## Prerequisite recap

- Complete `lab06_arp_and_adjacency`.
- Understand IPv4 prefixes and subnet masks.

## Concept walkthrough

`lab07` introduces route table behavior. Multiple routes may match a destination, but the selected route must follow deterministic LPM and tie-break policy.

## Implementation TODO map

- `src/routeforge/runtime/l3.py`: route install and lookup behavior.
- `src/routeforge/labs/exercises.py`: lab scenario for route selection.

## Verification commands and expected outputs

```bash
PYTHONPATH=src python -m routeforge run lab07_ipv4_subnet_and_rib --completed lab01_frame_and_headers --completed lab02_mac_learning_switch --completed lab03_vlan_and_trunks --completed lab04_stp --completed lab05_stp_convergence_and_protection --completed lab06_arp_and_adjacency
```

Expected:

- `rib_install_and_lpm` step `PASS`.
- Checkpoints include `RIB_ROUTE_INSTALL`, `ROUTE_LOOKUP`, `ROUTE_SELECT`.

## Debug trace checkpoints and interpretation guidance

- `RIB_ROUTE_INSTALL`: route inserted into RIB.
- `ROUTE_LOOKUP`: destination lookup executed.
- `ROUTE_SELECT`: one deterministic winner selected.

## Failure drills and troubleshooting flow

- Add competing routes with equal prefix length and verify tie-break determinism.
- Remove specific route and confirm fallback to less-specific prefix.

## Standards and references

- RFC 1812 router forwarding behavior (conceptual).
