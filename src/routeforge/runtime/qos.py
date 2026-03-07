"""Minimal QoS remark and queue helpers."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class QosQueue:
    name: str
    packets: list[str] = field(default_factory=list)

    def enqueue(self, packet_id: str) -> None:
        self.packets.append(packet_id)

    def dequeue(self) -> str | None:
        if not self.packets:
            return None
        return self.packets.pop(0)


@dataclass
class QosEngine:
    high_queue: QosQueue = field(default_factory=lambda: QosQueue(name="high"))
    default_queue: QosQueue = field(default_factory=lambda: QosQueue(name="default"))

    def remark_dscp(self, *, traffic_class: str) -> int:
        if traffic_class == "voice":
            return 46
        if traffic_class == "video":
            return 34
        return 0

    def enqueue(self, *, packet_id: str, dscp: int) -> str:
        if dscp >= 40:
            self.high_queue.enqueue(packet_id)
            return self.high_queue.name
        self.default_queue.enqueue(packet_id)
        return self.default_queue.name

    def dequeue(self) -> tuple[str | None, str | None]:
        # TODO(student): dequeue with deterministic priority order.
        raise NotImplementedError("TODO: implement QosEngine.dequeue")
