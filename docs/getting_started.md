# RouteForge Getting Started

This guide explains what RouteForge is, what it is trying to teach, and how to use it end-to-end as a learner.

## What RouteForge Is

RouteForge is a deterministic networking workbook designed to build CCNP-level routing and switching intuition.

It combines:

- lab exercises (`lab01` through `lab27`)
- checkpoint traces for explainability
- prerequisite gating so foundational concepts are learned in order
- progress and readiness reporting for structured study

## Learning Goals

By the end of the full track, a student should be able to:

- explain L2/L3 forwarding decisions and failure behavior
- reason through OSPF and BGP control-plane state changes
- troubleshoot ACL/NAT/QoS and service interactions
- validate incident recovery in a multi-protocol capstone

## How The Product Works

RouteForge uses two simulation layers:

- `dataplane_sim`: packet handling and forwarding outcomes
- `controlplane_sim`: protocol FSM and route-state behavior

All labs emit deterministic checkpoints so runs are reproducible and debuggable.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

## First 10 Minutes

1. List labs:

```bash
routeforge labs
```

2. Run the first lab:

```bash
routeforge run lab01_frame_and_headers
```

3. Save progress state:

```bash
routeforge run lab01_frame_and_headers --state-file /tmp/routeforge-progress.json
routeforge progress show --state-file /tmp/routeforge-progress.json
```

4. Run the next unlocked lab using the same state file:

```bash
routeforge run lab02_mac_learning_switch --state-file /tmp/routeforge-progress.json
```

## What "Complete A Lab" Means

A lab is complete when all of the following are true:

1. `routeforge run <lab_id>` exits with code `0`.
2. Every printed step line is `[PASS]`.
3. The run prints checkpoints for that lab.
4. If you used `--state-file`, that lab appears in `labs.completed.list`.

If any step shows `[FAIL]`, the lab is not complete yet.

## Branch-Based Student Workflow

RouteForge is intended to be used with two branches:

- `main`: reference implementation (all solutions)
- `student`: same codebase, but selected lab files contain TODO blanks

Student loop:

1. `git switch student`
2. edit the real source file for the current lab (for Lab 1: `src/routeforge/model/packet.py`)
3. run staged tests:

```bash
routeforge check lab01
```

4. when green, move to the next stage:

```bash
routeforge check lab02
```

By the end of the course:

```bash
routeforge check all
```

should pass.

## How To Read Lab Output

Example:

```text
running lab: lab02_mac_learning_switch
[PASS] unknown_unicast_flood: unknown unicast floods to all non-ingress ports
[PASS] known_unicast_forward: MAC learning enables deterministic unicast forwarding
checkpoints: PARSE_OK, VLAN_CLASSIFY, MAC_LEARN, L2_FLOOD, L2_UNICAST_FORWARD
progress updated: /tmp/routeforge-progress.json
```

Interpretation:

- `running lab`: the selected scenario started.
- each `[PASS]/[FAIL]` line is a step-level assertion.
- `checkpoints`: named events hit during the run.
- `progress updated`: completion state was written to your state file.

## What Is A Step vs A Checkpoint?

- Step:
  - human-readable test/assertion for one behavior in the lab
  - shown as `[PASS]` or `[FAIL]`
  - examples: `qos_remark`, `bgp_best_path_select`

- Checkpoint:
  - machine-readable event marker in the simulation timeline
  - used for conformance and debugging
  - examples: `PARSE_DROP`, `BGP_BEST_PATH`, `QOS_DEQUEUE`

Think of steps as "did this requirement pass?" and checkpoints as "what internal events happened?"

## What To Do If You See "blocked"

If output says:

```text
blocked: <lab_id> has unmet prerequisites: ...
```

that lab is locked until prerequisite labs are complete. Run the missing labs first.

Tip: `routeforge progress show --state-file <file>` always shows what is unlocked next.

## Completion Checklist (Copy/Paste Workflow)

```bash
STATE=/tmp/routeforge-progress.json
routeforge progress reset --state-file "$STATE"

routeforge run lab01_frame_and_headers --state-file "$STATE"
routeforge progress show --state-file "$STATE"

routeforge run lab02_mac_learning_switch --state-file "$STATE"
routeforge progress show --state-file "$STATE"

routeforge run lab03_vlan_and_trunks --state-file "$STATE"
routeforge progress show --state-file "$STATE"
```

Repeat this pattern for each newly unlocked lab.

## If A Lab Fails

1. Re-run with trace output:

```bash
routeforge run <lab_id> --state-file "$STATE" --trace-out /tmp/lab-trace.jsonl
```

2. Replay full timeline:

```bash
routeforge debug replay --trace /tmp/lab-trace.jsonl
```

3. Explain one failing step:

```bash
routeforge debug explain --trace /tmp/lab-trace.jsonl --step <step_name>
```

4. Open the matching tutorial chapter and compare expected checkpoints.

## Core Commands

- `routeforge labs`: ordered curriculum list
- `routeforge show <lab_id>`: lab metadata + conformance mapping
- `routeforge run <lab_id>`: execute lab with prerequisite checks
- `routeforge check <labNN|lab_id|all>`: run staged student tests up to a milestone
- `routeforge run <lab_id> --trace-out <file>`: write JSONL trace records
- `routeforge debug replay --trace <file>`: replay timeline
- `routeforge debug explain --trace <file> --step <step_name>`: inspect one step
- `routeforge progress show|mark|reset --state-file <file>`: manage learner state
- `routeforge report --state-file <file>`: readiness + assessment output

## Recommended Study Workflow

1. Run one lab at a time in order.
2. If a step fails, use trace replay and explain before moving on.
3. Keep a persistent state file and check unlocked labs after each run.
4. Use `routeforge report` weekly to track coverage and at-risk labs.
5. Revisit tutorial chapters for at-risk labs before retrying.

## Textbook Navigation

- Home: [index.md](index.md)
- Curriculum chapters: [tutorial](tutorial)
- Architecture background: [routeforge_redesign.md](routeforge_redesign.md)

## Conformance and Assessment

RouteForge ships with:

- conformance matrix: [`labs/conformance_matrix.yaml`](../labs/conformance_matrix.yaml)
- assessment rubric: [`labs/assessment_rubric.yaml`](../labs/assessment_rubric.yaml)

These are used by `routeforge report` to produce objective progress and readiness output.

## Next Steps

- Start with [Lab 01](tutorial/lab01_frame_and_headers.md).
- Follow the ordered path through [Lab 27](tutorial/lab27_capstone_incident_drill.md).
