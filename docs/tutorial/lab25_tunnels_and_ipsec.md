# Lab 25: Tunnels and IPsec

## Learning objectives

- Model deterministic encapsulation and decapsulation flow.
- Evaluate policy decisions for protected destinations.
- Verify security association lookup behavior.

## Prerequisite recap

- Complete `lab24_bgp_scaling_patterns`.
- Recall packet encapsulation semantics from previous forwarding labs.

## Concept walkthrough

`lab25` introduces service encapsulation plus policy checks. Packets are wrapped with outer headers, then policy and SA lookups determine secure forwarding behavior.

## Implementation TODO map

- `src/routeforge/runtime/tunnel_ipsec.py`: tunnel + policy primitives.
- `src/routeforge/labs/exercises.py`: encapsulation/IPsec scenario.

## Verification commands and expected outputs

```bash
PYTHONPATH=src python -m routeforge run lab25_tunnels_and_ipsec --completed <all-labs-lab01-through-lab24>
```

Expected:

- `tunnel_encap_push` step `PASS`.
- `tunnel_decap_pop` step `PASS`.
- `ipsec_policy_evaluate` step `PASS`.
- `ipsec_sa_lookup` step `PASS`.
- Checkpoints include `ENCAP_PUSH`, `ENCAP_POP`, `IPSEC_POLICY_EVALUATE`, `IPSEC_SA_LOOKUP`.

## Debug trace checkpoints and interpretation guidance

- `ENCAP_PUSH`: outer tunnel headers were applied.
- `ENCAP_POP`: inner payload fields were restored.
- `IPSEC_POLICY_EVALUATE`: policy action selected (`PROTECT`/`BYPASS`).
- `IPSEC_SA_LOOKUP`: peer SA lookup result and SPI.

## Failure drills and troubleshooting flow

- Use a destination outside protected prefixes and confirm policy becomes `BYPASS`.
- Remove peer SA entry and verify lookup returns no SPI.

## Standards and references

- GRE/IP tunnel model concepts and IPsec policy/SA processing basics.
