# Lab 22: BGP Attributes and Best Path

## Learning objectives

- Compare multiple BGP paths for one prefix.
- Apply deterministic best-path ordering.
- Validate that best-path selection is reproducible.

## Prerequisite recap

- Complete `lab21_bgp_session_fsm_and_transport`.
- Recall route-selection thinking from `lab07_ipv4_subnet_and_rib`.

## Concept walkthrough

`lab22` introduces attribute-based route selection. Candidate paths are scored with a stable order so repeated runs produce the same winner.

## Implementation TODO map

- `src/routeforge/runtime/bgp.py`: best-path comparator.
- `src/routeforge/labs/exercises.py`: path ingestion and winner selection scenario.

## Verification commands and expected outputs

```bash
PYTHONPATH=src python -m routeforge run lab22_bgp_attributes_and_bestpath --completed <all-labs-lab01-through-lab21>
```

Expected:

- `bgp_update_receive` step `PASS`.
- `bgp_best_path_select` step `PASS`.
- Checkpoints include `BGP_UPDATE_RX` and `BGP_BEST_PATH`.

## Debug trace checkpoints and interpretation guidance

- `BGP_UPDATE_RX`: candidate path set was ingested.
- `BGP_BEST_PATH`: deterministic winner was selected.

## Failure drills and troubleshooting flow

- Lower `local_pref` on the winning path and confirm winner changes.
- Increase AS-path length on one path and verify tie-break behavior.

## Standards and references

- RFC 4271 path attribute model and decision process overview.
