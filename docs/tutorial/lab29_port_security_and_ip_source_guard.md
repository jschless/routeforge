# Lab 29: Port Security and IP Source Guard

## Learning objectives

- Implement `update_secure_mac_table, port_security_ip_source_guard` in `src/routeforge/runtime/security.py`.
- Deliver `portsec_learn`: first host is learned under port-security limit.
- Deliver `portsec_violation`: exceeding secure MAC limit triggers violation.
- Deliver `ipsg_deny`: invalid source IP is denied.
- Validate internal behavior through checkpoints: PORTSEC_LEARN, PORTSEC_VIOLATION, IPSG_DENY.

## Prerequisite recap

- Required prior labs: `lab28_dhcp_snooping_and_dai`.
- Confirm target mapping before coding with `routeforge show lab29_port_security_and_ip_source_guard`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

### The problem: uncontrolled MAC proliferation and IP spoofing

A standard switch port will learn as many MAC addresses as its table allows. An attacker can flood the switch's MAC table by sending frames with thousands of fabricated source MACs, causing the switch to fall back to flooding all traffic out every port — a MAC flooding attack. Even a legitimate misconfiguration such as an unmanaged hub or a VM host running many VMs can exhaust table space unintentionally.

Port security limits the number of MAC addresses that can be learned on a single port. IP Source Guard (IPSG) adds a second layer: even after a MAC is admitted, the source IP in the frame is checked against the DHCP binding table (from lab 28). A host that passes MAC-level port security but sends traffic from an IP address it was not assigned is still denied.

### Key terms

- **Secure MAC limit (`max_macs`)**: The maximum number of distinct source MACs the port is allowed to learn. Once this limit is reached, any frame from a new, unknown MAC triggers a violation rather than learning.
- **PORTSEC_VIOLATION**: The action taken when the MAC table is full and an unknown source MAC arrives. In this lab the violation action is to deny the frame; the MAC table is not modified.
- **IP Source Guard (IPSG)**: A per-frame IP validation step applied after port security passes. The source IP in the frame is checked against an allowed-IP set (typically derived from the DHCP binding table). A frame from an IP that is not in the allowed set is denied with `IPSG_DENY`.
- **Policy evaluation order**: Port security runs first. If the frame fails port security the check stops with `PORTSEC_VIOLATION`. Only frames that pass port security proceed to IPSG evaluation.

### Decision flow

```
Frame arrives on port
        │
        ▼
Is source_mac already in learned_macs?
  ├─ Yes → skip learning, go to IPSG check
  └─ No  → is len(learned_macs) >= max_macs?
              ├─ Yes → return (learned_macs, "PORTSEC_VIOLATION")  [stop]
              └─ No  → add source_mac to learned_macs, go to IPSG check
        │
        ▼
IPSG check: is source_ip_allowed?
  ├─ Yes → return (learned_macs, "ALLOW")
  └─ No  → return (learned_macs, "IPSG_DENY")
```

### Why the MAC table is immutable on violation

The learned MAC table is returned as a tuple (immutable). On a `PORTSEC_VIOLATION` the original tuple is returned unchanged — the new MAC is never added. This models the hardware behavior where the violation action (shutdown, restrict, or protect) does not modify the existing forwarding table entry set.

### What correct behavior looks like

A port configured with `max_macs=2`:
- Frame 1 from `aa:bb` → learn, check IP → `ALLOW` (PORTSEC_MAC_LEARN fires)
- Frame 2 from `cc:dd` → learn, check IP → `ALLOW` (PORTSEC_MAC_LEARN fires)
- Frame 3 from `ee:ff` → table full → `PORTSEC_VIOLATION` (no learn)
- Frame 4 from `aa:bb` with a spoofed IP → already known MAC, IP not in allowed set → `IPSG_DENY`

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/security.py`
- Symbols: `update_secure_mac_table, port_security_ip_source_guard`
- Why this target: implement secure-MAC table update semantics and final policy action resolution.
- Stage check: `routeforge check lab29`

Function contract for this stage:

- Symbol: `update_secure_mac_table(*, max_macs: int, learned_macs: tuple[str, ...], source_mac: str) -> tuple[tuple[str, ...], bool]`
- Required behavior: return stable learned-MAC tuple and violation flag when capacity is exceeded
- Symbol: `port_security_ip_source_guard(*, max_macs: int, learned_macs: tuple[str, ...], source_mac: str, source_ip_allowed: bool) -> tuple[tuple[str, ...], Literal["ALLOW", "PORTSEC_VIOLATION", "IPSG_DENY"]]`
- Required behavior: enforce port-security first, then return IP source guard deny/allow

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab29_port_security_and_ip_source_guard`
3. Edit only `update_secure_mac_table, port_security_ip_source_guard` in `src/routeforge/runtime/security.py`.
4. Run `routeforge check lab29` until it exits with status `0`.
5. Run `routeforge run lab29_port_security_and_ip_source_guard --state-file "$STATE"` to confirm visible lab behavior and progress state updates.

## Verification commands and expected outputs

```bash
routeforge show lab29_port_security_and_ip_source_guard
routeforge check lab29

STATE=/tmp/routeforge-progress.json
routeforge run lab29_port_security_and_ip_source_guard --state-file "$STATE"
```

Expected outcomes:

- `routeforge show` prints `student.stage`, `student.target`, and `student.symbols` matching this chapter.
- `routeforge check lab29` passes when your implementation is complete for this stage.
- `portsec_learn` should print `[PASS]` (first host is learned under port-security limit).
- `portsec_violation` should print `[PASS]` (exceeding secure MAC limit triggers violation).
- `ipsg_deny` should print `[PASS]` (invalid source IP is denied).
- Run output includes checkpoints: PORTSEC_LEARN, PORTSEC_VIOLATION, IPSG_DENY.

## Debug trace checkpoints and interpretation guidance

Generate trace artifacts when a step fails:

```bash
routeforge run lab29_port_security_and_ip_source_guard --state-file "$STATE" --trace-out /tmp/lab29_port_security_and_ip_source_guard.jsonl
routeforge debug replay --trace /tmp/lab29_port_security_and_ip_source_guard.jsonl
routeforge debug explain --trace /tmp/lab29_port_security_and_ip_source_guard.jsonl --step portsec_learn
```

Checkpoint guide:

- `PORTSEC_MAC_LEARN`: A new source MAC was successfully added to the learned MAC table because the table had room. This fires only when the MAC was not already present and `len(learned_macs) < max_macs`. If this checkpoint is missing during the `portsec_learn` step, your implementation is not adding the new MAC to the tuple — verify that you construct and return an updated tuple with the new MAC appended.
- `PORTSEC_VIOLATION`: The MAC table was at capacity and an unknown source MAC arrived. The frame is denied and the table is not modified. If this checkpoint is missing during the `portsec_violation` step, your implementation is either learning the MAC beyond the limit (check the `>=` boundary condition) or is not returning `"PORTSEC_VIOLATION"` — confirm that you stop processing and return the original unchanged tuple.
- `IPSG_DENY`: Port security passed (the MAC is known or was just learned), but the source IP was not in the allowed set. This checkpoint fires after MAC admission, not before — if you see `PORTSEC_VIOLATION` and `IPSG_DENY` on the same frame, the policy ordering is wrong. If `IPSG_DENY` is missing during the `ipsg_deny` step, check that you evaluate `source_ip_allowed` after the MAC check and return `"IPSG_DENY"` when it is `False`.

## Failure drills and troubleshooting flow

- Intentionally break `update_secure_mac_table` or `port_security_ip_source_guard` in `src/routeforge/runtime/security.py` and rerun `routeforge check lab29` to confirm tests catch regressions.
- If `routeforge run lab29_port_security_and_ip_source_guard --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- Port security and IP source guard behavior.
