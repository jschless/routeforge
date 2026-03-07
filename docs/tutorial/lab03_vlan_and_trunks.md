# Lab 03: VLAN and Trunks

## Learning objectives

- Implement `DataplaneSim._vlan_translation_checkpoint` in `src/routeforge/runtime/dataplane_sim.py`.
- Deliver `access_to_trunk_tag_push`: access VLAN traffic is tagged when sent over trunk.
- Deliver `trunk_to_access_tag_pop`: tagged trunk traffic is untagged on matching access port.
- Validate internal behavior through checkpoints: PARSE_OK, VLAN_CLASSIFY, MAC_LEARN, L2_FLOOD, VLAN_TAG_PUSH, VLAN_TAG_POP.

## Prerequisite recap

- Required prior labs: lab02_mac_learning_switch.
- Confirm target mapping before coding with `routeforge show lab03_vlan_and_trunks`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

VLAN tagging/untagging and per-VLAN forwarding behavior. Student-mode coding target for this stage is `src/routeforge/runtime/dataplane_sim.py` (`DataplaneSim._vlan_translation_checkpoint`).

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/dataplane_sim.py`
- Symbols: `DataplaneSim._vlan_translation_checkpoint`
- Why this target: Emit VLAN tag push/pop checkpoints on trunk/access transitions.
- Stage check: `routeforge check lab03`

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab03_vlan_and_trunks`
3. Edit only the listed symbols in `src/routeforge/runtime/dataplane_sim.py`.
4. Run `routeforge check lab03` until it exits with status `0`.
5. Run `routeforge run lab03_vlan_and_trunks --state-file "$STATE"` to confirm visible lab behavior and progress state updates.

## Verification commands and expected outputs

```bash
routeforge show lab03_vlan_and_trunks
routeforge check lab03

STATE=/tmp/routeforge-progress.json
routeforge run lab03_vlan_and_trunks --state-file "$STATE"
```

Expected outcomes:

- `routeforge show` prints `student.stage`, `student.target`, and `student.symbols` matching this chapter.
- `routeforge check lab03` passes when your implementation is complete for this stage.
- `access_to_trunk_tag_push` should print `[PASS]` (access VLAN traffic is tagged when sent over trunk).
- `trunk_to_access_tag_pop` should print `[PASS]` (tagged trunk traffic is untagged on matching access port).
- Run output includes checkpoints: PARSE_OK, VLAN_CLASSIFY, MAC_LEARN, L2_FLOOD, VLAN_TAG_PUSH, VLAN_TAG_POP.

## Debug trace checkpoints and interpretation guidance

Generate trace artifacts when a step fails:

```bash
routeforge run lab03_vlan_and_trunks --state-file "$STATE" --trace-out /tmp/lab03_vlan_and_trunks.jsonl
routeforge debug replay --trace /tmp/lab03_vlan_and_trunks.jsonl
routeforge debug explain --trace /tmp/lab03_vlan_and_trunks.jsonl --step access_to_trunk_tag_push
```

Checkpoint guide:

- `PARSE_OK`: Ethernet/IPv4 frame and header validation behavior.
- `VLAN_CLASSIFY`: VLAN tagging/untagging and per-VLAN forwarding behavior.
- `MAC_LEARN`: MAC learning, unknown unicast flood, deterministic unicast forwarding.
- `L2_FLOOD`: MAC learning, unknown unicast flood, deterministic unicast forwarding.
- `VLAN_TAG_PUSH`: VLAN tagging/untagging and per-VLAN forwarding behavior.
- `VLAN_TAG_POP`: VLAN tagging/untagging and per-VLAN forwarding behavior.

## Failure drills and troubleshooting flow

- Intentionally break one listed symbol in `src/routeforge/runtime/dataplane_sim.py` and rerun `routeforge check lab03` to confirm tests catch regressions.
- If `routeforge run lab03_vlan_and_trunks --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- IEEE 802.1D (bridging and STP fundamentals).
- IEEE 802.1Q (VLAN tagging and trunk behavior).

