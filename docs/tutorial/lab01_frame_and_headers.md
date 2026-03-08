# Lab 01: Frame and Header Validation

## Learning objectives

- Implement `is_valid_mac, IPv4Header.validate, EthernetFrame.__post_init__, EthernetFrame.validate` in `src/routeforge/model/packet.py`.
- Deliver `valid_frame_parses`: valid frame passes Ethernet and IPv4 validation.
- Deliver `invalid_frame_drops`: invalid frame is rejected with parse-drop checkpoint.
- Validate internal behavior through checkpoints: PARSE_OK, PARSE_DROP.

## Prerequisite recap

- Required prior labs: none.
- Confirm target mapping before coding with `routeforge show lab01_frame_and_headers`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

### What is an Ethernet frame?

Every packet sent over an Ethernet network is wrapped in a *frame* — a fixed-format envelope that tells the network where to deliver it.  A frame contains:

- **src_mac / dst_mac** — 48-bit hardware addresses in `aa:bb:cc:dd:ee:ff` format (6 groups of hex digits separated by colons).
- **ethertype** — a 16-bit number identifying the payload type: `0x0800` for IPv4, `0x86DD` for IPv6, etc.  Valid range: 0–65535.  Out-of-range values are rejected when the frame object is constructed.
- **vlan_id** (optional) — a 12-bit VLAN tag; valid range 1–4094 (0 and 4095 are reserved).  Out-of-range values are rejected when the frame object is constructed.
- **payload** — for these labs, always an `IPv4Header`.

### What is an IPv4 header?

The payload carries L3 addressing:

- **src_ip / dst_ip** — dotted-decimal IPv4 addresses (`"192.0.2.1"`).  Must be parseable by `ipaddress.IPv4Address`.
- **ttl** — Time to Live, a hop counter that prevents routing loops.  Packets with TTL ≤ 1 are invalid for this lab and are later dropped by the forwarding pipeline as well.

### Validation rules

| Field | Valid condition | Error code |
|---|---|---|
| `src_mac` | matches `XX:XX:XX:XX:XX:XX` hex pattern | `L2_INVALID_SRC_MAC` |
| `dst_mac` | matches `XX:XX:XX:XX:XX:XX` hex pattern | `L2_INVALID_DST_MAC` |
| `ethertype` | in range and equal to `0x0800` for this lab | `L2_UNSUPPORTED_ETHERTYPE` |
| `src_ip` | valid IPv4 address string | `L3_INVALID_SRC_IP` |
| `dst_ip` | valid IPv4 address string | `L3_INVALID_DST_IP` |
| `ttl` | `ttl > 1` | `L3_INVALID_TTL` |

Construction-time guards:

- `EthernetFrame(ethertype=...)` raises `ValueError` if the ethertype is outside `0..65535`.
- `EthernetFrame(vlan_id=...)` raises `ValueError` if the VLAN is outside `1..4094`.
- `EthernetFrame.validate()` still handles semantic checks such as unsupported but in-range ethertypes.

Student-mode coding target for this stage is `src/routeforge/model/packet.py` (`is_valid_mac, IPv4Header.validate, EthernetFrame.__post_init__, EthernetFrame.validate`).

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/model/packet.py`
- Symbols: `is_valid_mac, IPv4Header.validate, EthernetFrame.__post_init__, EthernetFrame.validate`
- Why this target: Validate Ethernet and IPv4 header fields.
- Stage check: `routeforge check lab01`

Required error-code strings for this lab (exact match):

- `L2_INVALID_SRC_MAC`
- `L2_INVALID_DST_MAC`
- `L2_UNSUPPORTED_ETHERTYPE`
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
- `valid_frame_parses` should print `[PASS]` (valid frame passes Ethernet and IPv4 validation).
- `invalid_frame_drops` should print `[PASS]` (invalid frame is rejected with parse-drop checkpoint).
- Run output includes checkpoints: PARSE_OK, PARSE_DROP.

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
  is returning unexpected errors.  Check your MAC, IPv4, and TTL validation logic first.
- `PARSE_DROP`: Frame was dropped during or after parsing.  Expected for the invalid frame
  (bad src_mac).  If this fires for a valid frame, check your validation logic for false
  positives.  Out-of-range ethertype or VLAN values should fail earlier with `ValueError`.

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
- `PARSE_DROP`: Confirm this marker appears when your implementation follows the intended decision path.
