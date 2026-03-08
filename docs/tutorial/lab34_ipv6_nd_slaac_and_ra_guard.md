# Lab 34: IPv6 ND, SLAAC, and RA Guard

## Learning objectives

- Implement `derive_slaac_host_id, ipv6_nd_slaac_ra_guard` in `src/routeforge/runtime/ipv6.py`.
- Deliver `ipv6_nd_learn`: neighbor discovery entry is learned on trusted RA.
- Deliver `ipv6_slaac_apply`: SLAAC derives deterministic global address.
- Deliver `ipv6_ra_guard_drop`: untrusted RA is blocked by RA guard.
- Validate internal behavior through checkpoints: ND_RA_TRUSTED, ND_RA_DROP, SLAAC_ADDR_DERIVED.

## Prerequisite recap

- Required prior labs: `lab33_fhrp_tracking_and_failover`.
- Confirm target mapping before coding with `routeforge show lab34_ipv6_nd_slaac_and_ra_guard`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

IPv6 removes the ARP broadcasts of IPv4 and replaces them with Neighbor Discovery Protocol (NDP). One of NDP's most important messages is the Router Advertisement (RA): a router periodically broadcasts an RA containing the network prefix for that link. Hosts use this prefix to configure their own global unicast addresses automatically — a process called Stateless Address Autoconfiguration (SLAAC).

```
  Router                           Host
  ------                           ----
  link-local: fe80::1              link-local: fe80::cafe
  |                                |
  |--- Router Advertisement ------>|  prefix: 2001:db8::/64
  |    (prefix: 2001:db8::/64)     |
                                   |  derives global address:
                                   |  2001:db8::cafe
```

SLAAC address derivation works as follows: take the 64-bit prefix from the RA and append a host identifier derived from the host's link-local address. In this lab the host identifier is the portion of the link-local address after `fe80::` (so `fe80::cafe` yields host ID `cafe`). The resulting global address is `prefix::host_id`.

The security concern is that any device on the link can send a forged RA claiming to be the default router and advertising a malicious prefix. A rogue RA can redirect all host traffic through an attacker's machine.

RA Guard addresses this by configuring switch ports as either trusted (connected to legitimate routers) or untrusted (connected to hosts). Router Advertisements arriving on untrusted ports are silently dropped before they can reach hosts.

```
  Switch port config:
  Port Gi0/1 -- TRUSTED   --> Router (allowed to send RAs)
  Port Gi0/2 -- UNTRUSTED --> Host   (RAs dropped)
  Port Gi0/3 -- UNTRUSTED --> Host   (RAs dropped)
```

In this lab `ipv6_nd_slaac_ra_guard` captures both decisions in one function:

- If `ra_trusted` is `False`, return `("DROP", "")`. The RA is discarded and no address is derived.
- If `ra_trusted` is `True`, derive the SLAAC address by combining the prefix with the host identifier extracted from `source_link_local`, then return `("ALLOW", slaac_address)`.

The helper `derive_slaac_host_id` extracts just the host-identifier portion, defaulting to `"1"` when the link-local address has no meaningful suffix (e.g., `fe80::` alone).

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/ipv6.py`
- Symbols: `derive_slaac_host_id, ipv6_nd_slaac_ra_guard`
- Why this target: derive deterministic host identifier and enforce RA trust policy.
- Stage check: `routeforge check lab34`

Function contract for this stage:

- Symbol: `derive_slaac_host_id(*, source_link_local: str) -> str`
- Required behavior: extract stable host-id from link-local input (defaulting to `1` when missing)
- Symbol: `ipv6_nd_slaac_ra_guard(*, ra_trusted: bool, source_link_local: str, prefix: str) -> tuple[Literal["ALLOW", "DROP"], str]`
- Required behavior: block untrusted RA; otherwise return SLAAC address as `prefix + host-id`

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab34_ipv6_nd_slaac_and_ra_guard`
3. Edit only `derive_slaac_host_id, ipv6_nd_slaac_ra_guard` in `src/routeforge/runtime/ipv6.py`.
4. Run `routeforge check lab34` until it exits with status `0`.
5. Run `routeforge run lab34_ipv6_nd_slaac_and_ra_guard --state-file "$STATE"` to confirm visible lab behavior and progress state updates.

## Verification commands and expected outputs

```bash
routeforge show lab34_ipv6_nd_slaac_and_ra_guard
routeforge check lab34

STATE=/tmp/routeforge-progress.json
routeforge run lab34_ipv6_nd_slaac_and_ra_guard --state-file "$STATE"
```

Expected outcomes:

- `routeforge show` prints `student.stage`, `student.target`, and `student.symbols` matching this chapter.
- `routeforge check lab34` passes when your implementation is complete for this stage.
- `ipv6_nd_learn` should print `[PASS]` (neighbor discovery entry is learned on trusted RA).
- `ipv6_slaac_apply` should print `[PASS]` (SLAAC derives deterministic global address).
- `ipv6_ra_guard_drop` should print `[PASS]` (untrusted RA is blocked by RA guard).
- Run output includes checkpoints: ND_RA_TRUSTED, ND_RA_DROP, SLAAC_ADDR_DERIVED.

## Debug trace checkpoints and interpretation guidance

Generate trace artifacts when a step fails:

```bash
routeforge run lab34_ipv6_nd_slaac_and_ra_guard --state-file "$STATE" --trace-out /tmp/lab34_ipv6_nd_slaac_and_ra_guard.jsonl
routeforge debug replay --trace /tmp/lab34_ipv6_nd_slaac_and_ra_guard.jsonl
routeforge debug explain --trace /tmp/lab34_ipv6_nd_slaac_and_ra_guard.jsonl --step ipv6_nd_learn
```

Checkpoint guide:

- `ND_RA_TRUSTED`: fires when a Router Advertisement arrives on a trusted port and is passed through for processing. The function received `ra_trusted=True` and proceeded past the drop check. If this checkpoint is missing when you pass a trusted RA, confirm that your function reads `ra_trusted` rather than hardcoding `False`, and that `"ALLOW"` is returned rather than `"DROP"`.

- `ND_RA_DROP`: fires when a Router Advertisement is silently dropped because the source port is untrusted. The function received `ra_trusted=False` and returned `("DROP", "")` immediately without deriving any address. If this checkpoint is missing when you send an untrusted RA, check that your early-return path for `ra_trusted=False` is reached before address derivation logic.

- `SLAAC_ADDR_DERIVED`: fires when a global unicast address is successfully built from the RA prefix and the host identifier. The returned string should be in the form `prefix::host_id`. If this checkpoint fires but the address value is wrong, trace through `derive_slaac_host_id` to verify the split on `fe80::` and the default of `"1"` for empty suffixes.

## Failure drills and troubleshooting flow

- Intentionally break `derive_slaac_host_id` or `ipv6_nd_slaac_ra_guard` in `src/routeforge/runtime/ipv6.py` and rerun `routeforge check lab34` to confirm tests catch regressions.
- If `routeforge run lab34_ipv6_nd_slaac_and_ra_guard --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- IPv6 ND, SLAAC, and RA guard controls.
