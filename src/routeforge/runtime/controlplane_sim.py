"""Control-plane simulation scaffold."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ControlplaneSim:
    """Minimal inbox for future protocol state machines."""

    applied_messages: list[dict[str, Any]] = field(default_factory=list)

    def apply_message(self, message: dict[str, Any]) -> None:
        self.applied_messages.append(message)
