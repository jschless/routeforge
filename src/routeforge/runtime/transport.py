"""Deterministic transport-layer helpers for labs 16-17."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class FlowKey:
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: str


def classify_flow(*, src_ip: str, dst_ip: str, src_port: int, dst_port: int, protocol: str) -> FlowKey:
    return FlowKey(
        src_ip=src_ip,
        dst_ip=dst_ip,
        src_port=src_port,
        dst_port=dst_port,
        protocol=protocol.upper(),
    )


@dataclass
class TcpFsm:
    state: str = "CLOSED"
    history: list[str] = field(default_factory=lambda: ["CLOSED"])

    def on_event(self, event: str) -> str:
        event = event.upper()
        if self.state == "CLOSED" and event == "ACTIVE_OPEN":
            self.state = "SYN_SENT"
        elif self.state == "SYN_SENT" and event == "SYN_ACK_RX":
            self.state = "ESTABLISHED"
        elif self.state == "ESTABLISHED" and event == "FIN_RX":
            self.state = "CLOSE_WAIT"
        elif self.state == "CLOSE_WAIT" and event == "APP_CLOSE":
            self.state = "LAST_ACK"
        elif self.state == "LAST_ACK" and event == "ACK_RX":
            self.state = "CLOSED"
        self.history.append(self.state)
        return self.state


def validate_udp(*, length_bytes: int, checksum_valid: bool) -> bool:
    # TODO(student): validate UDP minimum header length and checksum.
    raise NotImplementedError("TODO: implement validate_udp")
