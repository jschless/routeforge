# TDL Primer: Routing

## Domain Overview

Routing-policy challenges cover how routes are matched, transformed, and accepted or denied in enterprise BGP policy chains.

## Key Concepts

- Prefix-list semantics include exact and range matches.
- Route-map processing is ordered and first-match wins.
- Community policy can add, remove, or replace tags.
- Local-pref and MED influence best-path at different scopes.
- Pipeline transparency matters for troubleshooting policy outcomes.

## Challenge Map

- `tdl_route_01_prefix_list_match`: implement prefix-list decision logic.
- `tdl_route_02_route_map_sequence_eval`: evaluate route-map sequence ordering.
- `tdl_route_03_bgp_community_policy`: apply deterministic community transforms.
- `tdl_route_04_local_pref_and_med_policy`: transform best-path attributes.
- `tdl_route_boss_policy_pipeline_debug`: evaluate complete policy pipeline behavior.

## Approach Guide

For `tdl_route_01_prefix_list_match`, think of the list as an ordered predicate set. Evaluate entries in order, return on first match, and apply default deny when no entries match.

## Verification Tips

Use deterministic ordering in output attributes and preserve original values when policy does not match. Test equivalent prefixes to confirm ge/le boundary handling.
