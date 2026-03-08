# TDL Primer: MPLS

## Domain Overview

MPLS challenges focus on label lifecycle and VPN control-plane constraints. You will model allocation, forwarding action choice, RT import/export, and VPNv4 install checks.

## Key Concepts

- LDP label allocation should be deterministic and reusable.
- Forwarding actions are PUSH, SWAP, or POP based on role/context.
- Route-target policy controls VRF route visibility.
- VPNv4 install requires valid next-hop and import policy checks.
- Data-plane traces should align with control-plane decisions.

## Challenge Map

- `tdl_mpls_01_ldp_label_allocation`: allocate and reuse labels predictably.
- `tdl_mpls_02_php_forwarding_decision`: decide PHP/forwarding action.
- `tdl_mpls_03_l3vpn_rt_import_export`: enforce RT import/export behavior.
- `tdl_mpls_04_vpnv4_next_hop_reachability`: gate install on reachability constraints.
- `tdl_mpls_boss_l3vpn_data_plane_trace`: trace end-to-end L3VPN decisions.

## Approach Guide

For `tdl_mpls_01_ldp_label_allocation`, model labels as deterministic mapping results keyed by FEC context. Repeated requests for the same key should return stable values.

## Verification Tips

Check for deterministic label/action output ordering and explicit deny reasons when RT or next-hop constraints fail. Avoid implicit defaults.
