"""Minimal deterministic BFD session model."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BfdSession:
    detect_mult: int = 3
    state: str = "DOWN"
    missed_intervals: int = 0

    def receive_control(self) -> str:
        self.missed_intervals = 0
        if self.state != "UP":
            self.state = "UP"
        return self.state

    def tick(self, *, control_received: bool) -> str:
        # TODO(student): handle BFD receive vs timeout interval transitions.
        raise NotImplementedError("TODO: implement BfdSession.tick")
