# TDL Primer: Resiliency

## Domain Overview

Resiliency challenges model convergence and stability controls under failure conditions. You will implement deterministic outcomes for tracking, dampening, pacing, and graceful restart handling.

## Key Concepts

- HSRP tracking recomputes priority from object health.
- BFD dampening suppresses unstable flapping behavior.
- IS-IS pacing limits burst intensity predictably.
- Graceful restart defines stale route retention/flush decisions.
- Incident triage should classify severity from combined indicators.

## Challenge Map

- `tdl_res_01_hsrp_priority_tracking`: recompute gateway priority deterministically.
- `tdl_res_02_bfd_flap_dampening`: apply suppress/unsuppress flap logic.
- `tdl_res_03_isis_lsp_pacing`: pace control updates under load.
- `tdl_res_04_graceful_restart_stale_timer`: decide stale-path action by timer state.
- `tdl_res_boss_control_plane_stability_incident`: triage multi-signal control-plane incidents.

## Approach Guide

For `tdl_res_01_hsrp_priority_tracking`, derive output only from deterministic inputs (base priority plus tracking penalties) and clamp values to valid bounds before role decision.

## Verification Tips

Verify hysteresis and timer-boundary behavior explicitly. Stable implementations prevent oscillation under repeated near-threshold events.
