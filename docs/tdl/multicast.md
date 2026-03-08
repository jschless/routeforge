# TDL Primer: Multicast

## Domain Overview

Multicast challenges focus on deterministic control decisions for one-to-many distribution. You will model RPF, DR election, listener membership, and RP mapping behavior.

## Key Concepts

- RPF validation checks upstream interface correctness.
- PIM DR election uses deterministic priority/tie-break rules.
- IGMP snooping membership must age and prune stale listeners.
- RP mapping selects rendezvous points for group ranges.
- End-to-end forwarding requires both upstream validity and downstream interest.

## Challenge Map

- `tdl_mcast_01_rpf_check`: verify inbound interface against expected RPF path.
- `tdl_mcast_02_pim_dr_election`: elect DR deterministically.
- `tdl_mcast_03_igmp_snooping_membership_aging`: maintain listener state through join/leave/aging.
- `tdl_mcast_04_rp_mapping_decision`: map group ranges to RP decisions.
- `tdl_mcast_boss_end_to_end_tree_debug`: combine all checks into forwarding outcomes.

## Approach Guide

For `tdl_mcast_01_rpf_check`, model the decision as a pure function: expected upstream plus observed ingress produces ALLOW or DROP with explicit reasons. Keep tie-break handling deterministic.

## Verification Tips

Watch for edge cases around stale memberships and tie-breaks. Correct output should include deterministic drop reasons and should not depend on insertion order of input structures.
