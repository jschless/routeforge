from __future__ import annotations

from routeforge.runtime.scheduler import DeterministicScheduler, ordering_key


def test_ordering_key_is_time_priority_sequence() -> None:
    assert ordering_key(10, 50, 3) == (10, 50, 3)


def test_scheduler_runs_in_deterministic_order() -> None:
    scheduler = DeterministicScheduler()
    seen: list[str] = []

    scheduler.schedule(sim_time_ms=10, priority=100, callback=lambda: seen.append("a"))
    scheduler.schedule(sim_time_ms=10, priority=50, callback=lambda: seen.append("b"))
    scheduler.schedule(sim_time_ms=5, priority=200, callback=lambda: seen.append("c"))
    scheduler.schedule(sim_time_ms=10, priority=50, callback=lambda: seen.append("d"))

    scheduler.run()

    assert seen == ["c", "b", "d", "a"]
    assert scheduler.now_ms == 10
