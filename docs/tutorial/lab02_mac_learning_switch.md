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

### What problem does MAC learning solve?

Without MAC learning, every frame sent into a switch must be *flooded* to all ports — the switch has no way to know which port leads to the destination host.  MAC learning eliminates unnecessary flooding by recording which host is behind which port.

### Topology

```
  Host A                 Switch (R1)                Host B
(00:11:22:33:44:55)   +--eth0---eth1--+   (00:11:22:33:44:66)
       |               |               |               |
       +---------------+               +---------------+
                               eth2
                                |
                          Host C (00:11:22:33:44:77)
```

Three hosts are connected to a single switch on ports `eth0`, `eth1`, and `eth2`.  All ports are in the same VLAN (access VLAN 1).

### How it works

1. **Frame arrives** on an ingress port.
2. **MAC learning**: the switch records `(VLAN, src_mac) → ingress_port` in the Forwarding Database (FDB).
3. **Destination lookup**: the switch looks up `(VLAN, dst_mac)` in the FDB.
   - **Miss (unknown unicast)** or **broadcast** → *flood* to all ports in the VLAN except the ingress port.
   - **Hit (known unicast)** → forward only to the learned port.

### Same-port destination

If the FDB lookup returns the same port the frame arrived on, the destination is behind the same physical segment.  Forwarding would loop the frame back — instead, *drop* it with reason `L2_SAME_PORT_DESTINATION`.

### What correct behavior looks like

- First frame from a new host → `action="FLOOD"`, `reason="L2_UNKNOWN_UNICAST_FLOOD"`, all non-ingress ports in egress.
- Second frame after both hosts have sent → `action="FORWARD"`, `reason="L2_FDB_HIT"`, only the destination port in egress.
- Frame whose destination equals the ingress port → `action="DROP"`, `reason="L2_SAME_PORT_DESTINATION"`.

Student-mode coding target for this stage is `src/routeforge/runtime/dataplane_sim.py` (`DataplaneSim._select_known_unicast_egress`).

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

- `PARSE_OK`: Frame passed header validation — MACs, ethertype, and payload are well-formed.
  If this is missing and `PARSE_DROP` appears instead, check your `EthernetFrame.validate()`.
- `VLAN_CLASSIFY`: Ingress VLAN has been assigned based on port mode (access/trunk).
  If missing, the frame was dropped before VLAN processing — check ingress interface lookup.
- `MAC_LEARN`: The source MAC was recorded in the FDB for this VLAN and port.
  If missing, your `router.learn_mac()` path was not reached.
- `L2_FLOOD`: Frame is being flooded because destination is unknown unicast or broadcast.
  Expected on the first frame from each new host pair.
- `L2_UNICAST_FORWARD`: FDB hit — frame is being sent only to the known destination port.
  If missing when expected, verify your `_select_known_unicast_egress` is returning the correct port.

## Failure drills and troubleshooting flow

- Intentionally break one listed symbol in `src/routeforge/runtime/dataplane_sim.py` and rerun `routeforge check lab02` to confirm tests catch regressions.
- If `routeforge run lab02_mac_learning_switch --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- IEEE 802.1D (bridging and STP fundamentals).
- IEEE 802.1Q (VLAN tagging and trunk behavior).

