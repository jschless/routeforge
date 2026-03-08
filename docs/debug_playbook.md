# RouteForge Debug Playbook

This playbook is the repeatable workflow for debugging failed labs.

Use it whenever `routeforge run <lab_id>` shows `[FAIL]`.

## End-to-End Cycle (Lab 05 Example)

### 1) Reproduce the failure

```bash
routeforge run lab05_stp_convergence_and_protection
```

You will see step-level status lines. If one step fails, copy the step name.

### 2) Capture a dedicated trace file

```bash
routeforge run lab05_stp_convergence_and_protection --trace-out /tmp/lab05_debug.jsonl
```

This writes deterministic JSONL records for each step. Keep one trace per attempt so you can compare before/after changes.

### 3) Replay the sequence

```bash
routeforge debug replay --trace /tmp/lab05_debug.jsonl
```

This gives a chronological timeline (sequence, step, action, reason, checkpoints). Use replay first to confirm whether the failure is isolated to one step or part of a broader chain.

### 4) Explain one failing step

```bash
routeforge debug explain --trace /tmp/lab05_debug.jsonl --step stp_root_election
```

Use explain on the exact failing step. It summarizes action/reason/checkpoints and protocol-specific details.

### 5) Cross-check checkpoint intent

Open the matching tutorial chapter and compare expected checkpoint sequence with what your trace emitted. A wrong checkpoint often means your logic is returning the right shape with the wrong branch condition.

### 6) Fix and re-run

After editing the target symbol:

```bash
routeforge check lab05
routeforge run lab05_stp_convergence_and_protection --trace-out /tmp/lab05_after.jsonl
```

If needed, diff replay output between `/tmp/lab05_debug.jsonl` and `/tmp/lab05_after.jsonl`.

## What Good Debugging Looks Like

- You start from one concrete failing step, not the whole module.
- You confirm action/reason/checkpoint drift in trace output.
- You fix one function contract at a time.
- You re-run stage checks and scenario run together.

## Common Failure Patterns

- Right action, wrong reason string: contract mismatch despite logical behavior.
- Correct return type, missing checkpoint: conformance-visible gap.
- Function appears to work in isolation, but scenario fails: wrong integration assumptions.
- Repeated fails across later labs: early contract bug propagating through prerequisites.

## Checkpoint Dictionary (Labs 01-27)

- `PARSE_OK`: frame/header parsing completed without validation errors.
- `VLAN_CLASSIFY`: ingress VLAN classification was computed.
- `MAC_LEARN`: source MAC was learned into the forwarding table.
- `L2_FLOOD`: unknown destination triggered flood forwarding behavior.
- `PARSE_DROP`: validation failure caused parse-stage drop.
- `L2_UNICAST_FORWARD`: known destination triggered unicast forwarding.
- `VLAN_TAG_PUSH`: access-to-trunk egress applied VLAN tag.
- `VLAN_TAG_POP`: trunk-to-access egress removed VLAN tag.
- `STP_ROOT_CHANGE`: STP elected or changed the root bridge.
- `STP_PORT_ROLE_CHANGE`: STP recomputed per-port roles.
- `STP_TOPOLOGY_CHANGE`: topology change event triggered reconvergence logic.
- `STP_GUARD_ACTION`: BPDU guard decision was applied.
- `ARP_REQUEST_TX`: ARP request transmission was emitted.
- `ARP_REPLY_RX`: ARP reply reception was processed.
- `ARP_CACHE_UPDATE`: adjacency/ARP cache state was updated.
- `RIB_ROUTE_INSTALL`: route was installed in the RIB.
- `ROUTE_LOOKUP`: route lookup operation executed.
- `ROUTE_SELECT`: route selection decision completed.
- `TTL_DECREMENT`: forwarding logic decremented packet TTL.
- `FIB_FORWARD`: FIB resolved a forward action.
- `FIB_DROP`: FIB lookup produced a drop decision.
- `ICMP_ECHO_REPLY`: control plane generated ICMP echo reply.
- `ICMP_UNREACHABLE`: control plane generated unreachable response.
- `ICMP_TIME_EXCEEDED`: control plane generated time-exceeded response.
- `EXPLAIN_CHECKPOINT`: diagnostic explain path executed.
- `DROP_REASON_ASSERT`: drop reason assertion check completed.
- `OSPF_HELLO_RX`: OSPF hello reception event processed.
- `OSPF_NEIGHBOR_CHANGE`: OSPF neighbor FSM changed state.
- `OSPF_DR_ELECT`: DR election logic ran.
- `OSPF_BDR_ELECT`: BDR election logic ran.
- `OSPF_DR_FAILOVER`: DR failover selection executed.
- `OSPF_LSA_INSTALL`: LSA install logic updated LSDB state.
- `OSPF_LSA_REFRESH`: LSA refresh logic updated sequence/age.
- `OSPF_LSA_AGE_OUT`: max-age LSA removal path ran.
- `OSPF_SPF_RUN`: SPF computation executed.
- `OSPF_SUMMARY_ORIGINATE`: ABR summary origination logic executed.
- `OSPF_INTERAREA_ROUTE_INSTALL`: inter-area route install path executed.
- `FLOW_CLASSIFY`: transport flow classifier executed.
- `TCP_STATE_CHANGE`: TCP FSM transition executed.
- `UDP_VALIDATE`: UDP header validation executed.
- `BFD_CONTROL_RX`: BFD control packet handling executed.
- `BFD_STATE_CHANGE`: BFD session state transition executed.
- `BFD_TIMEOUT`: BFD timeout detection path executed.
- `ACL_EVALUATE`: ACL rule evaluation pipeline executed.
- `ACL_PERMIT`: ACL permit decision path executed.
- `ACL_DENY`: ACL deny decision path executed.
- `NAT_SESSION_CREATE`: NAT session allocation executed.
- `NAT_TRANSLATE_OUTBOUND`: outbound NAT translation path executed.
- `NAT_TRANSLATE_INBOUND`: inbound NAT translation path executed.
- `NAT_SESSION_EXPIRE`: NAT session aging/expiry path executed.
- `QOS_REMARK`: QoS remarking decision executed.
- `QOS_ENQUEUE`: packet was enqueued in QoS queue.
- `QOS_DEQUEUE`: packet was dequeued from QoS queue.
- `BGP_OPEN_RX`: BGP OPEN reception processing executed.
- `BGP_SESSION_CHANGE`: BGP session FSM state transition executed.
- `BGP_UPDATE_RX`: BGP UPDATE reception processing executed.
- `BGP_BEST_PATH`: BGP best-path selection executed.
- `BGP_POLICY_APPLY`: BGP export/import policy pipeline executed.
- `BGP_UPDATE_EXPORT`: BGP update export generation executed.
- `BGP_RR_REFLECT`: route-reflector reflection decision executed.
- `BGP_CONVERGENCE_MARK`: convergence stability marker was computed.
- `BGP_MULTIPATH_SELECT`: multipath candidate selection executed.
- `ENCAP_PUSH`: tunnel encapsulation push path executed.
- `ENCAP_POP`: tunnel decapsulation pop path executed.
- `IPSEC_POLICY_EVALUATE`: IPsec policy match/evaluate path executed.
- `IPSEC_SA_LOOKUP`: security association lookup executed.
- `OPS_READINESS_CHECK`: operational readiness checks executed.
- `TELEMETRY_EMIT`: telemetry emission path executed.
- `SCENARIO_STEP_APPLY`: capstone scenario step state was applied.
- `CONVERGENCE_ASSERT`: capstone convergence assertion evaluated.
