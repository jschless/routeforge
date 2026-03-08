# Lab 37: MPLS LDP and Label Forwarding

## Learning objectives

- Implement `lfib_mapping, mpls_ldp_lfib` in `src/routeforge/runtime/mpls.py`.
- Deliver `ldp_label_alloc`: LDP allocates local label for FEC.
- Deliver `lfib_program`: LFIB programs outgoing label mapping.
- Deliver `mpls_swap_forward`: label swap forwarding path executes deterministically.
- Validate internal behavior through checkpoints: MPLS_LABEL_BIND, MPLS_LFIB_INSTALL.

## Prerequisite recap

- Required prior labs: `lab36_mpbgp_ipv6_unicast`.
- Confirm target mapping before coding with `routeforge show lab37_mpls_ldp_label_forwarding`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

IP forwarding makes routing decisions at every hop by inspecting the destination address and consulting the routing table. At scale this is expensive: each router re-parses the IP header and does a longest-prefix lookup. MPLS (Multiprotocol Label Switching) solves this by doing the expensive lookup only once, at the network edge, then attaching a short integer label to the packet. Every subsequent router performs a simple label swap — look up the incoming label in a table, swap it for an outgoing label, and forward — without touching the IP header.

Key terms:

- **FEC (Forwarding Equivalence Class)**: a set of packets that receive identical forwarding treatment. Usually maps to a destination prefix (e.g., `10.0.0.0/8`).
- **Label**: a 20-bit integer prepended to the packet between the L2 header and the IP header.
- **LDP (Label Distribution Protocol)**: a TCP-based protocol that routers use to advertise which label they want to receive for each FEC. Each router picks a local label and tells its neighbors.
- **LFIB (Label Forwarding Information Base)**: the data structure that maps an incoming label to an outgoing label and egress interface.
- **PHP (Penultimate Hop Popping)**: the second-to-last router removes the MPLS label before forwarding, saving the final router a label lookup. The outgoing label value 3 (implicit null) signals PHP.

A minimal three-node MPLS path looks like this:

```
  CE              P (transit)           PE (egress)
  |               |                     |
  | IP pkt        | label 200 ->        | label 3 (PHP)
  |----[PE ingress]----[P router]----[PE egress]--->
       adds label  swaps 100->200        pops label
       100 for FEC                       delivers IP pkt
```

`mpls_ldp_lfib` models the installation step: given a FEC, a local (incoming) label, and an outgoing label, it records the binding in the LFIB as a `(fec, local_label, outgoing_label)` tuple. `lfib_mapping` is the helper that constructs that tuple in canonical order. Both functions are passthroughs in this lab — the exercise focuses on wiring the data contract correctly so the checkpoints fire in the right sequence.

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/mpls.py`
- Symbols: `lfib_mapping, mpls_ldp_lfib`
- Why this target: define LFIB tuple builder and route forwarding function through same mapping contract.
- Stage check: `routeforge check lab37`

Function contract for this stage:

- Symbol: `lfib_mapping(*, fec: str, local_label: int, outgoing_label: int) -> tuple[str, int, int]`
- Required behavior: return deterministic LFIB tuple in `(FEC, local, outgoing)` order
- Symbol: `mpls_ldp_lfib(*, fec: str, local_label: int, outgoing_label: int) -> tuple[str, int, int]`
- Required behavior: call LFIB mapping contract and return identical tuple format

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab37_mpls_ldp_label_forwarding`
3. Edit only `lfib_mapping, mpls_ldp_lfib` in `src/routeforge/runtime/mpls.py`.
4. Run `routeforge check lab37` until it exits with status `0`.
5. Run `routeforge run lab37_mpls_ldp_label_forwarding --state-file "$STATE"` to confirm visible lab behavior and progress state updates.

## Verification commands and expected outputs

```bash
routeforge show lab37_mpls_ldp_label_forwarding
routeforge check lab37

STATE=/tmp/routeforge-progress.json
routeforge run lab37_mpls_ldp_label_forwarding --state-file "$STATE"
```

Expected outcomes:

- `routeforge show` prints `student.stage`, `student.target`, and `student.symbols` matching this chapter.
- `routeforge check lab37` passes when your implementation is complete for this stage.
- `ldp_label_alloc` should print `[PASS]` (LDP allocates local label for FEC).
- `lfib_program` should print `[PASS]` (LFIB programs outgoing label mapping).
- `mpls_swap_forward` should print `[PASS]` (label swap forwarding path executes deterministically).
- Run output includes checkpoints: MPLS_LABEL_BIND, MPLS_LFIB_INSTALL.

## Debug trace checkpoints and interpretation guidance

Generate trace artifacts when a step fails:

```bash
routeforge run lab37_mpls_ldp_label_forwarding --state-file "$STATE" --trace-out /tmp/lab37_mpls_ldp_label_forwarding.jsonl
routeforge debug replay --trace /tmp/lab37_mpls_ldp_label_forwarding.jsonl
routeforge debug explain --trace /tmp/lab37_mpls_ldp_label_forwarding.jsonl --step ldp_label_alloc
```

Checkpoint guide:

- `MPLS_LABEL_BIND`: fires when an LDP label binding is installed — meaning a FEC has been successfully mapped to a local label and an outgoing label pair. If this checkpoint is missing, `mpls_ldp_lfib` is not returning the tuple (or is raising before returning), so the binding was never recorded. Check that your function returns `(fec, local_label, outgoing_label)` rather than `None` or a reordered tuple.

- `MPLS_LFIB_INSTALL`: fires when the LFIB entry is confirmed installed and ready for forwarding — the runtime has accepted the binding from `MPLS_LABEL_BIND` and written it into the forwarding table. If `MPLS_LABEL_BIND` fired but `MPLS_LFIB_INSTALL` is absent, the tuple was returned in the wrong field order, causing the install step to reject it. Verify that `lfib_mapping` places fields as `(fec, local_label, outgoing_label)` — swapping local and outgoing will pass type checks but break the install assertion.

## Failure drills and troubleshooting flow

- Intentionally break `lfib_mapping` or `mpls_ldp_lfib` in `src/routeforge/runtime/mpls.py` and rerun `routeforge check lab37` to confirm tests catch regressions.
- If `routeforge run lab37_mpls_ldp_label_forwarding --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- MPLS LDP and LFIB behavior.
