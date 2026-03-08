# Lab 32: Route Redistribution and Loop Prevention

## Learning objectives

- Implement `build_redistribution_tag, redistribute_with_loop_guard` in `src/routeforge/runtime/routing_policy.py`.
- Deliver `redist_import`: new route is imported into target protocol.
- Deliver `redist_tag_set`: redistributed route is tagged for loop prevention.
- Deliver `redist_loop_suppress`: re-seen tag is suppressed to prevent loops.
- Validate internal behavior through checkpoints: REDIST_IMPORT, TAG_SET, LOOP_SUPPRESS.

## Prerequisite recap

- Required prior labs: `lab31_qos_congestion_avoidance_wred`.
- Confirm target mapping before coding with `routeforge show lab32_route_redistribution_and_loop_prevention`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

Route redistribution lets a router share routes learned by one routing protocol with a different protocol. A router running both OSPF and BGP, for example, can inject OSPF-learned prefixes into BGP so that BGP speakers elsewhere can reach those destinations, and vice versa.

The danger is a feedback loop. Suppose Router A redistributes prefix `10.1.1.0/24` from OSPF into BGP. Router B receives that BGP route and, running its own redistribution policy, injects it back into OSPF. Router A now sees `10.1.1.0/24` arrive via OSPF again and could redistribute it into BGP a second time, creating a duplicate or oscillating entry.

The standard defense is tagging: attach a unique label to a route the moment it is redistributed, and refuse to redistribute any route whose label is already present in the tag set. The label encodes both the originating protocol and the prefix, so it can be checked deterministically at every redistribution boundary.

```
   OSPF domain          BGP domain
   ----------           ----------
   10.1.1.0/24  -->  redistribute  -->  BGP update (tag: OSPF:10.1.1.0/24)
                                              |
              <-- loop blocked (tag seen) <---+
```

In this lab the tag format is `PROTOCOL:prefix` in upper-case. The function `build_redistribution_tag` constructs this canonical string. `redistribute_with_loop_guard` then checks whether the tag already exists in the route's tag set:

- If the tag is absent, the route is new: add the tag and return the action `"IMPORT"`.
- If the tag is already present, the route has been here before: return `"LOOP_SUPPRESS"` without modifying the tag set.

The key insight is that the tag set travels with the route across redistribution boundaries. Each hop adds its own tag, so the set grows as the route propagates. Any router that has already touched the route will see its own tag and suppress re-import.

The helper `tracked_object_result` converts a boolean liveness flag into the explicit string `"UP"` or `"DOWN"`. This pattern appears across several modules to keep conditional logic readable.

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/routing_policy.py`
- Symbols: `build_redistribution_tag, redistribute_with_loop_guard`
- Why this target: build canonical tags and enforce one-time import loop guard behavior.
- Stage check: `routeforge check lab32`

Function contract for this stage:

- Symbol: `build_redistribution_tag(*, source_prefix: str, source_protocol: str) -> str`
- Required behavior: return uppercase canonical tag in `PROTOCOL:prefix` format
- Symbol: `redistribute_with_loop_guard(*, source_prefix: str, source_protocol: str, existing_tags: set[str]) -> tuple[set[str], Literal["IMPORT", "LOOP_SUPPRESS"]]`
- Required behavior: import once per canonical tag; suppress re-import when tag is already present

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab32_route_redistribution_and_loop_prevention`
3. Edit only `build_redistribution_tag, redistribute_with_loop_guard` in `src/routeforge/runtime/routing_policy.py`.
4. Run `routeforge check lab32` until it exits with status `0`.
5. Run `routeforge run lab32_route_redistribution_and_loop_prevention --state-file "$STATE"` to confirm visible lab behavior and progress state updates.

## Verification commands and expected outputs

```bash
routeforge show lab32_route_redistribution_and_loop_prevention
routeforge check lab32

STATE=/tmp/routeforge-progress.json
routeforge run lab32_route_redistribution_and_loop_prevention --state-file "$STATE"
```

Expected outcomes:

- `routeforge show` prints `student.stage`, `student.target`, and `student.symbols` matching this chapter.
- `routeforge check lab32` passes when your implementation is complete for this stage.
- `redist_import` should print `[PASS]` (new route is imported into target protocol).
- `redist_tag_set` should print `[PASS]` (redistributed route is tagged for loop prevention).
- `redist_loop_suppress` should print `[PASS]` (re-seen tag is suppressed to prevent loops).
- Run output includes checkpoints: REDIST_IMPORT, TAG_SET, LOOP_SUPPRESS.

## Debug trace checkpoints and interpretation guidance

Generate trace artifacts when a step fails:

```bash
routeforge run lab32_route_redistribution_and_loop_prevention --state-file "$STATE" --trace-out /tmp/lab32_route_redistribution_and_loop_prevention.jsonl
routeforge debug replay --trace /tmp/lab32_route_redistribution_and_loop_prevention.jsonl
routeforge debug explain --trace /tmp/lab32_route_redistribution_and_loop_prevention.jsonl --step redist_import
```

Checkpoint guide:

- `REDIST_IMPORT`: fires when a route is successfully imported across protocol boundaries. The tag for this route was absent from `existing_tags`, so the function added it to a new copy of the set and returned `"IMPORT"`. If this checkpoint is missing, check that your tag comparison uses the exact string produced by `build_redistribution_tag` (upper-case protocol, colon separator, then the prefix as-is).
- `TAG_SET`: fires when the canonical redistribution tag is added to the route's tag set on a successful import. If this checkpoint is missing, your successful import path is not persisting the new tag.
- `LOOP_SUPPRESS`: fires when a route is detected as a redistribution loop and silently dropped. The canonical tag was already present in `existing_tags`, so the function returned `"LOOP_SUPPRESS"` without modifying the set. If this checkpoint is missing when you expect suppression, verify that you are checking tag membership before mutating the set and that you are not returning `"IMPORT"` unconditionally.

## Failure drills and troubleshooting flow

- Intentionally break `build_redistribution_tag` or `redistribute_with_loop_guard` in `src/routeforge/runtime/routing_policy.py` and rerun `routeforge check lab32` to confirm tests catch regressions.
- If `routeforge run lab32_route_redistribution_and_loop_prevention --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- Route redistribution loop prevention patterns.
