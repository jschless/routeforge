# Lab 33: FHRP Tracking and Failover

## Learning objectives

- Implement `tracked_object_result, fhrp_track_failover` in `src/routeforge/runtime/routing_policy.py`.
- Deliver `fhrp_active_initial`: primary router is initially active.
- Deliver `fhrp_track_failover`: tracked failure triggers failover.
- Deliver `fhrp_preempt_recover`: primary preempts after recovery.
- Validate internal behavior through checkpoints: FHRP_ACTIVE_CHANGE, TRACK_DOWN, FHRP_PREEMPT.

## Prerequisite recap

- Required prior labs: `lab32_route_redistribution_and_loop_prevention`.
- Confirm target mapping before coding with `routeforge show lab33_fhrp_tracking_and_failover`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

First-Hop Redundancy Protocols (FHRP) — including HSRP and VRRP — solve a basic availability problem: end hosts configure a single default gateway IP address, so if the router serving that IP fails, hosts lose their path to the rest of the network. FHRP assigns a shared virtual IP to a group of routers and elects one of them as the active gateway at any given moment.

```
  Hosts           Virtual IP: 192.168.1.1
  ------          -----------------------
  Host A ---+     ACTIVE: RouterA (priority 110)
            |---> RouterA ----+
  Host B ---+                 |--> uplink / internet
                 RouterB ----+
  (standby, priority 100)
```

Under normal conditions all host traffic flows through RouterA (the active router). If RouterA's uplink to the internet goes down, hosts would lose connectivity even though RouterA itself is still reachable — it just can't forward traffic anywhere useful.

Object tracking solves this by monitoring a specific condition (an uplink interface, a reachability probe, or any other metric) and coupling the FHRP priority to that condition. When the tracked object goes down:

1. The active router lowers its FHRP priority below the standby router's priority.
2. The standby router detects the priority change via FHRP hello messages.
3. The standby router preempts and becomes the new active gateway.
4. Hosts experience at most a brief interruption, then traffic flows through RouterB.

```
  Normal                          After uplink failure
  ------                          --------------------
  RouterA (ACTIVE, track=UP)      RouterA (STANDBY, track=DOWN)
  RouterB (STANDBY)               RouterB (ACTIVE, preempted)
```

In this lab the failover decision is intentionally simple: `fhrp_track_failover` takes the names of the active and standby routers plus the tracked object state and returns the name of whichever router should be active now. When the tracked object is up, the active router keeps its role. When it goes down, the standby router takes over. This captures the core decision without the timer complexity of real FHRP.

The helper `tracked_object_result` converts a boolean liveness flag into the explicit string `"UP"` or `"DOWN"`, making the calling code self-documenting.

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/routing_policy.py`
- Symbols: `tracked_object_result, fhrp_track_failover`
- Why this target: derive explicit track state first, then select deterministic active/standby role.
- Stage check: `routeforge check lab33`

Function contract for this stage:

- Symbol: `tracked_object_result(*, tracked_object_up: bool) -> Literal["UP", "DOWN"]`
- Required behavior: convert tracked-object boolean into explicit UP/DOWN state
- Symbol: `fhrp_track_failover(*, active_router: str, standby_router: str, tracked_object_up: bool) -> str`
- Required behavior: keep active on UP, fail over to standby on DOWN

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab33_fhrp_tracking_and_failover`
3. Edit only `tracked_object_result, fhrp_track_failover` in `src/routeforge/runtime/routing_policy.py`.
4. Run `routeforge check lab33` until it exits with status `0`.
5. Run `routeforge run lab33_fhrp_tracking_and_failover --state-file "$STATE"` to confirm visible lab behavior and progress state updates.

## Verification commands and expected outputs

```bash
routeforge show lab33_fhrp_tracking_and_failover
routeforge check lab33

STATE=/tmp/routeforge-progress.json
routeforge run lab33_fhrp_tracking_and_failover --state-file "$STATE"
```

Expected outcomes:

- `routeforge show` prints `student.stage`, `student.target`, and `student.symbols` matching this chapter.
- `routeforge check lab33` passes when your implementation is complete for this stage.
- `fhrp_active_initial` should print `[PASS]` (primary router is initially active).
- `fhrp_track_failover` should print `[PASS]` (tracked failure triggers failover).
- `fhrp_preempt_recover` should print `[PASS]` (primary preempts after recovery).
- Run output includes checkpoints: FHRP_ACTIVE_CHANGE, TRACK_DOWN, FHRP_PREEMPT.

## Debug trace checkpoints and interpretation guidance

Generate trace artifacts when a step fails:

```bash
routeforge run lab33_fhrp_tracking_and_failover --state-file "$STATE" --trace-out /tmp/lab33_fhrp_tracking_and_failover.jsonl
routeforge debug replay --trace /tmp/lab33_fhrp_tracking_and_failover.jsonl
routeforge debug explain --trace /tmp/lab33_fhrp_tracking_and_failover.jsonl --step fhrp_active_initial
```

Checkpoint guide:

- `FHRP_ACTIVE_CHANGE`: fires when the active gateway decision is evaluated and the selected active router is returned. If this checkpoint is missing, the failover selection logic is not reaching the active/standby decision point.
- `TRACK_DOWN`: fires when the tracked object reports a down state. If this checkpoint is missing when `tracked_object_up=False`, verify that your helper returns `"DOWN"` and that the failover path consumes that result.
- `FHRP_PREEMPT`: fires when the standby router takes over because the tracked object is down. If this checkpoint is missing, verify that the branch for `tracked_object_up=False` returns `standby_router` rather than `active_router`.

## Failure drills and troubleshooting flow

- Intentionally break `tracked_object_result` or `fhrp_track_failover` in `src/routeforge/runtime/routing_policy.py` and rerun `routeforge check lab33` to confirm tests catch regressions.
- If `routeforge run lab33_fhrp_tracking_and_failover --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- FHRP tracking and preemption semantics.
