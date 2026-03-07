# Lab 02: MAC Learning Switch

## Learning objectives

- Learn source MAC addresses into a per-VLAN forwarding table.
- Flood unknown unicast deterministically.
- Unicast forward on MAC table hit.

## Prerequisite recap

- Complete `lab01_frame_and_headers`.
- Be able to identify ingress vs egress interface behavior.

## Concept walkthrough

`lab02` introduces the L2 forwarding database (FDB). First traffic floods because the destination is unknown. Return traffic learns the second host and then forwards as known unicast.

## Implementation TODO map

- `src/routeforge/runtime/router.py`: MAC learn and lookup methods.
- `src/routeforge/runtime/dataplane_sim.py`: flood vs unicast decision path.

## Verification commands and expected outputs

```bash
PYTHONPATH=src python -m routeforge run lab02_mac_learning_switch --completed lab01_frame_and_headers
```

Expected:

- `unknown_unicast_flood` step `PASS`.
- `known_unicast_forward` step `PASS`.
- Checkpoints include `MAC_LEARN`, `L2_FLOOD`, `L2_UNICAST_FORWARD`.

## Debug trace checkpoints and interpretation guidance

- `MAC_LEARN`: source MAC inserted/updated in FDB.
- `L2_FLOOD`: unknown destination emitted to all eligible non-ingress ports.
- `L2_UNICAST_FORWARD`: known destination emitted to one deterministic egress.

## Failure drills and troubleshooting flow

- Clear MAC table between steps and confirm unicast step falls back to flood.
- Force ingress/egress same-port destination and confirm drop behavior.

## Standards and references

- IEEE 802.1D bridge forwarding concepts.
