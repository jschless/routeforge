# RouteForge Architecture Overview

RouteForge is organized as a deterministic simulation stack. The same pattern repeats across labs: students implement a small contract function, a lab scenario calls that function with fixed inputs, and the runtime emits checkpoints that become both debug breadcrumbs and conformance evidence.

## Layer 1: Model Layer

`src/routeforge/model/packet.py` defines packet-level data structures and validation contracts used by the early labs.

Key responsibilities:

- represent typed frame/header inputs (`EthernetFrame`, `IPv4Header`)
- normalize and validate protocol fields
- return deterministic error code strings that tests assert directly

The model layer is intentionally small. It exists to keep data representation and field validation separate from forwarding logic.

## Layer 2: Runtime Layer

Runtime modules under `src/routeforge/runtime/` implement the protocol mechanics students code against.

The main flow is layered:

- L2 switching path: `interface.py -> router.py -> dataplane_sim.py`
- L3 forwarding path: `adjacency.py -> l3.py`
- Control-plane path: `ospf.py`, `bgp.py`, `stp.py`, then route/policy outcomes returned into scenario steps
- Service features: `nat44.py`, `policy_acl.py`, `qos.py`, `tunnel_ipsec.py`, `observability.py`, `capstone.py`

Each function returns explicit outputs (`action`, `reason`, and details/checkpoints) instead of mutating opaque global state. That design keeps runs reproducible and debugging traceable.

### L2 Data Flow (Typical Early Lab)

```text
Ingress Frame
    |
    v
[Interface VLAN admission]
    |
    v
[Router MAC learning + lookup]
    |
    +--> unknown dst -> L2_FLOOD -> egress list
    |
    +--> known dst   -> L2_UNICAST_FORWARD -> single egress
    |
    v
[DataplaneSim result + checkpoints]
```

In this path, checkpoint strings such as `PARSE_OK`, `VLAN_CLASSIFY`, `MAC_LEARN`, and `L2_FLOOD`/`L2_UNICAST_FORWARD` are the machine-readable record of what happened internally.

### L3/Control Data Flow (Routing Labs)

```text
IPv4 Packet
    |
    v
[RIB lookup / SPF output]
    |
    +--> route exists -> FIB_FORWARD + TTL_DECREMENT
    |
    +--> no route     -> FIB_DROP + control reason
    |
    v
[Control responses (ICMP/OSPF/BGP decisions)]
    |
    v
[Scenario step outcome + checkpoints]
```

OSPF and BGP labs follow the same deterministic pattern: FSM transitions and selection logic emit explicit checkpoint markers (for example, `OSPF_NEIGHBOR_CHANGE`, `BGP_BEST_PATH`) that scenario tests and conformance mapping consume.

## Layer 3: Lab Infrastructure

The lab framework under `src/routeforge/labs/` binds learning flow to runtime behavior.

Core components:

- `manifest.py`: ordered lab list and prerequisites
- `exercises.py`: lab scenario runners returning `LabRunResult`
- `contracts.py`: `LabStepResult`/outcome types and trace-record conversion
- `conformance.py`: feature-level MUST/SHOULD/OUT matrix loader
- `progress.py`: learner progress persistence (`completed`, `run_counts`, `pass_counts`)
- `assessment.py`: weighted readiness score and band calculation
- `student_targets.py`: file/symbol map for student implementation targets

The CLI (`src/routeforge/cli.py`) is a thin orchestrator over these modules. It does not contain protocol logic; it resolves prerequisites, runs scenarios/checks, and presents actionable output.

## Steps, Checkpoints, and Conformance

RouteForge has three related but distinct evaluation units:

- **Step**: a human-readable assertion in a lab run (`[PASS]`/`[FAIL]`/`[TODO]`)
- **Checkpoint**: internal machine marker emitted by runtime decisions
- **Conformance feature**: higher-level capability in `labs/conformance_matrix.yaml` mapped across labs

Relationship:

1. A scenario step exercises one or more runtime functions.
2. Those functions emit checkpoints.
3. Conformance features reference checkpoint-covered behavior across labs.

So if a step fails, debugging starts at the trace/checkpoint level; if conformance coverage is weak, remediation starts at lab progression level.

## Why This Shape Works for Learning

This decomposition keeps student effort focused:

- students implement narrow functions with explicit contracts
- scenarios translate function correctness into behavior-level outcomes
- checkpoints expose internal execution points without requiring custom debuggers
- readiness reports summarize learning progress without hiding protocol details

The result is a workbook that behaves like a deterministic simulator, but remains small enough to reason about per function and per lab.
