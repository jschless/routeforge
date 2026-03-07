from __future__ import annotations

from routeforge.labs.exercises import LAB_RUNNERS, run_lab


def test_all_lab_runs_are_deterministic_across_repeated_execution() -> None:
    for lab_id in sorted(LAB_RUNNERS):
        first = run_lab(lab_id)
        second = run_lab(lab_id)
        assert first.passed is True
        assert second.passed is True
        assert first.steps == second.steps
        assert first.checkpoints == second.checkpoints
        assert first.trace_records == second.trace_records


def test_trace_records_have_stable_sequence_and_step_alignment() -> None:
    for lab_id in sorted(LAB_RUNNERS):
        result = run_lab(lab_id)
        expected_steps = [step.name for step in result.steps]
        observed_steps = [record["step"] for record in result.trace_records]
        observed_sequence = [record["seq"] for record in result.trace_records]

        assert observed_steps == expected_steps
        assert observed_sequence == list(range(1, len(result.trace_records) + 1))
