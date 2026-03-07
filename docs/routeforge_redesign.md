# RouteForge Workbook Redesign

Status: Draft  
Date: 2026-03-07  
Author: Collaborative draft for next-repo planning

## 1) Purpose

Design a new repository (fork or fresh repo) for a pedagogical Python networking stack where learners fill in missing router logic progressively.

This redesign keeps the educational intent of the original pyCIE work, but resets structure around:

- one consistent code stack across all labs
- one consistent debug/trace model across all labs
- one required, sequential OSI-oriented learning path
- separate packet/data-plane and control-plane simulation abstractions
- CCNP-level implementation depth for all included protocols/features
- simplifying assumptions that keep implementation scope tractable

## 2) Problem Statement

The prior pyCIE codebase has broad protocol coverage and useful labs, but it grew into a wide topic map with multiple tracks. For this new repo, we want tighter pedagogy:

- strict dependency ordering (no skipping foundational mechanics)
- shared primitives reused lab-to-lab (not parallel mini-stacks)
- consistent observability semantics (same trace language everywhere)
- smaller conceptual surface at each step (pyTCP-like fill-in-the-blanks model)

## 3) Design Goals

1. Build durable intuition for router behavior via code, not CLI memorization.
2. Require sequential progression from lower-layer packet mechanics upward.
3. Make every lab extend the same RouterOS runtime and data model.
4. Keep all lab behavior deterministic and testable.
5. Make debugging first-class, uniform, and explainable.
6. Implement covered protocols at CCNP depth with bounded feature scope.
7. Preserve textbook-style documentation so students can step through every lab.
8. Split simulation concerns so packet behavior and routing behavior scale independently.

## 4) Non-Goals

1. Full vendor-grade protocol fidelity.
2. Real packet I/O on host NICs.
3. Kernel forwarding integration.
4. Full control-plane scale simulation (thousands of devices/routes).
5. Multi-threaded or non-deterministic event execution.

## 5) Guiding Principles

1. Single stack, many capabilities: labs unlock pieces of one runtime.
2. Determinism over realism: fixed tie-breaks, explicit drop reasons, stable event order.
3. Pedagogy over breadth: fewer protocols, CCNP-level depth on what is included.
4. Visible state transitions: every major state change emits structured debug events.
5. Small-step implementation: each TODO maps to one cognitive concept.

## 6) Target Users

- Software engineers filling networking knowledge gaps.
- Network engineers learning protocol behavior as executable logic.
- Mentors/instructors needing predictable lab outcomes and explainable traces.

## 7) Proposed Repository Shape

```text
repo/
  src/routeforge/
    runtime/
      simulator.py        # shared deterministic scheduler/clock
      dataplane_sim.py    # packet-level event loop
      controlplane_sim.py # protocol/timer/state event loop
      bridge.py           # typed bridge between the two simulations
      scheduler.py        # timer wheel + protocol job scheduling
      router.py           # RouterOS object + lifecycle hooks
      interface.py        # interface/link state, counters
      event_bus.py        # typed pub/sub for inter-module events
    model/
      packet.py           # frame/packet/headers + validation
      state.py            # router tables (FDB, ARP, RIB, FIB, sessions)
      decision.py         # canonical decision + reason codes
    engines/
      dataplane.py        # ingress/parse/l2/l3/l4/service/egress chain
      controlplane.py     # protocol daemon lifecycle + route arbitration
      policy.py           # ACL/NAT/QoS/policy chain execution
      management.py       # ops/observability checks and mgmt state
    protocols/
      ospf/
      bgp/
      bfd/
      stp/
      services/
    debug/
      events.py           # event schema + enums
      recorder.py         # JSONL sink + in-memory sink
      explain.py          # lab-aware explanations
      replay.py           # timeline/replay helpers
    labs/
      manifest.py         # ordered labs, prerequisites, capability gates
      capabilities.py     # feature flags + dependency graph
      scaffold.py         # TODO scaffold generation
    cli.py
  labs/
    lab01_.../README.md
    ...
  tests/
    contract/
    labs/
  docs/
    tutorial/             # chaptered textbook path through all labs
    labs/                 # per-lab step-by-step guides
```

## 8) Dual-Simulation Architecture (Data Plane + Control Plane)

The platform uses two simulation abstractions that run under one shared deterministic scheduler.

### 8.1 Simulation abstractions

1. `dataplane_sim`
   - Packet/frame focused.
   - Runs ingress/parse/l2/l3/l4/services/egress processing and queueing behavior.
2. `controlplane_sim`
   - Protocol-state focused.
   - Runs OSPF/BGP/BFD/STP FSMs, timer jobs, database updates, and route arbitration.

### 8.2 Shared timing model

Both simulators consume a single global scheduler/clock and deterministic ordering:

- ordering key: `(sim_time_ms, priority, sequence)`
- no wall-clock timing dependencies
- reproducible replay for both packet and protocol events

### 8.3 Bridge contract between simulations

The two simulators do not directly mutate each other's internals. They exchange typed bridge messages.

Normative contract reference:

- [`docs/bridge_contract.md`](bridge_contract.md)

Control plane -> data plane messages:

- `ROUTE_INSTALL`
- `ROUTE_WITHDRAW`
- `NEXTHOP_REWRITE_UPDATE`
- `POLICY_PROGRAM_UPDATE`

Data plane -> control plane messages:

- `INTERFACE_STATE_CHANGE`
- `ADJACENCY_SIGNAL`
- `FORWARDING_FAILURE_SIGNAL`
- `TRAFFIC_OBSERVATION_SIGNAL`

Scenario engine -> both simulators:

- `FAIL_LINK`, `RECOVER_LINK`, `FAIL_PEER`, `RECOVER_PEER`

### 8.4 Engines and responsibilities

1. Data plane engine
   - Runs packet path logic inside `dataplane_sim`.
2. Control plane engine
   - Runs protocol daemons inside `controlplane_sim`.
   - Arbitrates route candidates and emits route programming actions.
3. Policy engine
   - Executes ordered ACL/NAT/QoS and route-policy chains.
4. Management engine
   - Tracks health/readiness and operational observability state.
5. Scenario engine
   - Injects failures/recoveries and validates convergence expectations.

### 8.5 Event-driven integration model

All engines communicate through typed events and bridge messages:

- packet events (`PACKET_RX`, `PACKET_TX`, `PACKET_DROP`)
- control events (`NEIGHBOR_UP`, `LSA_INSTALLED`, `BGP_PATH_SELECTED`)
- bridge events (`ROUTE_INSTALL`, `INTERFACE_STATE_CHANGE`, `FORWARDING_FAILURE_SIGNAL`)
- state events (`RIB_CHANGED`, `FIB_PROGRAMMED`)
- timer events (`TIMER_EXPIRE`)
- scenario events (`FAIL_LINK`, `RECOVER_LINK`)

### 8.6 Extension contract for new topics

New topics are added as modules, not by changing core loops.

Each module declares:

1. `module_id`
2. dependencies (`requires=[...]`)
3. subscribed events
4. emitted events
5. state namespace
6. capability flags unlocked

This allows adding new protocols/features while preserving stable APIs and lab order.

### 8.7 Decision model (shared across engines)

Every significant step returns or emits a typed `Decision`:

- `action` (`forward`, `flood`, `drop`, `punt`, `encap`, `decap`, `queue`, `install`, `withdraw`)
- `reason_code` (global enum; stable across labs)
- `state_delta` (authoritative state updates)
- `next_hop`/`next_stage` metadata

The same decision schema powers tests, traces, and explanations.

## 9) Unified Debug and Explainability Model

### 9.1 Event contract

Every significant operation emits a `DebugEvent` with:

- `seq`, `sim_time_ms`, `node`, `lab_id`
- `sim_domain` (`DATAPLANE` or `CONTROLPLANE`)
- `stage` (`INGRESS`, `PARSE`, `L2`, `L3`, `L4`, `SERVICE`, `EGRESS`, `TIMER`)
- `action`, `reason_code`
- `packet_id` (optional for control-only timers)
- `before` and `after` snapshots (compact dictionaries)
- `module_id` (which engine/protocol emitted the event)
- `correlation_id` (links packet, timer, and control-plane cascades)

### 9.2 Canonical action/reason taxonomy

Use a small fixed set globally (instead of protocol-specific event explosion):

- Actions: `LOOKUP`, `SELECT`, `INSTALL`, `WITHDRAW`, `FORWARD`, `DROP`, `ENCAP`, `DECAP`, `QUEUE`, `DEQUEUE`, `TIMER_EXPIRE`
- Reasons: `NO_FDB_ENTRY`, `STP_BLOCKED`, `ARP_MISS`, `NO_ROUTE`, `TTL_EXPIRED`, `ACL_DENY`, `NAT_NO_SESSION`, `POLICY_REJECT`, etc.

Reason codes are namespaced for scale:

- `COMMON_*`
- `L2_*`
- `L3_*`
- `OSPF_*`
- `BGP_*`
- `POLICY_*`
- `SERVICE_*`
- `MGMT_*`

### 9.3 Debug levels

- `off`: no events
- `basic`: state transitions + final packet outcome
- `verbose`: per-stage decisions + candidate sets

### 9.4 Tooling expectations

- `routeforge run labXX --trace-out trace.jsonl`
- `routeforge debug replay --trace trace.jsonl`
- `routeforge debug explain --trace trace.jsonl --packet-id pX --lab labXX`

All labs use the same schema and same commands.

### 9.5 Debug schema constraints

To keep trace quality and determinism stable:

1. `before`/`after` snapshots are field-whitelisted per module.
2. Snapshot payload size is capped (contract test enforced).
3. All enumerations are versioned; breaking changes require schema version bump.
4. Each lab defines required checkpoint events that must appear in passing traces.
5. Bridge messages must emit paired trace checkpoints (`emit` and `apply`) with the same `correlation_id`.

## 10) Sequential OSI Curriculum (Required Order)

This sequence is mandatory by design; each lab depends on prior labs.

### Phase A: Layers 1-2 Foundations

1. `lab01_frame_and_headers`
   - Build/validate Ethernet + basic IPv4 packet structure.
2. `lab02_mac_learning_switch`
   - Learn/flood/unicast + MAC aging.
3. `lab03_vlan_and_trunks`
   - VLAN tagging/untagging, per-VLAN forwarding tables.
4. `lab04_stp`
   - Loop prevention with deterministic root/port role selection.
5. `lab05_stp_convergence_and_protection`
   - Topology change handling, timers, and protection checks (BPDU guard/root guard semantics).

### Phase B: Layer 3 Core Router Behavior

6. `lab06_arp_and_adjacency`
   - ARP request/reply + pending packet queue.
7. `lab07_ipv4_subnet_and_rib`
   - Connected/static routes + LPM decisions.
8. `lab08_fib_forwarding_pipeline`
   - TTL decrement, checksum update, egress resolution.
9. `lab09_icmp_and_control_responses`
   - Echo, unreachable, time-exceeded, traceroute semantics.
10. `lab10_ipv4_control_plane_diagnostics`
    - Deterministic troubleshooting flow: route, ARP, TTL, and ICMP decision visibility with explainability checkpoints.

### Phase C: OSPFv2 CCNP Track (Split for Progressive Depth)

11. `lab11_ospf_adjacency_fsm`
    - OSPF hello exchange, neighbor state machine, and adjacency gating.
12. `lab12_ospf_network_types_and_dr_bdr`
    - Broadcast/NBMA style behavior and DR/BDR election logic.
13. `lab13_ospf_lsa_flooding_and_lsdb`
    - LSA install/flood/aging semantics and loop-safe LSDB synchronization.
14. `lab14_ospf_spf_and_route_install`
    - SPF run triggers, path selection, ECMP handling, and route installation.
15. `lab15_ospf_multi_area_abr`
    - Inter-area behavior, ABR summaries, and route-type preference.

### Phase D: Layer 4 and Fast Failure Signals

16. `lab16_udp_tcp_fundamentals`
    - 5-tuple flow identity, TCP state behavior, and UDP validation.
17. `lab17_bfd_for_liveness`
    - Session state machine and timeout-driven failure detection.

### Phase E: Policy and Edge Services

18. `lab18_acl_pipeline`
    - Ordered first-match filtering + implicit deny.
19. `lab19_nat44_stateful_translation`
    - Session create/reuse/expire and return-path matching.
20. `lab20_qos_marking_and_queueing`
    - Classification, marking, queue admission/scheduling.

### Phase F: BGP-4 CCNP Track (Split for Progressive Depth)

21. `lab21_bgp_session_fsm_and_transport`
    - eBGP/iBGP session lifecycle, OPEN/KEEPALIVE/UPDATE handling, and timer-driven reset paths.
22. `lab22_bgp_attributes_and_bestpath`
    - Deterministic best-path selection over core attributes and tie-breakers.
23. `lab23_bgp_policy_and_filters`
    - Prefix/AS-path/community policy controls for import/export decisions.
24. `lab24_bgp_scaling_patterns`
    - Route reflection, next-hop behavior, and deterministic convergence semantics in larger topologies.

### Phase G: Overlay, Security, and Operations

25. `lab25_tunnels_and_ipsec`
    - GRE-like encap/decap + policy-driven protect/bypass/drop.
26. `lab26_observability_and_ops`
    - Structured logs/telemetry and readiness/state checks.
27. `lab27_capstone_incident_drill`
    - Multi-protocol failure/recovery with convergence assertions.

### 10.1 Prerequisite enforcement

The manifest defines strict prerequisites for every lab.

Examples:

1. `lab11_ospf_adjacency_fsm` requires labs `01-10`.
2. `lab15_ospf_multi_area_abr` requires labs `11-14`.
3. `lab21_bgp_session_fsm_and_transport` requires labs `01-20`.
4. `lab24_bgp_scaling_patterns` requires labs `21-23`.
5. `lab27_capstone_incident_drill` requires completion of all previous labs.

## 11) CCNP Conformance Profile

### 11.1 Conformance levels

Each protocol feature is labeled:

1. `MUST (v1)` required for initial release and CI conformance.
2. `SHOULD (v1.1+)` designed for near-term expansion.
3. `OUT (v1)` explicitly out of scope for initial release.

### 11.2 OSPFv2 feature matrix

| Feature area | MUST (v1) | SHOULD (v1.1+) | OUT (v1) |
| --- | --- | --- | --- |
| Neighboring | Full FSM (`Down` -> `Full`), hello/dead timers | Graceful-restart interactions | OSPFv3 |
| Network types | Broadcast + point-to-point | NBMA emulation | Virtual links |
| DR/BDR | Deterministic election and failover | Priority tuning edge-cases | Multi-vendor quirks |
| LSDB/LSA | Type 1/2/3/5 handling, flooding, aging, sequence checks | Type 4 coverage expansion | Opaque LSAs |
| SPF/routes | Deterministic SPF, ECMP policy, intra/inter/external preference | Incremental SPF optimization | Full traffic engineering |
| Multi-area | ABR summaries and inter-area propagation | Stub/totally-stub behavior | NSSA translator corner cases |
| Security | Basic auth hooks in model only | Deterministic auth failure scenarios | Cryptographic parity with vendors |

### 11.3 BGP-4 feature matrix

| Feature area | MUST (v1) | SHOULD (v1.1+) | OUT (v1) |
| --- | --- | --- | --- |
| Session FSM | `Idle` -> `Established`, timers, reset/notification paths | Graceful restart modeling | Full TCP stack fidelity |
| Topology modes | eBGP and iBGP support | Confederation examples | Multi-AFI/SAFI beyond IPv4 unicast |
| Best-path | Deterministic path selection across core attributes/tie-breakers | Multipath/ADD-PATH experiments | Vendor-specific knobs |
| Policy | Prefix/AS-path/community matching and import/export mutation | Larger policy language surface | Arbitrary scripting policy engines |
| Next-hop | Next-hop validation and next-hop-self behavior | Recursive next-hop optimization | MPLS labeled-unicast |
| Scale patterns | Route reflection behavior and convergence checks | Dynamic policy re-evaluation performance tuning | Internet-scale table simulation |

### 11.4 Cross-protocol CCNP expectations

1. ACL/NAT/QoS use production-like pipeline semantics with deterministic outcomes.
2. BFD can trigger deterministic control-plane reaction paths.
3. Troubleshooting fidelity is mandatory: traces and explain output must expose decision points at CCNP reasoning depth.

### 11.5 Simplifying assumptions

1. Deterministic simulator; no real-time race conditions.
2. No packet loss unless explicitly injected by scenario.
3. IPv4-only curriculum and implementation; no IPv6 scope in this repo.
4. OSPFv2 only.
5. BGP-4 IPv4 unicast only.
6. One queueing model (small fixed queue set + WRR).
7. IPsec uses simplified SA/key lifecycle while preserving policy and packet-transform logic.
8. Finite lab topologies with explicit fixture definitions.

### 11.6 Feature-to-lab traceability (v1 MUST)

| Protocol feature (MUST) | Primary labs |
| --- | --- |
| OSPF neighbor FSM and timer behavior | `lab11` |
| OSPF DR/BDR elections and failover | `lab12` |
| OSPF LSA flooding/aging and LSDB consistency | `lab13` |
| OSPF SPF, ECMP, and route install | `lab14` |
| OSPF multi-area ABR summaries | `lab15` |
| BGP session FSM and transport timers | `lab21` |
| BGP best-path deterministic tie-breaks | `lab22` |
| BGP policy import/export controls | `lab23` |
| BGP route reflection and scaling behavior | `lab24` |

## 12) Lab Authoring Contract

Every lab must define:

1. Prerequisites (strict list of prior labs).
2. Capability flags unlocked in this lab.
3. Target TODO methods and expected state transitions.
4. Deterministic exercise tests.
5. Edge-case tests.
6. Expected debug checkpoints (what events prove correctness).
7. Textbook chapter references, step-by-step guidance, and standards pointers.
8. CCNP conformance items covered in that lab (`MUST`/`SHOULD`/`OUT` traceability).

Conformance traceability is stored in:

- `labs/conformance_matrix.yaml`

This is the single machine-readable source for protocol/lab conformance and release gates to prevent docs/test drift.

### 12.1 Required textbook chapter template

Each tutorial chapter must include:

1. Learning objectives.
2. Prerequisite recap.
3. Concept walkthrough with topology diagram.
4. Implementation TODO map (function-by-function).
5. Verification commands and expected outputs.
6. Debug trace checkpoints and interpretation guidance.
7. Failure drills and troubleshooting flow.
8. Standards/pointer references.

## 13) Testing Strategy

1. `contract` tests: schema, CLI, deterministic ordering, scaffold integrity.
2. `bridge` tests: typed message validation across `dataplane_sim` and `controlplane_sim`.
3. `lab` tests: student-facing behavior, one marker per lab.
4. `conformance` tests: protocol `MUST (v1)` matrix validation for OSPF/BGP and core services.
5. `trace` tests: assert required event types/reasons/checkpoints appear in canonical paths.
6. `scenario` tests: deterministic failure/recovery and convergence assertions.
7. `docs` tests: tutorial/lab chapter links, chapter template completeness, and standards references remain valid.
8. `determinism` tests: repeated runs must produce identical normalized outcomes and stable ordering.

## 14) Migration Strategy from Current pyCIE

Keep current pyCIE intact. Build the new effort in a separate repo or top-level sibling tree.

### 14.1 Reuse candidates

- simulation/event queue primitives
- packet/header models
- test harness patterns and scaffold workflow
- existing docs language for pedagogical style

### 14.2 Do not port as-is

- broad event enum surface (replace with compact canonical action/reason model)
- non-sequential tracks (replace with one strict dependency chain)
- protocol breadth that bypasses foundational prerequisites

### 14.3 Suggested mapping

- Current L2/L3 fundamentals map into new `lab01`-`lab10`.
- Current OSPF depth is split across `lab11`-`lab15`.
- Current transport/BFD/policy/services map into `lab16`-`lab20`.
- Current BGP depth is split across `lab21`-`lab24`.
- Current tunnel/security/ops/capstone map into `lab25`-`lab27`.

## 15) Delivery Plan (Execution)

### Milestone 0: Platform Bootstrap (1-2 weeks)

- create new package skeleton + CLI
- add dual simulators (`dataplane_sim`, `controlplane_sim`) on one scheduler
- add multi-engine runtime (`dataplane`, `controlplane`, `policy`, `management`)
- add typed bridge contract and validation harness
- add debug schema and recorder with schema versioning
- add lab manifest, capability graph, and prerequisite gate

Exit criteria:

- `routeforge labs` prints ordered list
- `lab gating` prevents out-of-order runs
- trace schema contract tests pass
- module dependency loading works with deterministic ordering
- bridge contract tests pass for core message flows

### Milestone 1: Foundations (`lab01`-`lab10`, 4-6 weeks)

- deliver labs `01-10` with tests and docs
- publish textbook chapters for labs `01-10` with step-by-step exercises
- establish docs template CI checks

Exit criteria:

- learners can forward IPv4 packets end-to-end with deterministic traces
- docs chapters meet required template contract
- conformance harness framework exists (even if partially populated)

### Milestone 2: OSPFv2 CCNP Track (`lab11`-`lab15`, 3-4 weeks)

- deliver labs `11-15` with tests and docs
- publish textbook chapters for labs `11-15` with troubleshooting checkpoints
- implement OSPF `MUST (v1)` conformance tests

Exit criteria:

- OSPF CCNP `MUST (v1)` matrix passes in CI
- OSPF failure/recovery scenarios are deterministic and explainable

### Milestone 3: Services and Policy (`lab16`-`lab20`, 3-4 weeks)

- deliver labs `16-20` with tests and docs
- publish textbook chapters for labs `16-20`
- validate ACL/NAT/QoS pipeline conformance and debug checkpoints

Exit criteria:

- services pipeline outcomes are deterministic under edge-case tests
- control-plane and data-plane traces correlate by `correlation_id`

### Milestone 4: BGP-4 CCNP Track (`lab21`-`lab24`, 3-4 weeks)

- deliver labs `21-24` with tests and docs
- publish textbook chapters for labs `21-24`
- implement BGP `MUST (v1)` conformance tests

Exit criteria:

- BGP CCNP `MUST (v1)` matrix passes in CI
- route-reflector and policy scenarios converge deterministically

### Milestone 5: Integration and Capstone (`lab25`-`lab27`, 2-3 weeks)

- deliver labs `25-27` with tests and docs
- publish textbook chapters for labs `25-27` with incident walkthroughs
- finalize full-sequence learner path and capstone evaluation

Exit criteria:

- capstone scenarios pass with explainable timeline and failure reasons
- full tutorial progression (`lab01` -> `lab27`) is runnable end-to-end

## 16) Open Decisions

1. Repo name is fixed: `routeforge`.
2. Whether to support a short alias command in addition to `routeforge` (for example, `rfg`).
3. Whether to preserve existing lab IDs (`lab01`...) or reset naming convention.
4. Whether MPLS/VRF are in v1 or v1.1 expansion.
5. Whether OSPF auth and BGP multipath are promoted from `SHOULD` to `MUST` before v1 freeze.

## 17) Definition of Done for v1

v1 is done when:

1. Labs `01-27` all exist with docs + exercise + edge tests.
2. Strict prerequisite gating is enforced.
3. All labs use the same dual-simulation runtime, bridge contract, and debug schema.
4. OSPF and BGP `MUST (v1)` conformance matrices pass in CI.
5. Every lab has a complete tutorial chapter following the chapter template.
6. Capstone demonstrates multi-protocol failure and recovery.
7. A learner can run start-to-capstone without changing toolchain or workflow.
