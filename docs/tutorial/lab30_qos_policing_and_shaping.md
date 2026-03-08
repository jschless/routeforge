# Lab 30: QoS Policing and Shaping

## Learning objectives

- Implement `apply_policer, qos_police_shape` in `src/routeforge/runtime/qos_advanced.py`.
- Deliver `qos_police_rate`: traffic above CIR is policed.
- Deliver `qos_shape_queue`: excess traffic is queued by shaper.
- Deliver `qos_shape_release`: queued traffic is released at shape rate.
- Validate internal behavior through checkpoints: QOS_POLICE, QOS_SHAPE_QUEUE, QOS_SHAPE_RELEASE.

## Prerequisite recap

- Required prior labs: `lab29_port_security_and_ip_source_guard`.
- Confirm target mapping before coding with `routeforge show lab30_qos_policing_and_shaping`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

### The problem: protecting network resources from traffic bursts

Without rate controls, a single flow can consume all available bandwidth on a link, starving other flows. QoS provides two complementary mechanisms to enforce rate limits: policing and shaping. They operate differently and serve different purposes; this lab implements both in a single two-stage pipeline.

### Policing: drop excess traffic immediately

A policer measures the rate of incoming traffic and compares it against a configured Committed Information Rate (CIR). Traffic arriving within the CIR is admitted. Traffic arriving above the CIR is excess and is dropped immediately — it is not buffered or delayed, it is simply discarded.

**CIR (Committed Information Rate)**: The maximum rate at which traffic is guaranteed to be admitted. Think of it as the contracted bandwidth limit. Traffic up to this rate is always let through; anything above is excess.

Policing is typically applied at ingress — for example, at the customer edge of a service provider network to enforce the contracted rate. The effect is visible as packet loss when the sender exceeds the CIR.

### Shaping: buffer and pace excess traffic

A shaper also limits traffic to a configured rate, but instead of dropping excess it holds it in a queue and releases it at a controlled rate. Shaping smooths out bursts: a sender that transmits in large bursts will see those bursts absorbed into the queue and metered out evenly.

**Shape rate**: The maximum rate at which the shaper releases frames from its queue. If the admitted rate (after policing) exceeds the shape rate, the surplus waits in the queue rather than being forwarded immediately.

Shaping is typically applied at egress — for example, to pace traffic going out to a slower downstream link.

### The two-stage pipeline

```
                  offered_kbps
                       │
                       ▼
              ┌─────────────────┐
              │   POLICER        │  cap at CIR, drop excess
              │   admitted =     │
              │   min(offered,   │
              │       cir)       │
              └────────┬────────┘
                       │ admitted_kbps
                       ▼
              ┌─────────────────┐
              │   SHAPER         │  cap at shape_rate, queue remainder
              │   released =     │
              │   min(admitted,  │
              │       shape_rate)│
              └────────┬────────┘
                       │ released_kbps
                       ▼
                  (forwarded)
```

`apply_policer` implements the first stage alone: it returns `min(offered_kbps, cir_kbps)`, floored at zero. `qos_police_shape` composes both stages and returns `(admitted_kbps, released_kbps)`.

### Example

CIR = 100 kbps, shape rate = 80 kbps, offered = 150 kbps:
- Policer admits `min(150, 100) = 100` kbps; 50 kbps is dropped.
- Shaper releases `min(100, 80) = 80` kbps; 20 kbps waits in the queue.

If the offered rate drops to 60 kbps in the next interval:
- Policer admits `min(60, 100) = 60` kbps (below CIR, no drop).
- Shaper releases `min(60, 80) = 60` kbps (below shape rate, no queuing delay).

Note that `QOS_POLICE_EXCESS` fires whenever `offered_kbps > cir_kbps`, even if the excess is small. `QOS_SHAPE_RELEASE` fires whenever the shaper is the binding constraint, i.e., when `admitted_kbps > shape_rate_kbps`.

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/qos_advanced.py`
- Symbols: `apply_policer, qos_police_shape`
- Why this target: implement CIR policing logic and deterministic shaping release behavior.
- Stage check: `routeforge check lab30`

Function contract for this stage:

- Symbol: `apply_policer(*, offered_kbps: int, cir_kbps: int) -> int`
- Required behavior: return admitted rate at or below CIR with zero-floor normalization
- Symbol: `qos_police_shape(*, offered_kbps: int, cir_kbps: int, shape_rate_kbps: int) -> tuple[int, int]`
- Required behavior: return `(admitted, released)` where released is shape-limited from admitted

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab30_qos_policing_and_shaping`
3. Edit only `apply_policer, qos_police_shape` in `src/routeforge/runtime/qos_advanced.py`.
4. Run `routeforge check lab30` until it exits with status `0`.
5. Run `routeforge run lab30_qos_policing_and_shaping --state-file "$STATE"` to confirm visible lab behavior and progress state updates.

## Verification commands and expected outputs

```bash
routeforge show lab30_qos_policing_and_shaping
routeforge check lab30

STATE=/tmp/routeforge-progress.json
routeforge run lab30_qos_policing_and_shaping --state-file "$STATE"
```

Expected outcomes:

- `routeforge show` prints `student.stage`, `student.target`, and `student.symbols` matching this chapter.
- `routeforge check lab30` passes when your implementation is complete for this stage.
- `qos_police_rate` should print `[PASS]` (traffic above CIR is policed).
- `qos_shape_queue` should print `[PASS]` (excess traffic is queued by shaper).
- `qos_shape_release` should print `[PASS]` (queued traffic is released at shape rate).
- Run output includes checkpoints: QOS_POLICE, QOS_SHAPE_QUEUE, QOS_SHAPE_RELEASE.

## Debug trace checkpoints and interpretation guidance

Generate trace artifacts when a step fails:

```bash
routeforge run lab30_qos_policing_and_shaping --state-file "$STATE" --trace-out /tmp/lab30_qos_policing_and_shaping.jsonl
routeforge debug replay --trace /tmp/lab30_qos_policing_and_shaping.jsonl
routeforge debug explain --trace /tmp/lab30_qos_policing_and_shaping.jsonl --step qos_police_rate
```

Checkpoint guide:

- `QOS_POLICE`: Traffic was admitted at or below the CIR, with any excess dropped. The returned `admitted_kbps` value should equal `min(offered_kbps, cir_kbps)`. If this checkpoint is missing during the `qos_police_rate` step, your policer is not capping at the CIR correctly.
- `QOS_SHAPE_QUEUE`: The shaper detected that admitted traffic exceeded the shape rate and queued the excess rather than forwarding it immediately. If this checkpoint is missing during `qos_shape_queue`, verify that the shaping stage recognizes `admitted_kbps > shape_rate_kbps`.
- `QOS_SHAPE_RELEASE`: The shaper was the binding constraint: `admitted_kbps > shape_rate_kbps`, so `released_kbps = shape_rate_kbps < admitted_kbps`. The difference between admitted and released is held in the shaping queue. If this checkpoint is missing during `qos_shape_release`, your shaper is not applying the `min(admitted, shape_rate)` constraint — verify that the second stage of `qos_police_shape` uses `shape_rate_kbps` as an upper bound on the returned `released` value.

## Failure drills and troubleshooting flow

- Intentionally break `apply_policer` or `qos_police_shape` in `src/routeforge/runtime/qos_advanced.py` and rerun `routeforge check lab30` to confirm tests catch regressions.
- If `routeforge run lab30_qos_policing_and_shaping --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- Traffic policing and shaping principles.
