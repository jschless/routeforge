# Lab 28: DHCP Snooping and DAI

## Learning objectives

- Implement `learn_binding_if_trusted, dhcp_snooping_dai` in `src/routeforge/runtime/security.py`.
- Deliver `dhcp_binding_learn`: trusted DHCP flow learns binding.
- Deliver `dai_validate_match`: matching ARP is accepted.
- Deliver `dai_drop_mismatch`: mismatched ARP is dropped.
- Validate internal behavior through checkpoints: DHCP_BINDING_LEARN, DAI_VALIDATE, DAI_DROP.

## Prerequisite recap

- Required prior labs: `lab27_capstone_incident_drill`.
- Confirm target mapping before coding with `routeforge show lab28_dhcp_snooping_and_dai`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

### The problem: ARP is unauthenticated

On a standard Ethernet switch, any host can send a gratuitous ARP claiming to own any IP address. An attacker on an untrusted port can poison the ARP caches of every other host on the VLAN, redirecting traffic through themselves (a man-in-the-middle attack). Neither the switch nor the receiving hosts have any way to distinguish the legitimate ARP from the spoofed one.

DHCP snooping and Dynamic ARP Inspection (DAI) work together to solve this. DHCP snooping watches DHCP exchanges on trusted ports and builds a binding table that maps each client MAC address to the IP address the DHCP server legitimately assigned it. DAI then uses that binding table as a ground truth to validate ARP packets before they are forwarded.

### Key terms

- **Trusted port**: A port connected to a DHCP server or upstream infrastructure. DHCP responses and ARP packets arriving here are accepted unconditionally, and new bindings are learned from ARP traffic if no binding exists yet.
- **Untrusted port**: A port connected to an end host. Frames here are subject to full inspection.
- **DHCP binding**: A record of `(mac, ip, vlan)` established when a host successfully completes DHCP on a trusted port. It is the authoritative record of what IP a MAC is allowed to use.
- **DAI (Dynamic ARP Inspection)**: The enforcement step. Before forwarding an ARP, the switch compares the sender MAC and sender IP fields against the binding table. A mismatch means the ARP is spoofed and it is dropped.

### Topology

```
                   Trusted port
  DHCP Server ─────────────────┐
                                │
                            [ Switch ]
                                │
  Host A ──────────────────────┘
  (untrusted port)
```

When Host A completes DHCP, the exchange arrives at the trusted uplink. The switch records `DhcpBinding(mac=A_mac, ip=A_ip, vlan=10)`. When Host A later sends an ARP, the switch checks: does the ARP sender MAC match `A_mac` and sender IP match `A_ip`? If yes, the ARP is forwarded (DAI_VALIDATE). If an attacker on another untrusted port sends an ARP claiming `A_ip`, the binding check fails and the frame is dropped (DAI_DROP).

### How the two functions compose

`learn_binding_if_trusted` handles the learning half: it is called whenever an ARP arrives, but only creates a new `DhcpBinding` when the port is trusted and no binding already exists. If a binding already exists it is returned unchanged — this prevents a trusted port from overwriting an established binding with spoofed data.

`dhcp_snooping_dai` handles the enforcement half. It calls `learn_binding_if_trusted` internally and then applies the DAI rule: trusted port always passes, untrusted with no binding drops, untrusted with a binding drops if the ARP MAC does not match the binding MAC.

Correct behavior summary:
- Trusted port, no prior binding → binding is created, ARP is ALLOWED
- Trusted port, binding already present → binding unchanged, ARP is ALLOWED
- Untrusted port, no binding → (None, "DROP")
- Untrusted port, binding present, MAC matches → (binding, "ALLOW")
- Untrusted port, binding present, MAC mismatch → (binding, "DROP")

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/security.py`
- Symbols: `learn_binding_if_trusted, dhcp_snooping_dai`
- Why this target: implement trusted-port binding learn and deterministic DAI validation outcomes.
- Stage check: `routeforge check lab28`

Function contract for this stage:

- Symbol: `learn_binding_if_trusted(*, trusted_port: bool, binding: DhcpBinding | None, arp_mac: str, arp_ip: str, default_vlan: int = 10) -> DhcpBinding | None`
- Required behavior: learn only on trusted ingress when no prior binding exists
- Symbol: `dhcp_snooping_dai(*, trusted_port: bool, binding: DhcpBinding | None, arp_mac: str, arp_ip: str) -> tuple[DhcpBinding | None, Literal["ALLOW", "DROP"]]`
- Required behavior: return ALLOW only when resolved binding matches ARP MAC+IP

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab28_dhcp_snooping_and_dai`
3. Edit only `learn_binding_if_trusted, dhcp_snooping_dai` in `src/routeforge/runtime/security.py`.
4. Run `routeforge check lab28` until it exits with status `0`.
5. Run `routeforge run lab28_dhcp_snooping_and_dai --state-file "$STATE"` to confirm visible lab behavior and progress state updates.

## Verification commands and expected outputs

```bash
routeforge show lab28_dhcp_snooping_and_dai
routeforge check lab28

STATE=/tmp/routeforge-progress.json
routeforge run lab28_dhcp_snooping_and_dai --state-file "$STATE"
```

Expected outcomes:

- `routeforge show` prints `student.stage`, `student.target`, and `student.symbols` matching this chapter.
- `routeforge check lab28` passes when your implementation is complete for this stage.
- `dhcp_binding_learn` should print `[PASS]` (trusted DHCP flow learns binding).
- `dai_validate_match` should print `[PASS]` (matching ARP is accepted).
- `dai_drop_mismatch` should print `[PASS]` (mismatched ARP is dropped).
- Run output includes checkpoints: DHCP_BINDING_LEARN, DAI_VALIDATE, DAI_DROP.

## Debug trace checkpoints and interpretation guidance

Generate trace artifacts when a step fails:

```bash
routeforge run lab28_dhcp_snooping_and_dai --state-file "$STATE" --trace-out /tmp/lab28_dhcp_snooping_and_dai.jsonl
routeforge debug replay --trace /tmp/lab28_dhcp_snooping_and_dai.jsonl
routeforge debug explain --trace /tmp/lab28_dhcp_snooping_and_dai.jsonl --step dhcp_binding_learn
```

Checkpoint guide:

- `DHCP_BINDING_LEARN`: A new `DhcpBinding` was created and stored for this MAC/IP/VLAN triple. This fires only when `trusted_port=True` and the incoming binding was `None`. If this checkpoint is missing during the `dhcp_binding_learn` step, your `learn_binding_if_trusted` is not constructing a new binding — check that you return a fresh `DhcpBinding` rather than `None` when both conditions are satisfied.
- `DAI_VALIDATE`: An ARP on an untrusted port was compared against an existing binding and the sender MAC matched the binding MAC. The frame was allowed to forward. If this checkpoint is missing during `dai_validate_match`, your comparison logic is not reaching the ALLOW branch — check that you are comparing `arp_mac` against `binding.mac` and returning `"ALLOW"` on equality.
- `DAI_DROP`: An ARP was rejected. This fires in two situations: the port is untrusted and no binding exists for the sender IP, or the port is untrusted and the sender MAC does not match the binding MAC. If this checkpoint is missing during `dai_drop_mismatch`, your enforcement is not catching MAC mismatches — verify that a non-matching `arp_mac` returns `"DROP"` even when a binding is present.

## Failure drills and troubleshooting flow

- Intentionally break `learn_binding_if_trusted` or `dhcp_snooping_dai` in `src/routeforge/runtime/security.py` and rerun `routeforge check lab28` to confirm tests catch regressions.
- If `routeforge run lab28_dhcp_snooping_and_dai --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- DHCP snooping and dynamic ARP inspection controls.
