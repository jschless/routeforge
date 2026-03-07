# Lab 28: DHCP Snooping and DAI

## Learning objectives

- Implement `learn_binding_if_trusted, dhcp_snooping_dai` in `src/routeforge/runtime/phase2.py`.
- Deliver `dhcp_binding_learn`: trusted DHCP flow learns binding.
- Deliver `dai_validate_match`: matching ARP is accepted.
- Deliver `dai_drop_mismatch`: mismatched ARP is dropped.
- Validate internal behavior through checkpoints: DHCP_BINDING_LEARN, DAI_VALIDATE, DAI_DROP.

## Prerequisite recap

- Required prior labs: `lab27_capstone_incident_drill`.
- Confirm target mapping before coding with `routeforge show lab28_dhcp_snooping_and_dai`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

Layer-2 access security with binding-based ARP validation. Student-mode coding target for this stage is `src/routeforge/runtime/phase2.py` (`learn_binding_if_trusted, dhcp_snooping_dai`).

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/phase2.py`
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
3. Edit only `learn_binding_if_trusted, dhcp_snooping_dai` in `src/routeforge/runtime/phase2.py`.
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

- `DHCP_BINDING_LEARN`: first expected pipeline milestone.
- `DAI_VALIDATE`: second expected pipeline milestone.
- `DAI_DROP`: third expected pipeline milestone.

## Failure drills and troubleshooting flow

- Intentionally break `learn_binding_if_trusted` or `dhcp_snooping_dai` in `src/routeforge/runtime/phase2.py` and rerun `routeforge check lab28` to confirm tests catch regressions.
- If `routeforge run lab28_dhcp_snooping_and_dai --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- DHCP snooping and dynamic ARP inspection controls.
