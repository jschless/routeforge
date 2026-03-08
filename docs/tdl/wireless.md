# TDL Primer: Wireless

## Domain Overview

Wireless challenges model deterministic client and RF control logic. The emphasis is stable FSM transitions, conflict scoring, roam choices, and queue mapping.

## Key Concepts

- Client join is a finite-state machine with valid transitions only.
- Channel conflict scoring should be reproducible for identical inputs.
- Roaming decisions use hysteresis to prevent oscillation.
- WMM queue mapping ties class intent to deterministic queue class.
- Incident triage combines multiple signals into one dominant cause.

## Challenge Map

- `tdl_wlan_01_client_join_state_machine`: implement deterministic join FSM transitions.
- `tdl_wlan_02_ap_channel_conflict_scoring`: score interference severity.
- `tdl_wlan_03_roaming_decision`: select roam target using stable policy.
- `tdl_wlan_04_wmm_queue_mapping`: map class markers to queue labels.
- `tdl_wlan_boss_site_incident_triage`: classify site incidents from compounded symptoms.

## Approach Guide

For `tdl_wlan_01_client_join_state_machine`, define an explicit transition table first. Unknown events or illegal transitions should return deterministic no-change or reject outcomes.

## Verification Tips

Correct answers avoid hidden mutable state and return identical outcomes for repeated equivalent event sequences. Validate tie-break rules for equal scores.
