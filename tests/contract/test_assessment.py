from __future__ import annotations

from routeforge.labs.assessment import evaluate_assessment, load_assessment_rubric
from routeforge.labs.manifest import LABS
from routeforge.labs.progress import ProgressState, clear_progress, mark_completed


def test_rubric_loads_and_covers_all_labs() -> None:
    rubric = load_assessment_rubric()
    assert rubric.profile == "ccnp_v1"
    assert len(rubric.labs) == len(LABS)
    assert sum(lab.weight for lab in rubric.labs.values()) == 100


def test_assessment_empty_and_full_progress() -> None:
    rubric = load_assessment_rubric()

    empty = evaluate_assessment(clear_progress(), rubric)
    assert empty.overall_score == 0.0
    assert empty.band == "BELOW_PASS"
    assert empty.total_weight == 100

    state = clear_progress()
    for entry in LABS:
        state = mark_completed(state, entry["id"])
    full = evaluate_assessment(state, rubric)
    assert full.overall_score == 100.0
    assert full.band == "DISTINCTION"


def test_assessment_marks_at_risk_attempted_labs() -> None:
    rubric = load_assessment_rubric()
    state = ProgressState(
        version=1,
        completed=(),
        run_counts={"lab01_frame_and_headers": 5},
        pass_counts={"lab01_frame_and_headers": 1},
        last_result={"lab01_frame_and_headers": "FAIL"},
    )
    result = evaluate_assessment(state, rubric)
    assert "lab01_frame_and_headers" in result.at_risk_labs
