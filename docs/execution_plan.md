# RouteForge Execution Plan

Status: Active draft  
Date: 2026-03-07

## 1) Planning Baseline

This execution plan implements the following source docs:

- `docs/routeforge_redesign.md`
- `docs/bridge_contract.md`
- `labs/conformance_matrix.yaml`

## 2) Build Strategy

Use a staged, test-first rollout:

1. Platform contracts first (bridge, scheduler ordering, trace schema)
2. Lab orchestration second (manifest, prerequisite gate, conformance loading)
3. Protocol/lab implementation third (in sequence)
4. Documentation and CI checks in parallel, not at the end

## 3) Workstreams

### WS1: Dual-Sim Runtime

Scope:

- Shared deterministic scheduler
- `dataplane_sim` and `controlplane_sim` abstractions
- Typed bridge message envelope and validation

Done when:

- Message direction/type validation exists
- Bridge idempotency enforced by `message_id`
- Deterministic ordering test passes repeatedly

### WS2: Lab Orchestration

Scope:

- Ordered lab manifest
- Prerequisite gate in CLI (`routeforge run <lab>`)
- Conformance matrix loader and lookup helpers

Done when:

- Out-of-order labs are blocked with clear errors
- Lab metadata and conformance mapping are queryable by CLI

### WS3: Debug and Trace Contract

Scope:

- Unified event schema with `sim_domain` and `correlation_id`
- Bridge emit/apply checkpoint pairs
- Trace contract tests

Done when:

- Trace events from both sims are queryable in one timeline
- Contract tests detect missing required checkpoints

### WS4: Docs + Test Harness

Scope:

- Tutorial chapter template checks
- Conformance test harness skeleton by feature ID
- Docs link validation

Done when:

- CI fails on broken doc links/template gaps
- Conformance harness can assert `MUST (v1)` status per feature

## 4) Phase 0 (Immediate Build Slice)

Goal: Convert current scaffold into a minimal executable architecture contract.

### Task list

1. Implement bridge message type registry and payload validators.
2. Implement deterministic scheduler queue and ordering utility tests.
3. Add CLI `run` command with prerequisite gating.
4. Add conformance matrix parser and `routeforge show <lab>` conformance output.
5. Add trace event dataclass and bridge emit/apply trace helpers.
6. Add contract tests for bridge validation, gating, and matrix loading.

### Exit criteria

1. `pytest -q` passes contract tests.
2. `routeforge labs` and `routeforge show <lab>` are functional.
3. `routeforge run <lab>` blocks unmet prerequisites.
4. Bridge messages validate and produce deterministic ordering.

## 5) Phase 1 (First Functional Labs)

Goal: Deliver `lab01`-`lab03` with executable student loop.

### Task list

1. Implement basic packet/frame model + validation.
2. Implement MAC learning switch behavior.
3. Implement VLAN/trunk behavior.
4. Add lab tests + edge tests for labs 01-03.
5. Publish tutorial chapters for labs 01-03.

### Exit criteria

1. Labs 01-03 pass exercise and edge tests.
2. Required checkpoints exist in trace outputs.
3. Tutorial chapters meet template checks.

## 6) CI Gates (from start)

Run in CI on every push:

1. `pytest -q` (contract + lab + conformance)
2. docs link and template checks
3. deterministic replay check (same seed/input -> same normalized trace)

## 7) Risks and Controls

1. Risk: bridge complexity drifts early.
   - Control: keep strict message schema + idempotency tests.
2. Risk: docs lag implementation.
   - Control: chapter template checks in CI.
3. Risk: lab scope creep.
   - Control: enforce `MUST/SHOULD/OUT` matrix at PR review.

## 8) Next Command Sequence

```bash
cd /Users/joeschlessinger/Programming/routeforge
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
PYTHONPATH=src pytest -q
PYTHONPATH=src python -m routeforge labs
```
