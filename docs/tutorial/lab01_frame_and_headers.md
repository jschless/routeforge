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

### What is an Ethernet frame?

Every packet sent over an Ethernet network is wrapped in a *frame* — a fixed-format envelope that tells the network where to deliver it.  A frame contains:

- **src_mac / dst_mac** — 48-bit hardware addresses in `aa:bb:cc:dd:ee:ff` format (6 groups of hex digits separated by colons).
- **ethertype** — a 16-bit number identifying the payload type: `0x0800` for IPv4, `0x86DD` for IPv6, etc.  Valid range: 0–65535.
- **vlan_id** (optional) — a 12-bit VLAN tag; valid range 1–4094 (0 and 4095 are reserved).
- **payload** — for these labs, always an `IPv4Header`.

### What is an IPv4 header?

The payload carries L3 addressing:

- **src_ip / dst_ip** — dotted-decimal IPv4 addresses (`"192.0.2.1"`).  Must be parseable by `ipaddress.IPv4Address`.
- **ttl** — Time to Live, a hop counter that prevents routing loops.  Packets with TTL ≤ 1 are dropped (TTL is checked *before* decrement, so TTL=1 means "drop here").

### Validation rules

| Field | Valid condition | Error code |
|---|---|---|
| `src_mac` | matches `XX:XX:XX:XX:XX:XX` hex pattern | `L2_INVALID_SRC_MAC` |
| `dst_mac` | matches `XX:XX:XX:XX:XX:XX` hex pattern | `L2_INVALID_DST_MAC` |
| `ethertype` | `0 <= ethertype < 65536` | `L2_UNSUPPORTED_ETHERTYPE` |
| `vlan_id` | None, or `1 <= vlan_id <= 4094` | `L2_INVALID_VLAN` |
| `src_ip` | valid IPv4 address string | `L3_INVALID_SRC_IP` |
| `dst_ip` | valid IPv4 address string | `L3_INVALID_DST_IP` |
| `ttl` | `ttl > 1` | `L3_INVALID_TTL` |

**Spot the bug:** the pre-filled ethertype check in `packet.py` has an operator precedence error.  Find it and fix it before running the tests.

Student-mode coding target for this stage is `src/routeforge/model/packet.py` (`is_valid_mac, IPv4Header.validate, EthernetFrame.validate`).

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

Use these exact strings in your implementation — they are the expected error codes checked by the tests.

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

- `PARSE_OK`: Frame passed full L2+L3 validation — all fields are well-formed.
  If missing for a valid frame, your `EthernetFrame.validate()` or `IPv4Header.validate()`
  is returning unexpected errors.  Check the ethertype operator precedence bug.
- `VLAN_CLASSIFY`: VLAN classification succeeded — the ingress port accepted the frame's
  tag/untagged state.  Follows `PARSE_OK` on the valid frame path.
- `MAC_LEARN`: Source MAC was learned into the FDB.  Expected for valid frames on known interfaces.
- `L2_FLOOD`: Frame is being flooded (broadcast or unknown unicast destination).
  Expected for the first frame in the lab since no FDB entries exist yet.
- `PARSE_DROP`: Frame was dropped during or after parsing.  Expected for the invalid frame
  (bad src_mac).  If this fires for a valid frame, check your validation logic for false
  positives (e.g., the ethertype bug accepting out-of-range values).

## Failure drills and troubleshooting flow

- Intentionally break one listed symbol in `src/routeforge/model/packet.py` and rerun `routeforge check lab01` to confirm tests catch regressions.
- If `routeforge run lab01_frame_and_headers --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- IEEE 802.1D (bridging and STP fundamentals).
- IEEE 802.1Q (VLAN tagging and trunk behavior).

## Concept Deepening Notes

Frame validation is the first contract boundary in RouteForge. The most important mental model is that malformed input must fail deterministically with explicit reason strings, not ad hoc exceptions. Later labs assume this boundary is stable, so consistency in error classification here prevents cascading ambiguity when forwarding, ACL, or routing logic is layered on top.

## Checkpoint Guide (Expanded)

- `PARSE_OK`: Confirm this marker appears when your implementation follows the intended decision path.
- `VLAN_CLASSIFY`: Confirm this marker appears when your implementation follows the intended decision path.
- `MAC_LEARN`: Confirm this marker appears when your implementation follows the intended decision path.
- `L2_FLOOD`: Confirm this marker appears when your implementation follows the intended decision path.
- `PARSE_DROP`: Confirm this marker appears when your implementation follows the intended decision path.
