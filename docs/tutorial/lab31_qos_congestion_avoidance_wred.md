# Lab 31: QoS Congestion Avoidance (WRED)

## Learning objectives

- Implement `wred_decision_profile, qos_wred_decision` in `src/routeforge/runtime/qos_advanced.py`.
- Deliver `qos_wred_profile`: WRED profile activates above minimum threshold.
- Deliver `qos_ecn_mark`: ECN-capable flow is marked before hard drop.
- Deliver `qos_wred_drop`: queue beyond max threshold is dropped.
- Validate internal behavior through checkpoints: QOS_WRED_PROFILE, QOS_ECN_MARK, QOS_WRED_DROP.

## Prerequisite recap

- Required prior labs: `lab30_qos_policing_and_shaping`.
- Confirm target mapping before coding with `routeforge show lab31_qos_congestion_avoidance_wred`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

### The problem: tail-drop and global synchronization

The naive approach to a full queue is tail-drop: when the queue is full, every new arriving packet is dropped. This causes a phenomenon called TCP global synchronization. Because many TCP flows share the queue and all see packet loss at the same moment, they all simultaneously enter congestion-control slow-start, cutting their windows at the same time. This drains the queue to near-empty, then all flows ramp up together and fill it again, repeating in waves. The result is highly inefficient, oscillating link utilization.

Weighted Random Early Detection (WRED) solves this by proactively signaling congestion to individual flows before the queue is completely full, staggering their slowdowns rather than triggering them all at once.

### Key terms

- **Min threshold**: The queue depth below which WRED takes no action. All traffic is forwarded normally when the queue is this shallow.
- **Max threshold**: The queue depth at or above which WRED drops all arriving traffic unconditionally, regardless of ECN capability.
- **Between thresholds**: The active WRED zone. Traffic here may be dropped or marked depending on ECN capability. In this simplified model all traffic in this zone is acted on (rather than the probabilistic approach used in real hardware).
- **ECN (Explicit Congestion Notification)**: A mechanism that allows a router to signal congestion to a sender without dropping packets. When an ECN-capable endpoint sends a packet with the ECN-capable transport (ECT) bit set, a congested router can set the Congestion Experienced (CE) bit instead of dropping the packet. The receiver notifies the sender, which reduces its transmission rate. ECN avoids the retransmission overhead of packet loss.
- **ECN marking vs. dropping**: In the between-thresholds zone, ECN-capable flows are marked (MARK) rather than dropped; the sender receives a congestion signal without losing the packet. Non-ECN flows cannot be marked, so they are dropped (DROP) to produce the same congestion signal via loss detection.

### Threshold diagram

```
Queue depth
    │
    │  ≥ max_threshold  ──────────  DROP everything (hard limit)
    │
    │  between           ──────────  ECN-capable → MARK
    │  thresholds                    non-ECN     → DROP
    │
    │  < min_threshold  ──────────  FORWARD (no congestion action)
    │
    0
```

### The two-function design

`wred_decision_profile` classifies the current queue depth into one of three regions: `BELOW_MIN`, `BETWEEN_THRESHOLDS`, or `AT_OR_ABOVE_MAX`. This is a pure classification step with no policy logic.

`qos_wred_decision` calls `wred_decision_profile` and maps the result to a final action:

| Profile | ECN capable | Action |
|---|---|---|
| BELOW_MIN | any | FORWARD |
| BETWEEN_THRESHOLDS | True | MARK |
| BETWEEN_THRESHOLDS | False | DROP |
| AT_OR_ABOVE_MAX | any | DROP |

The key subtlety: `AT_OR_ABOVE_MAX` always produces DROP, even for ECN-capable flows. Once the queue is at maximum capacity, the system cannot afford to merely mark — it must drop to free space immediately.

### What correct behavior looks like

Given `min_threshold=20`, `max_threshold=40`:
- `queue_depth=10` → `FORWARD` (below min, no action regardless of ECN)
- `queue_depth=30, ecn_capable=True` → `MARK` (between thresholds, ECN available)
- `queue_depth=30, ecn_capable=False` → `DROP` (between thresholds, no ECN)
- `queue_depth=40, ecn_capable=True` → `DROP` (at max, ECN irrelevant)
- `queue_depth=55, ecn_capable=True` → `DROP` (above max, ECN irrelevant)

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/qos_advanced.py`
- Symbols: `wred_decision_profile, qos_wred_decision`
- Why this target: classify queue-depth thresholds first, then resolve FORWARD/MARK/DROP action.
- Stage check: `routeforge check lab31`

Function contract for this stage:

- Symbol: `wred_decision_profile(*, queue_depth: int, min_threshold: int, max_threshold: int) -> Literal["BELOW_MIN", "BETWEEN_THRESHOLDS", "AT_OR_ABOVE_MAX"]`
- Required behavior: classify queue depth into one deterministic threshold profile
- Symbol: `qos_wred_decision(*, queue_depth: int, min_threshold: int, max_threshold: int, ecn_capable: bool) -> Literal["FORWARD", "MARK", "DROP"]`
- Required behavior: map profile + ECN capability into deterministic congestion action

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab31_qos_congestion_avoidance_wred`
3. Edit only `wred_decision_profile, qos_wred_decision` in `src/routeforge/runtime/qos_advanced.py`.
4. Run `routeforge check lab31` until it exits with status `0`.
5. Run `routeforge run lab31_qos_congestion_avoidance_wred --state-file "$STATE"` to confirm visible lab behavior and progress state updates.

## Verification commands and expected outputs

```bash
routeforge show lab31_qos_congestion_avoidance_wred
routeforge check lab31

STATE=/tmp/routeforge-progress.json
routeforge run lab31_qos_congestion_avoidance_wred --state-file "$STATE"
```

Expected outcomes:

- `routeforge show` prints `student.stage`, `student.target`, and `student.symbols` matching this chapter.
- `routeforge check lab31` passes when your implementation is complete for this stage.
- `qos_wred_profile` should print `[PASS]` (WRED profile activates above minimum threshold).
- `qos_ecn_mark` should print `[PASS]` (ECN-capable flow is marked before hard drop).
- `qos_wred_drop` should print `[PASS]` (queue beyond max threshold is dropped).
- Run output includes checkpoints: QOS_WRED_PROFILE, QOS_ECN_MARK, QOS_WRED_DROP.

## Debug trace checkpoints and interpretation guidance

Generate trace artifacts when a step fails:

```bash
routeforge run lab31_qos_congestion_avoidance_wred --state-file "$STATE" --trace-out /tmp/lab31_qos_congestion_avoidance_wred.jsonl
routeforge debug replay --trace /tmp/lab31_qos_congestion_avoidance_wred.jsonl
routeforge debug explain --trace /tmp/lab31_qos_congestion_avoidance_wred.jsonl --step qos_wred_profile
```

Checkpoint guide:

- `QOS_WRED_PROFILE`: The queue depth was classified into one of the WRED threshold regions before a congestion action was chosen. If this checkpoint is missing, `wred_decision_profile` is not being reached or is not returning a recognized profile.
- `QOS_ECN_MARK`: The queue depth was between `min_threshold` and `max_threshold` (exclusive), and the flow was ECN-capable. The packet's CE bit was set rather than dropping it, signaling congestion without loss. If this checkpoint is missing during `qos_ecn_mark`, check two things: first, that `wred_decision_profile` returns `BETWEEN_THRESHOLDS` for this depth; second, that `qos_wred_decision` returns `"MARK"` when the profile is `BETWEEN_THRESHOLDS` and `ecn_capable=True`.
- `QOS_WRED_DROP`: A packet was dropped because either the queue depth was at or above `max_threshold`, or the queue was in the between-thresholds zone and the flow was not ECN-capable. If this checkpoint is missing during `qos_wred_drop`, verify that your max-threshold boundary uses `>=` and that non-ECN flows in the `BETWEEN_THRESHOLDS` zone return `"DROP"` rather than `"MARK"`.

## Failure drills and troubleshooting flow

- Intentionally break `wred_decision_profile` or `qos_wred_decision` in `src/routeforge/runtime/qos_advanced.py` and rerun `routeforge check lab31` to confirm tests catch regressions.
- If `routeforge run lab31_qos_congestion_avoidance_wred --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- WRED and ECN congestion management.
