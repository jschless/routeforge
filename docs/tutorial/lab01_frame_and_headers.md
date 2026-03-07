# Lab 01: Frame and Header Validation

## Learning objectives

- Implement `is_valid_mac, IPv4Header.validate, EthernetFrame.validate` in `src/routeforge/model/packet.py`.
- Deliver `valid_frame_parses`: valid frame is accepted and forwarded/flooded.
- Deliver `invalid_frame_drops`: invalid frame is rejected with parse-drop checkpoint.
- Validate internal behavior through checkpoints: PARSE_OK, VLAN_CLASSIFY, MAC_LEARN, L2_FLOOD, PARSE_DROP.

## Prerequisite recap

- Required prior labs: none.
- Confirm target mapping before coding with `routeforge show lab01_frame_and_headers`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

Ethernet/IPv4 frame and header validation behavior. Student-mode coding target for this stage is `src/routeforge/model/packet.py` (`is_valid_mac, IPv4Header.validate, EthernetFrame.validate`).

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/model/packet.py`
- Symbols: `is_valid_mac, IPv4Header.validate, EthernetFrame.validate`
- Why this target: Validate Ethernet and IPv4 header fields.
- Stage check: `routeforge check lab01`

Required error-code strings for this lab (exact match):

- `L2_INVALID_SRC_MAC`
- `L2_INVALID_DST_MAC`
- `L2_UNSUPPORTED_ETHERTYPE`
- `L2_INVALID_VLAN`
- `L3_INVALID_SRC_IP`
- `L3_INVALID_DST_IP`
- `L3_INVALID_TTL`

These are also declared in `src/routeforge/model/packet.py` for direct in-code reference.

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab01_frame_and_headers`
3. Edit only the listed symbols in `src/routeforge/model/packet.py`.
4. Run `routeforge check lab01` until it exits with status `0`.
5. Run `routeforge run lab01_frame_and_headers --state-file "$STATE"` to confirm visible lab behavior and progress state updates.

## Verification commands and expected outputs

```bash
routeforge show lab01_frame_and_headers
routeforge check lab01

STATE=/tmp/routeforge-progress.json
routeforge run lab01_frame_and_headers --state-file "$STATE"
```

Expected outcomes:

- `routeforge show` prints `student.stage`, `student.target`, and `student.symbols` matching this chapter.
- `routeforge check lab01` passes when your implementation is complete for this stage.
- `valid_frame_parses` should print `[PASS]` (valid frame is accepted and forwarded/flooded).
- `invalid_frame_drops` should print `[PASS]` (invalid frame is rejected with parse-drop checkpoint).
- Run output includes checkpoints: PARSE_OK, VLAN_CLASSIFY, MAC_LEARN, L2_FLOOD, PARSE_DROP.

## Debug trace checkpoints and interpretation guidance

Generate trace artifacts when a step fails:

```bash
routeforge run lab01_frame_and_headers --state-file "$STATE" --trace-out /tmp/lab01_frame_and_headers.jsonl
routeforge debug replay --trace /tmp/lab01_frame_and_headers.jsonl
routeforge debug explain --trace /tmp/lab01_frame_and_headers.jsonl --step valid_frame_parses
```

Checkpoint guide:

- `PARSE_OK`: Ethernet/IPv4 frame and header validation behavior.
- `VLAN_CLASSIFY`: VLAN tagging/untagging and per-VLAN forwarding behavior.
- `MAC_LEARN`: MAC learning, unknown unicast flood, deterministic unicast forwarding.
- `L2_FLOOD`: MAC learning, unknown unicast flood, deterministic unicast forwarding.
- `PARSE_DROP`: Ethernet/IPv4 frame and header validation behavior.

## Failure drills and troubleshooting flow

- Intentionally break one listed symbol in `src/routeforge/model/packet.py` and rerun `routeforge check lab01` to confirm tests catch regressions.
- If `routeforge run lab01_frame_and_headers --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- IEEE 802.1D (bridging and STP fundamentals).
- IEEE 802.1Q (VLAN tagging and trunk behavior).
