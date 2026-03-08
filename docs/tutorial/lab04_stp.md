# Lab 04: Spanning Tree

## Learning objectives

- Implement `compute_stp` in `src/routeforge/runtime/stp.py`.
- Deliver `stp_root_election`: lowest bridge ID is selected as deterministic root.
- Deliver `stp_port_roles`: root/designated/alternate roles are assigned deterministically.
- Validate internal behavior through checkpoints: STP_ROOT_CHANGE, STP_PORT_ROLE_CHANGE.

## Prerequisite recap

- Required prior labs: lab03_vlan_and_trunks.
- Confirm target mapping before coding with `routeforge show lab04_stp`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

### What problem does STP solve?

Ethernet networks can have physical loops — multiple paths between switches that cause frames to circulate forever.  Spanning Tree Protocol (STP) detects loops and logically disables enough ports to make the network a *tree* (loop-free), while keeping redundant links available for failover.

### Topology

```
        Bridge A (priority=32768, mac="aa:aa:aa:aa:aa:01")
           /           \
      cost=4          cost=4
        /                 \
Bridge B                Bridge C
(priority=32768,        (priority=32768,
 mac="bb:bb:bb:bb:bb:02") mac="cc:cc:cc:cc:cc:03")
           \                /
           cost=4        cost=4
                \        /
                Bridge D
               (priority=32768,
                mac="dd:dd:dd:dd:dd:04")
```

Four bridges in a ring — any two bridges have two paths between them.  STP must block at least one port to eliminate the loop.

### How it works

**Step 1 — Elect root bridge**
Every bridge compares its `BridgeID = (priority, mac)`.  The *lowest* BridgeID wins.  With equal priorities, the lowest MAC address is elected root.  In the topology above, Bridge A wins (lowest MAC).

**Step 2 — Compute root path costs**
Each non-root bridge computes the total link cost to reach the root.  BFS/Dijkstra from the root, summing link costs.  Bridge B and C are cost 4 from A; Bridge D is cost 8 (via B or C — both equal).

**Step 3 — Assign root ports**
Each non-root bridge picks the port on the cheapest path to root as its *root port*.  Tiebreak: lower port_id string wins.

**Step 4 — Assign designated ports**
On each link segment, the bridge with the lower root path cost becomes *designated* on that segment.  Tiebreak: lower bridge_id, then lower port_id.

**Step 5 — Block remaining ports**
Any port not elected root or designated becomes *alternate* (blocked).  This breaks the loop.

### What correct behavior looks like

- `result.root_node_id` is the bridge with the lowest `BridgeID`.
- Every non-root bridge has exactly one ROOT port in `port_roles`.
- Every link segment has exactly one DESIGNATED port.
- All remaining ports are ALTERNATE.

Student-mode coding target for this stage is `src/routeforge/runtime/stp.py` (`compute_stp`).

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/stp.py`
- Symbols: `compute_stp`
- Why this target: Compute deterministic STP root and port roles.
- Stage check: `routeforge check lab04`

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab04_stp`
3. Edit only the listed symbols in `src/routeforge/runtime/stp.py`.
4. Run `routeforge check lab04` until it exits with status `0`.
5. Run `routeforge run lab04_stp --state-file "$STATE"` to confirm visible lab behavior and progress state updates.

## Verification commands and expected outputs

```bash
routeforge show lab04_stp
routeforge check lab04

STATE=/tmp/routeforge-progress.json
routeforge run lab04_stp --state-file "$STATE"
```

Expected outcomes:

- `routeforge show` prints `student.stage`, `student.target`, and `student.symbols` matching this chapter.
- `routeforge check lab04` passes when your implementation is complete for this stage.
- `stp_root_election` should print `[PASS]` (lowest bridge ID is selected as deterministic root).
- `stp_port_roles` should print `[PASS]` (root/designated/alternate roles are assigned deterministically).
- Run output includes checkpoints: STP_ROOT_CHANGE, STP_PORT_ROLE_CHANGE.

## Debug trace checkpoints and interpretation guidance

Generate trace artifacts when a step fails:

```bash
routeforge run lab04_stp --state-file "$STATE" --trace-out /tmp/lab04_stp.jsonl
routeforge debug replay --trace /tmp/lab04_stp.jsonl
routeforge debug explain --trace /tmp/lab04_stp.jsonl --step stp_root_election
```

Checkpoint guide:

- `STP_ROOT_CHANGE`: A new root bridge has been elected and recorded.  Fired after Step 1
  completes.  If missing, your root election logic didn't produce a result or the result
  wasn't passed back to the caller.
- `STP_PORT_ROLE_CHANGE`: Port roles have changed from the previous STP state — at least
  one port transitioned to ROOT, DESIGNATED, or ALTERNATE.  If missing, your `compute_stp`
  returned roles identical to the initial state (all DOWN), or the caller didn't detect
  the change via `role_changes()`.

## Failure drills and troubleshooting flow

- Intentionally break one listed symbol in `src/routeforge/runtime/stp.py` and rerun `routeforge check lab04` to confirm tests catch regressions.
- If `routeforge run lab04_stp --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- IEEE 802.1D (bridging and STP fundamentals).
- IEEE 802.1Q (VLAN tagging and trunk behavior).

