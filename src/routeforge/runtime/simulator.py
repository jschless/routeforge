"""Shared simulation clock and scheduler bundle."""

from __future__ import annotations

from dataclasses import dataclass

from routeforge.runtime.scheduler import DeterministicScheduler


@dataclass
class SimulationClock:
    now_ms: int = 0


@dataclass
class SimulationRuntime:
    clock: SimulationClock
    scheduler: DeterministicScheduler

    @classmethod
    def create(cls, start_time_ms: int = 0) -> SimulationRuntime:
        clock = SimulationClock(now_ms=start_time_ms)
        scheduler = DeterministicScheduler(start_time_ms=start_time_ms)
        return cls(clock=clock, scheduler=scheduler)

    def sync_clock(self) -> None:
        self.clock.now_ms = self.scheduler.now_ms
