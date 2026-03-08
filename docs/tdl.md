# TDL Side Quests

TDL means **Test Driven Learning**.

It is an optional gamified side-quest track that covers CCNP-adjacent topics not in the core lab chain. Where core labs (lab01–lab39) teach end-to-end protocol workflows, TDL isolates individual concepts into short, focused challenges.

## Unlocking TDL (Read This First)

TDL unlocks automatically after you complete **lab27_capstone_incident_drill**.

Until then, `routeforge tdl list` will show most entries as `LOCKED`, even if the
challenge code and tests exist in the repository. This is expected behavior.

Fast unlock check:

1. complete `lab27_capstone_incident_drill`
2. run `routeforge tdl list`
3. verify first mission in each domain shows `UNLOCKED`

## What TDL Covers

TDL challenges span six domains that extend beyond the core curriculum:

| Domain | Topics |
|---|---|
| **Automation** | YANG path validation, NETCONF, RESTCONF, config drift detection, closed-loop remediation |
| **Multicast** | RPF check, PIM DR election, IGMP snooping, RP mapping, end-to-end multicast forwarding |
| **Wireless** | Client join FSM, channel conflict scoring, roaming decision, WMM queue mapping |
| **Routing Policy** | Prefix lists, route-map sequences, BGP community policy, local-pref/MED transforms |
| **MPLS** | LDP label allocation, PHP forwarding, L3VPN RT import/export, VPNv4 next-hop reachability |
| **Resiliency** | HSRP priority tracking, BFD flap dampening, IS-IS LSP pacing, graceful restart |

## Domain Primers

Full per-domain primers:

- [Automation Primer](tdl/automation.md)
- [Multicast Primer](tdl/multicast.md)
- [Wireless Primer](tdl/wireless.md)
- [Routing Primer](tdl/routing.md)
- [MPLS Primer](tdl/mpls.md)
- [Resiliency Primer](tdl/resiliency.md)

### Automation

Automation missions model network configuration as structured data, not CLI text.
Before starting this domain, make sure you understand that YANG defines schema,
NETCONF applies structured edits to that schema, and RESTCONF exposes similar
operations over REST semantics. In practical terms: a path is valid only if it
matches the model shape, merge/replace operations must be deterministic, and
idempotence means applying the same patch twice should not create additional
state drift. In closed-loop workflows, config drift detection compares intended
state to observed state and emits specific remediation actions. Think in terms
of state transitions and invariants, not command-by-command diffs.

### Multicast

Multicast missions focus on control-plane correctness before forwarding scale.
Key prerequisite ideas: RPF checks validate that traffic arrived on the expected
upstream path, PIM DR election picks one designated router per segment with
deterministic tie-breaks, and IGMP snooping tracks listener membership over time.
RP mapping then connects group ranges to rendezvous points for shared-tree
construction. If you are rusty, review `(*,G)` vs `(S,G)` behavior and why
membership aging matters for pruning stale entries. A useful mindset is to treat
multicast forwarding as constrained distribution: every branch decision should
be explainable by upstream reachability plus downstream interest.

### Wireless

Wireless missions emphasize finite-state behavior and classification decisions.
Client join workflows (auth/assoc/ready) are modeled as explicit FSM transitions,
so illegal transitions should be rejected deterministically. Channel conflict
scoring and roaming decisions combine signal quality with hysteresis and policy
guardrails; the point is reproducible decisioning under noisy inputs. WMM queue
mapping ties traffic class intent to service queues, so correctness is mostly
about consistent class-to-queue mapping and tie-breaks. Approach these missions
as control logic problems: define valid state, identify transition triggers, and
keep policy outcomes stable when inputs are equal.

### Routing Policy

Routing policy missions model how engineers control route propagation. Prefix
lists are match primitives; route maps are ordered pipelines where first match
wins and implicit deny exists unless explicitly overridden. Community handling
adds metadata-driven policy, while local-pref and MED transformations influence
best-path outcomes at different scopes (intra-AS vs inter-AS influence). Before
starting, be comfortable with exact/longer-prefix match behavior and sequence
ordering effects. A reliable implementation pattern is: normalize input, evaluate
match conditions in deterministic order, then apply set actions once. Avoid
implicit side effects; policy chains should be transparent and replayable.

### MPLS

MPLS missions focus on label lifecycle and VPN control boundaries. LDP label
allocation requires deterministic mapping and stable reuse; PHP decisions control
where label popping occurs to simplify downstream forwarding. L3VPN RT import/
export determines tenant route visibility, and VPNv4 next-hop reachability gates
whether a control-plane route can safely install. If MPLS is rusty, review LIB
vs LFIB roles, swap/pop/push actions, and route-target semantics for VRF import
policy. Treat each mission as a pipeline stage: allocate, program, decide import,
then verify forwarding intent matches control-plane constraints.

### Resiliency

Resiliency missions model failure handling with predictable convergence behavior.
HSRP tracking recomputes priority from object health; BFD dampening prevents
state thrash under flap storms; IS-IS pacing smooths control bursts; graceful
restart logic decides when to retain or withdraw stale paths. The core concept is
not just \"fail fast\" but \"recover predictably\". Inputs may oscillate, but policy
must avoid unstable loops and repeated churn. When implementing these missions,
focus on timer and threshold boundaries, explicit suppression conditions, and
clear reasons for state transitions so incident triage remains explainable.

## Missions vs Bosses

Each domain has **four missions** and **one boss challenge**:

- **Missions (100 XP each)** — single-concept challenges. Implement one function and pass its tests. Faster to complete; good for exploring a topic.
- **Bosses (300 XP each)** — multi-concept challenges that combine all four missions from the domain. Stricter edge cases, larger test surface. Complete all four missions in a domain before unlocking the boss.

## Prerequisites and Unlock Order

TDL is separate from the core assessment. To start TDL:

1. Complete **lab27_capstone_incident_drill** (the final core lab).
2. Run `routeforge tdl list` to see which challenges are unlocked.

Within each domain, challenges unlock in order (mission 01, 02, 03, 04, then boss). You cannot skip missions.

## TDL Score vs Core Assessment

TDL XP and badges are tracked separately from the core CCNP assessment score:

- Core score (labs 01–39) determines your PASS / MERIT / DISTINCTION band.
- TDL XP and domain badges (`automation_complete`, `multicast_complete`, etc.) are bonus achievements.
- TDL completion does **not** affect `routeforge report` score or `capstone.ready` status.

## Student Workflow

```bash
# 1) See available side quests and lock state
routeforge tdl list

# 2) Inspect one challenge's contract
routeforge tdl show tdl_auto_01_yang_path_validation

# 3) Implement the target function
$EDITOR src/routeforge/runtime/tdl.py

# 4) Run only this challenge's tests
routeforge tdl check tdl_auto_01_yang_path_validation

# 5) Run the scenario and update TDL XP/progress
routeforge tdl run tdl_auto_01_yang_path_validation

# 6) Check total TDL progress
routeforge tdl progress show
```

Notes:

- `routeforge tdl run` persists progress in `~/.routeforge_tdl_progress.json` by default.
- If the home-directory TDL progress file does not exist yet but a legacy local `.routeforge_tdl_progress.json` is present in your current working directory, the CLI warns and reuses that legacy file until you migrate it.
- If prerequisites are not complete, the challenge prints `blocked`.
- `routeforge tdl check all` runs the full TDL test suite.

## Challenge Map

| ID | Domain | Kind | XP | Target Symbol |
|---|---|---|---|---|
| `tdl_auto_01_yang_path_validation` | Automation | mission | 100 | `validate_yang_path` |
| `tdl_auto_02_netconf_edit_merge_replace` | Automation | mission | 100 | `netconf_edit_merge_replace` |
| `tdl_auto_03_restconf_patch_idempotence` | Automation | mission | 100 | `restconf_patch_idempotence` |
| `tdl_auto_04_config_diff_and_drift_detection` | Automation | mission | 100 | `config_drift_diff` |
| `tdl_auto_boss_closed_loop_remediation` | Automation | boss | 300 | `closed_loop_remediation` |
| `tdl_mcast_01_rpf_check` | Multicast | mission | 100 | `rpf_check` |
| `tdl_mcast_02_pim_dr_election` | Multicast | mission | 100 | `pim_dr_election` |
| `tdl_mcast_03_igmp_snooping_membership_aging` | Multicast | mission | 100 | `igmp_snooping_membership` |
| `tdl_mcast_04_rp_mapping_decision` | Multicast | mission | 100 | `rp_mapping` |
| `tdl_mcast_boss_end_to_end_tree_debug` | Multicast | boss | 300 | `multicast_tree_forward` |
| `tdl_wlan_01_client_join_state_machine` | Wireless | mission | 100 | `client_join_fsm` |
| `tdl_wlan_02_ap_channel_conflict_scoring` | Wireless | mission | 100 | `channel_conflict_score` |
| `tdl_wlan_03_roaming_decision` | Wireless | mission | 100 | `roaming_decision` |
| `tdl_wlan_04_wmm_queue_mapping` | Wireless | mission | 100 | `wmm_queue_map` |
| `tdl_wlan_boss_site_incident_triage` | Wireless | boss | 300 | `wireless_incident_triage` |
| `tdl_route_01_prefix_list_match` | Routing | mission | 100 | `prefix_list_match` |
| `tdl_route_02_route_map_sequence_eval` | Routing | mission | 100 | `route_map_eval` |
| `tdl_route_03_bgp_community_policy` | Routing | mission | 100 | `community_policy_apply` |
| `tdl_route_04_local_pref_and_med_policy` | Routing | mission | 100 | `attribute_policy_transform` |
| `tdl_route_boss_policy_pipeline_debug` | Routing | boss | 300 | `policy_pipeline_decision` |
| `tdl_mpls_01_ldp_label_allocation` | MPLS | mission | 100 | `ldp_label_allocate` |
| `tdl_mpls_02_php_forwarding_decision` | MPLS | mission | 100 | `mpls_forward_action` |
| `tdl_mpls_03_l3vpn_rt_import_export` | MPLS | mission | 100 | `vrf_rt_import_export` |
| `tdl_mpls_04_vpnv4_next_hop_reachability` | MPLS | mission | 100 | `vpnv4_install_decision` |
| `tdl_mpls_boss_l3vpn_data_plane_trace` | MPLS | boss | 300 | `l3vpn_trace_forward` |
| `tdl_res_01_hsrp_priority_tracking` | Resiliency | mission | 100 | `hsrp_priority_recompute` |
| `tdl_res_02_bfd_flap_dampening` | Resiliency | mission | 100 | `bfd_flap_dampening` |
| `tdl_res_03_isis_lsp_pacing` | Resiliency | mission | 100 | `isis_lsp_pacing` |
| `tdl_res_04_graceful_restart_stale_timer` | Resiliency | mission | 100 | `gr_stale_path_action` |
| `tdl_res_boss_control_plane_stability_incident` | Resiliency | boss | 300 | `control_plane_stability_triage` |

## XP and Badges

- Missions: 100 XP each (20 missions × 100 = 2,000 XP maximum from missions)
- Bosses: 300 XP each (6 bosses × 300 = 1,800 XP maximum from bosses)
- **Maximum TDL XP: 4,200**

Domain badges (awarded when all missions and boss in a domain are complete):

- `automation_complete`
- `multicast_complete`
- `wireless_complete`
- `routing_complete`
- `mpls_complete`
- `resiliency_complete`
- `tdl_master` — awarded when all 6 domain badges are earned

## Common Failure Patterns

- Returning strings that differ from the expected contract values (case matters)
- Skipping deterministic tie-break behavior in selection functions
- Mutating input structures (tuples, sets) instead of returning new ones
- Ignoring prerequisite lock sequencing between missions within a domain
