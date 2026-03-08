# RouteForge Bridge Contract (v1)

> **Advanced/optional:** this document describes the target Phase 3
> multi-simulator architecture. Labs 01-39 call protocol functions directly.
> Skip this unless you want the long-term design context.

Status: Draft  
Date: 2026-03-07

## 1) Purpose

Define the typed interface between `controlplane_sim` and `dataplane_sim` so both simulations can evolve independently while remaining deterministic and testable.

## 2) Design Rules

1. Simulators never mutate each other's internal state directly.
2. All cross-sim actions must be expressed as typed bridge messages.
3. Messages are processed in shared scheduler order: `(sim_time_ms, priority, sequence)`.
4. Every message must emit both `bridge_emit` and `bridge_apply` trace checkpoints with the same `correlation_id`.

## 3) Envelope Schema

All bridge messages use a common envelope:

```json
{
  "schema_version": 1,
  "message_id": "uuid-or-stable-id",
  "message_type": "ROUTE_INSTALL",
  "source_sim": "CONTROLPLANE",
  "target_sim": "DATAPLANE",
  "sim_time_ms": 12345,
  "priority": 100,
  "node_id": "R1",
  "correlation_id": "c-001",
  "payload": {}
}
```

Required fields:

- `schema_version` (int)
- `message_id` (str, unique per run)
- `message_type` (enum)
- `source_sim` (`DATAPLANE` or `CONTROLPLANE`)
- `target_sim` (`DATAPLANE` or `CONTROLPLANE`)
- `sim_time_ms` (int)
- `priority` (int)
- `node_id` (str)
- `correlation_id` (str)
- `payload` (object)

## 4) Message Types

### 4.1 Control plane -> Data plane

1. `ROUTE_INSTALL`
   - Payload: `prefix`, `prefix_len`, `protocol`, `next_hop`, `out_if`, `admin_distance`, `metric`.
2. `ROUTE_WITHDRAW`
   - Payload: `prefix`, `prefix_len`, `protocol`, `reason`.
3. `NEXTHOP_REWRITE_UPDATE`
   - Payload: `next_hop`, `resolved_mac`, `out_if`, `state`.
4. `POLICY_PROGRAM_UPDATE`
   - Payload: `policy_type` (`ACL|QOS|NAT`), `program_id`, `operation` (`replace|append|remove`), `entries`.

### 4.2 Data plane -> Control plane

1. `INTERFACE_STATE_CHANGE`
   - Payload: `if_name`, `state` (`up|down`), `reason`.
2. `ADJACENCY_SIGNAL`
   - Payload: `protocol` (`OSPF|BGP|BFD|STP`), `peer_id`, `if_name`, `state`.
3. `FORWARDING_FAILURE_SIGNAL`
   - Payload: `flow_key`, `reason_code`, `drop_count_delta`, `egress_if`.
4. `TRAFFIC_OBSERVATION_SIGNAL`
   - Payload: `flow_key`, `pps`, `bps`, `dscp_histogram`, `sample_window_ms`.

### 4.3 Scenario -> Both

1. `FAIL_LINK`
2. `RECOVER_LINK`
3. `FAIL_PEER`
4. `RECOVER_PEER`

Each carries scenario context:

- `scenario_id`, `step_id`, `target`, `expected_effect`.

## 5) Validation Rules

1. `source_sim` and `target_sim` must be opposite domains.
2. `message_type` must match the allowed direction.
3. Payload keys are strict; unknown keys fail validation.
4. Required payload keys must be present and correctly typed.
5. Bridge apply must be idempotent by `message_id`.

## 6) Failure Semantics

On apply failure, the target simulator emits:

1. `BRIDGE_APPLY_FAILED` with normalized reason.
2. Optional compensating signal back to source simulator.
3. Test-visible failure record including `message_id` and validation error details.

## 7) Versioning and Compatibility

1. Envelope and payload schema are versioned by `schema_version`.
2. Backward-incompatible changes require a new major schema version.
3. Minor changes can add optional payload fields only.

## 8) Required Contract Tests

1. Directionality test: disallow wrong source/target domain.
2. Schema test: validate required keys and types.
3. Idempotency test: duplicate `message_id` does not double-apply.
4. Determinism test: same inputs produce same bridge apply sequence.
5. Trace test: every applied message has paired `emit/apply` checkpoints.
