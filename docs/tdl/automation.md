# TDL Primer: Automation

## Domain Overview

Automation challenges focus on model-driven configuration workflows used in modern network operations. The goal is to reason about config intent, deterministic edits, and safe remediation loops.

## Key Concepts

- YANG paths represent schema-aware object locations.
- NETCONF merge vs replace changes update semantics.
- RESTCONF PATCH should be idempotent for repeat requests.
- Drift detection compares intended and observed key/value state.
- Closed-loop remediation converts telemetry thresholds into bounded actions.

## Challenge Map

- `tdl_auto_01_yang_path_validation`: validate strict YANG-style path syntax.
- `tdl_auto_02_netconf_edit_merge_replace`: apply merge/replace behavior deterministically.
- `tdl_auto_03_restconf_patch_idempotence`: detect no-op vs effective PATCH updates.
- `tdl_auto_04_config_diff_and_drift_detection`: compute deterministic drift output.
- `tdl_auto_boss_closed_loop_remediation`: combine telemetry, policy, and remediation selection.

## Approach Guide

For `tdl_auto_01_yang_path_validation`, treat paths as structured tokens, not free text. Validate separators, namespace/key segments, and ordering constraints first. Then fail fast with stable error outcomes when input shape is invalid.

## Verification Tips

Correct solutions are stable across repeated runs, preserve deterministic ordering in outputs, and return exactly the contract strings expected by tests. Re-running the same input should not produce side effects.
