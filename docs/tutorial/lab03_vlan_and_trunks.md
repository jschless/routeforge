# Lab 03: VLAN and Trunks

## Learning objectives

- Classify ingress VLAN on access and trunk interfaces.
- Push VLAN tags when sending access traffic to a trunk.
- Pop VLAN tags when sending trunk traffic to a matching access port.

## Prerequisite recap

- Complete `lab02_mac_learning_switch`.
- Understand VLAN access and trunk mode behavior.

## Concept walkthrough

`lab03` adds VLAN domain isolation and tag translation at ingress/egress boundaries. Access ports are untagged; trunk ports can carry tagged frames for multiple VLANs.

## Implementation TODO map

- `src/routeforge/runtime/interface.py`: ingress VLAN and egress tag helpers.
- `src/routeforge/runtime/dataplane_sim.py`: VLAN classify, tag push, tag pop checkpoints.

## Verification commands and expected outputs

```bash
PYTHONPATH=src python -m routeforge run lab03_vlan_and_trunks --completed lab01_frame_and_headers --completed lab02_mac_learning_switch
```

Expected:

- `access_to_trunk_tag_push` step `PASS`.
- `trunk_to_access_tag_pop` step `PASS`.
- Checkpoints include `VLAN_CLASSIFY`, `VLAN_TAG_PUSH`, `VLAN_TAG_POP`.

## Debug trace checkpoints and interpretation guidance

- `VLAN_CLASSIFY`: ingress VLAN chosen from access/trunk context.
- `VLAN_TAG_PUSH`: outgoing frame receives 802.1Q tag.
- `VLAN_TAG_POP`: outgoing frame tag removed for access delivery.

## Failure drills and troubleshooting flow

- Remove VLAN 20 from trunk allowed list and confirm VLAN-not-allowed drop.
- Send tagged frame into access port and confirm deterministic drop reason.

## Standards and references

- IEEE 802.1Q VLAN tagging.
