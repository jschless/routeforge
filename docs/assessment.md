# Assessment and Scoring

RouteForge uses a weighted scoring model to evaluate student readiness against the CCNP curriculum covered in labs 01–39.

## How the Score Is Calculated

Each lab has a **weight** (1–5) in `labs/assessment_rubric.yaml`. Completing a lab earns full credit for that lab's weight. Partially-completed labs earn partial credit based on pass rate.

For each lab:

```
mastery = 1.0                          if lab is completed (routeforge run passed)
mastery = pass_count / run_count       if lab was run but not completed
mastery = 0.0                          if lab was never run
```

The overall score:

```
overall_score = 100 × (sum of weight × mastery across all labs) / (sum of all weights)
```

A lab is considered **completed** when `routeforge run <lab_id>` returns a passing result and that result is saved to your progress state file.

## Assessment Bands

| Band | Minimum Score | Meaning |
|---|---|---|
| BELOW_PASS | 0 | Score < 70; continue completing labs |
| PASS | 70 | Sufficient coverage for CCNP concepts |
| MERIT | 85 | Strong mastery across most domains |
| DISTINCTION | 95 | Excellent mastery, near-complete coverage |

Your band is reported by `routeforge report` as `assessment.band`.

## At-Risk Labs

`assessment.at_risk_labs` lists labs where:

- You ran the lab at least once (`run_count > 0`)
- The lab is not yet completed
- Your pass rate for that lab is below 70% (`mastery < 0.7`)

These are labs where repeated failures suggest a gap in understanding. The report shows up to 5 at-risk labs, sorted by lowest mastery first.

## `routeforge report` Output Explained

```
report.profile: ccnp_v1               # rubric profile identifier
report.as_of: 2026-03-07              # rubric publication date
labs.completed: 15/39                 # labs completed out of 39 total
labs.unlocked: lab16_...              # next labs you can run (prereqs met)
conformance.must: 8/12                # MUST-level features covered
conformance.should: 3/9               # SHOULD-level features covered
assessment.score: 42.31               # weighted score (0–100)
assessment.band: BELOW_PASS           # BELOW_PASS / PASS / MERIT / DISTINCTION
assessment.at_risk_labs: lab05 (...) # labs with low pass rate
assessment.remediation_docs: ...      # tutorial links for at-risk labs
assessment.next_step: routeforge ...  # suggested command to make progress
capstone.ready: no                    # yes when lab27 prereqs are met
```

## Conformance Coverage

The conformance matrix (`labs/conformance_matrix.yaml`) tracks which protocol features each lab covers:

- **MUST** features: core CCNP-required behaviors. Covering all MUST features is the primary goal.
- **SHOULD** features: important but not required for every deployment.
- **OUT** features: outside the current profile scope.

`conformance.must` shows how many MUST features you have at least partial coverage of.

## Improving Your Score

1. Run at-risk labs again after fixing your implementation: `routeforge check <lab_id>`
2. Then re-run the lab scenario to update progress: `routeforge run <lab_id> --state-file "$STATE"`
3. Complete uncompleted labs to advance your band.

A lab only counts as completed once `routeforge run` passes and is recorded in your progress state. `routeforge check` (which runs pytest) does not update the score — it is for local verification only.

## State File

Progress is saved in `~/.routeforge_progress.json` by default, or a custom path with `--state-file`. The state file tracks:

- Which labs are completed
- Run and pass counts per lab

Use `routeforge progress show` to inspect it and `routeforge progress reset` to start over.
