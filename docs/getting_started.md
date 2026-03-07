# RouteForge Getting Started

This guide is the practical entry point for students.

If you only read one file before coding, read this one.

## What RouteForge Is

RouteForge is a deterministic networking lab workbook.

You learn by implementing specific functions in real source files, then proving behavior with staged tests.

Core components:

- 39 ordered labs (`lab01` to `lab39`)
- deterministic checkpoints for debug visibility
- prerequisite gating between labs
- progress/readiness reporting

## The Two Branches (Important)

- `main`: solved reference implementation
- `student`: same project, but with TODO stubs for student coding

If you are trying to learn by coding, use `student`.

If you stay on `main`, most tests already pass and you will not get meaningful practice.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

## 15-Minute Student Quickstart

```bash
git switch student
routeforge labs
routeforge show lab01_frame_and_headers
routeforge check lab01
```

What this means:

1. `git switch student` puts you on the coding branch.
2. `routeforge show ...` tells you exactly what file/functions to implement.
3. `routeforge check lab01` runs staged tests up to Lab 1.

When `routeforge check lab01` is green, move to:

```bash
routeforge check lab02
```

At the end of the track:

```bash
routeforge check all
```

## How To Complete A Lab

Definition of done for one lab:

1. You implemented the listed target symbols for that lab.
2. `routeforge check labNN` exits with status `0`.
3. `routeforge run <lab_id>` shows all `[PASS]` steps.
4. Expected checkpoints are present in output.

Use this exact loop:

```bash
# 1) discover target
routeforge show <lab_id>

# 2) edit target file/symbols on student branch

# 3) verify stage
routeforge check labNN

# 4) verify runtime behavior
STATE=/tmp/routeforge-progress.json
routeforge run <lab_id> --state-file "$STATE"
```

## `check` vs `run` vs `show`

- `routeforge show <lab_id>`
  - metadata + prerequisites + conformance + student coding target
- `routeforge check <labNN|lab_id|all>`
  - staged pytest gates for student progression
- `routeforge run <lab_id>`
  - executes scenario and prints step/checkpoint outcomes

Use `check` for pass/fail progression; use `run` for behavior visibility.

## Checkpoints vs Steps

- Step
  - human-readable assertion
  - displayed as `[PASS]` or `[FAIL]`
- Checkpoint
  - machine-readable internal event marker
  - used for conformance and trace debugging

Example:

```text
[PASS] known_unicast_forward: MAC learning enables deterministic unicast forwarding
checkpoints: PARSE_OK, VLAN_CLASSIFY, MAC_LEARN, L2_UNICAST_FORWARD
```

Interpretation:

- step passed = expected behavior happened
- checkpoints show where in the internal pipeline behavior occurred

## Prerequisites and "blocked" Runs

If you see:

```text
blocked: <lab_id> has unmet prerequisites: ...
```

then you are trying to run out of order.

Fix by completing earlier labs first or by using a state file generated from sequential runs.

## Recommended State-File Workflow

```bash
STATE=/tmp/routeforge-progress.json
routeforge progress reset --state-file "$STATE"

routeforge run lab01_frame_and_headers --state-file "$STATE"
routeforge progress show --state-file "$STATE"

routeforge run lab02_mac_learning_switch --state-file "$STATE"
routeforge progress show --state-file "$STATE"
```

Repeat in order through the curriculum.

## Debug Workflow When Something Fails

```bash
routeforge run <lab_id> --state-file "$STATE" --trace-out /tmp/lab-trace.jsonl
routeforge debug replay --trace /tmp/lab-trace.jsonl
routeforge debug explain --trace /tmp/lab-trace.jsonl --step <step_name>
```

Use this order:

1. replay full trace timeline
2. explain one failing step
3. compare with tutorial chapter expected checkpoints

## Where To Find Targets and Walkthroughs

- Lab-by-lab coding targets: [student_task_map.md](student_task_map.md)
- Function signatures + required checkpoints: [function_contracts.md](function_contracts.md)
- Full chapter walkthroughs: [tutorial](tutorial)
- Start here: [Lab 01](tutorial/lab01_frame_and_headers.md)

## Core Commands Reference

- `routeforge labs`
- `routeforge show <lab_id>`
- `routeforge check <labNN|lab_id|all>`
- `routeforge run <lab_id> [--state-file ...] [--trace-out ...]`
- `routeforge progress show|mark|reset --state-file <file>`
- `routeforge report --state-file <file>`
- `routeforge debug replay --trace <file>`
- `routeforge debug explain --trace <file> --step <step_name>`

## Common Mistakes

- Coding on `main` instead of `student`
- Running `routeforge run` and expecting it to replace staged checks
- Ignoring `routeforge show <lab_id>` and editing unrelated files
- Treating checkpoints as optional; they are part of conformance

## Next Step

Open [Lab 01](tutorial/lab01_frame_and_headers.md), implement its target symbols, and make `routeforge check lab01` pass.
