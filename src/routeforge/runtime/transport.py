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
    # TODO(student): normalize protocol and build a deterministic flow key.
    raise NotImplementedError("TODO: implement classify_flow")


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


def classify_transport_protocol(*, protocol: str) -> str:
    """Classify a transport protocol as STATEFUL or STATELESS.

    Classification (compare after uppercasing ``protocol``):

    - ``"TCP"`` → ``"STATEFUL"``  — connection-oriented; the OS tracks sequence
      numbers, window sizes, and teardown state per flow.
    - ``"UDP"`` → ``"STATELESS"`` — connectionless; each datagram is independent
      and no session state is maintained.
    - ``"ICMP"`` → ``"STATELESS"`` — control messages; no transport-layer session.
    - Any other protocol → ``"STATELESS"`` (safe default).

    This classification determines whether a stateful firewall or NAT device
    must maintain per-flow state entries for the protocol.

    See ``docs/tutorial/lab16_udp_tcp_fundamentals.md`` for the walkthrough.

    # TODO(student): implement classify_transport_protocol.
    """
    raise NotImplementedError("TODO: implement classify_transport_protocol")
