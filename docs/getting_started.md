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

## Core Commands

- `routeforge labs`: ordered curriculum list
- `routeforge show <lab_id>`: lab metadata + conformance mapping
- `routeforge run <lab_id>`: execute lab with prerequisite checks
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
