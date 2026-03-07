"""Deterministic scheduler queue for both simulation domains."""

from __future__ import annotations

from dataclasses import dataclass, field
from heapq import heappop, heappush
from typing import Any, Callable


def ordering_key(sim_time_ms: int, priority: int, sequence: int) -> tuple[int, int, int]:
    return (sim_time_ms, priority, sequence)


@dataclass(order=True)
class ScheduledTask:
    sim_time_ms: int
    priority: int
    sequence: int
    callback: Callable[[], Any] = field(compare=False)
    label: str = field(default="", compare=False)


class DeterministicScheduler:
    """Single-threaded deterministic task scheduler."""

    def __init__(self, start_time_ms: int = 0) -> None:
        self.now_ms = start_time_ms
        self._sequence = 0
        self._queue: list[ScheduledTask] = []

    def schedule(
        self,
        *,
        sim_time_ms: int,
        priority: int,
        callback: Callable[[], Any],
        label: str = "",
    ) -> ScheduledTask:
        task = ScheduledTask(
            sim_time_ms=sim_time_ms,
            priority=priority,
            sequence=self._sequence,
            callback=callback,
            label=label,
        )
        self._sequence += 1
        heappush(self._queue, task)
        return task

    def pop_next(self) -> ScheduledTask | None:
        if not self._queue:
            return None
        task = heappop(self._queue)
        if task.sim_time_ms > self.now_ms:
            self.now_ms = task.sim_time_ms
        return task

    def run_next(self) -> ScheduledTask | None:
        task = self.pop_next()
        if task is None:
            return None
        task.callback()
        return task

    def run(self) -> list[ScheduledTask]:
        executed: list[ScheduledTask] = []
        while True:
            task = self.run_next()
            if task is None:
                return executed
            executed.append(task)

    @property
    def pending(self) -> int:
        return len(self._queue)
