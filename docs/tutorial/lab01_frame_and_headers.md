# Lab 01: Frame and Header Validation

## Learning objectives

- Validate Ethernet MAC address format and IPv4 header basics.
- Distinguish accepted frames from dropped frames.
- Read `PARSE_OK` and `PARSE_DROP` checkpoints.

## Prerequisite recap

- No prior lab prerequisites.
- Basic familiarity with Ethernet and IPv4 addressing.

## Concept walkthrough

`lab01` validates frame/header structure before forwarding behavior is considered. A valid frame moves forward in the pipeline, while malformed fields are rejected deterministically.

## Implementation TODO map

- `src/routeforge/model/packet.py`: validation rules for MAC/IP/TTL.
- `src/routeforge/runtime/dataplane_sim.py`: parse gate and drop reasons.

## Verification commands and expected outputs

```bash
PYTHONPATH=src python -m routeforge run lab01_frame_and_headers
```

Expected:

- Two step checks printed.
- One `PASS` for valid parse path.
- One `PASS` for invalid parse drop path.
- Checkpoints include `PARSE_OK` and `PARSE_DROP`.

## Debug trace checkpoints and interpretation guidance

- `PARSE_OK`: frame/header passed validation.
- `PARSE_DROP`: validation failed and frame was dropped.

## Failure drills and troubleshooting flow

- Break MAC format (non-hex octet) and confirm `PARSE_DROP`.
- Set IPv4 TTL to `0` and confirm deterministic drop reason.

## Standards and references

- IEEE 802.3 Ethernet framing basics.
- RFC 791 (IPv4).
