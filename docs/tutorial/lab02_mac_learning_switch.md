# Lab 02: MAC Learning Switch

## Learning objectives

- Implement `DataplaneSim._select_known_unicast_egress` in `src/routeforge/runtime/dataplane_sim.py`.
- Deliver `unknown_unicast_flood`: unknown unicast floods to all non-ingress ports.
- Deliver `known_unicast_forward`: MAC learning enables deterministic unicast forwarding.
- Validate internal behavior through checkpoints: PARSE_OK, VLAN_CLASSIFY, MAC_LEARN, L2_FLOOD, L2_UNICAST_FORWARD.

## Prerequisite recap

- Required prior labs: lab01_frame_and_headers.
- Confirm target mapping before coding with `routeforge show lab02_mac_learning_switch`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

MAC learning, unknown unicast flood, deterministic unicast forwarding. Student-mode coding target for this stage is `src/routeforge/runtime/dataplane_sim.py` (`DataplaneSim._select_known_unicast_egress`).

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/dataplane_sim.py`
- Symbols: `DataplaneSim._select_known_unicast_egress`
- Why this target: Select deterministic egress for known unicast frames.
- Stage check: `routeforge check lab02`

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab02_mac_learning_switch`
3. Edit only the listed symbols in `src/routeforge/runtime/dataplane_sim.py`.
4. Run `routeforge check lab02` until it exits with status `0`.
5. Run `routeforge run lab02_mac_learning_switch --state-file "$STATE"` to confirm visible lab behavior and progress state updates.

## Verification commands and expected outputs

```bash
routeforge show lab02_mac_learning_switch
routeforge check lab02

STATE=/tmp/routeforge-progress.json
routeforge run lab02_mac_learning_switch --state-file "$STATE"
```

Expected outcomes:

- `routeforge show` prints `student.stage`, `student.target`, and `student.symbols` matching this chapter.
- `routeforge check lab02` passes when your implementation is complete for this stage.
- `unknown_unicast_flood` should print `[PASS]` (unknown unicast floods to all non-ingress ports).
- `known_unicast_forward` should print `[PASS]` (MAC learning enables deterministic unicast forwarding).
- Run output includes checkpoints: PARSE_OK, VLAN_CLASSIFY, MAC_LEARN, L2_FLOOD, L2_UNICAST_FORWARD.

## Debug trace checkpoints and interpretation guidance

Generate trace artifacts when a step fails:

```bash
routeforge run lab02_mac_learning_switch --state-file "$STATE" --trace-out /tmp/lab02_mac_learning_switch.jsonl
routeforge debug replay --trace /tmp/lab02_mac_learning_switch.jsonl
routeforge debug explain --trace /tmp/lab02_mac_learning_switch.jsonl --step unknown_unicast_flood
```

Checkpoint guide:

- `PARSE_OK`: Ethernet/IPv4 frame and header validation behavior.
- `VLAN_CLASSIFY`: VLAN tagging/untagging and per-VLAN forwarding behavior.
- `MAC_LEARN`: MAC learning, unknown unicast flood, deterministic unicast forwarding.
- `L2_FLOOD`: MAC learning, unknown unicast flood, deterministic unicast forwarding.
- `L2_UNICAST_FORWARD`: MAC learning, unknown unicast flood, deterministic unicast forwarding.

## Failure drills and troubleshooting flow

- Intentionally break one listed symbol in `src/routeforge/runtime/dataplane_sim.py` and rerun `routeforge check lab02` to confirm tests catch regressions.
- If `routeforge run lab02_mac_learning_switch --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- IEEE 802.1D (bridging and STP fundamentals).
- IEEE 802.1Q (VLAN tagging and trunk behavior).

