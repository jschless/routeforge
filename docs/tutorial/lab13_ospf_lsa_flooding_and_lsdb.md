# Lab 13: OSPF LSA Flooding and LSDB

## Learning objectives

- Install LSAs into LSDB with deterministic keying.
- Refresh LSAs by incrementing sequence and resetting age.
- Age out LSAs at max age.

## Prerequisite recap

- Complete `lab12_ospf_network_types_and_dr_bdr`.
- Understand LSA lifecycle basics.

## Concept walkthrough

`lab13` focuses on LSDB mutation semantics: initial install, periodic refresh, and deterministic age-out at max age.

## Implementation TODO map

- `src/routeforge/runtime/ospf.py`: LSDB install/refresh/age helpers.
- `src/routeforge/labs/exercises.py`: LSDB lifecycle scenario.

## Verification commands and expected outputs

```bash
PYTHONPATH=src python -m routeforge run lab13_ospf_lsa_flooding_and_lsdb --completed lab01_frame_and_headers,lab02_mac_learning_switch,lab03_vlan_and_trunks,lab04_stp,lab05_stp_convergence_and_protection,lab06_arp_and_adjacency,lab07_ipv4_subnet_and_rib,lab08_fib_forwarding_pipeline,lab09_icmp_and_control_responses,lab10_ipv4_control_plane_diagnostics,lab11_ospf_adjacency_fsm,lab12_ospf_network_types_and_dr_bdr
```

Expected:

- `ospf_lsa_install` step `PASS`.
- `ospf_lsa_refresh` step `PASS`.
- `ospf_lsa_age_out` step `PASS`.
- Checkpoints include `OSPF_LSA_INSTALL`, `OSPF_LSA_REFRESH`, `OSPF_LSA_AGE_OUT`.

## Debug trace checkpoints and interpretation guidance

- `OSPF_LSA_INSTALL`: new LSA accepted into LSDB.
- `OSPF_LSA_REFRESH`: sequence advanced and age reset.
- `OSPF_LSA_AGE_OUT`: max-age record removed.

## Failure drills and troubleshooting flow

- Refresh unknown key and confirm deterministic failure behavior.
- Increase max-age threshold and confirm delayed age-out timing.

## Standards and references

- RFC 2328 LSDB/LSA aging behavior.
