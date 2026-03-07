# Lab 20: QoS Marking and Queueing

## Learning objectives

- Implement `QosEngine.dequeue` in `src/routeforge/runtime/qos.py`.
- Deliver `qos_remark`: traffic class is remarked to deterministic DSCP.
- Deliver `qos_enqueue`: remarked packet is admitted to expected queue.
- Deliver `qos_dequeue`: scheduler dequeues packet in deterministic order.
- Validate internal behavior through checkpoints: QOS_REMARK, QOS_ENQUEUE, QOS_DEQUEUE.

## Prerequisite recap

- Required prior labs: lab19_nat44_stateful_translation.
- Confirm target mapping before coding with `routeforge show lab20_qos_marking_and_queueing`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

Marking, queue admission, and deterministic dequeue behavior. Student-mode coding target for this stage is `src/routeforge/runtime/qos.py` (`QosEngine.dequeue`).

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/qos.py`
- Symbols: `QosEngine.dequeue`
- Why this target: Dequeue packets using deterministic scheduler order.
- Stage check: `routeforge check lab20`

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab20_qos_marking_and_queueing`
3. Edit only the listed symbols in `src/routeforge/runtime/qos.py`.
4. Run `routeforge check lab20` until it exits with status `0`.
5. Run `routeforge run lab20_qos_marking_and_queueing --state-file "$STATE"` to confirm visible lab behavior and progress state updates.

## Verification commands and expected outputs

```bash
routeforge show lab20_qos_marking_and_queueing
routeforge check lab20

STATE=/tmp/routeforge-progress.json
routeforge run lab20_qos_marking_and_queueing --state-file "$STATE"
```

Expected outcomes:

- `routeforge show` prints `student.stage`, `student.target`, and `student.symbols` matching this chapter.
- `routeforge check lab20` passes when your implementation is complete for this stage.
- `qos_remark` should print `[PASS]` (traffic class is remarked to deterministic DSCP).
- `qos_enqueue` should print `[PASS]` (remarked packet is admitted to expected queue).
- `qos_dequeue` should print `[PASS]` (scheduler dequeues packet in deterministic order).
- Run output includes checkpoints: QOS_REMARK, QOS_ENQUEUE, QOS_DEQUEUE.

## Debug trace checkpoints and interpretation guidance

Generate trace artifacts when a step fails:

```bash
routeforge run lab20_qos_marking_and_queueing --state-file "$STATE" --trace-out /tmp/lab20_qos_marking_and_queueing.jsonl
routeforge debug replay --trace /tmp/lab20_qos_marking_and_queueing.jsonl
routeforge debug explain --trace /tmp/lab20_qos_marking_and_queueing.jsonl --step qos_remark
```

Checkpoint guide:

- `QOS_REMARK`: Marking, queue admission, and deterministic dequeue behavior.
- `QOS_ENQUEUE`: Marking, queue admission, and deterministic dequeue behavior.
- `QOS_DEQUEUE`: Marking, queue admission, and deterministic dequeue behavior.

## Failure drills and troubleshooting flow

- Intentionally break one listed symbol in `src/routeforge/runtime/qos.py` and rerun `routeforge check lab20` to confirm tests catch regressions.
- If `routeforge run lab20_qos_marking_and_queueing --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- RFC 3022 (Traditional NAT).
- RFC 2474 / RFC 2475 (DiffServ marking and QoS service model).
- RFC 4301 (IPsec architecture).

