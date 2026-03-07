"""Deterministic NAT44 session table for lab exercises."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class NatSession:
    inside_ip: str
    inside_port: int
    protocol: str
    outside_ip: str
    outside_port: int
    last_seen: int


@dataclass
class Nat44Table:
    public_ip: str
    _next_port: int = 10000
    sessions_by_inside: dict[tuple[str, int, str], NatSession] = field(default_factory=dict)
    sessions_by_outside: dict[tuple[int, str], NatSession] = field(default_factory=dict)

    def _allocate_port(self) -> int:
        port = self._next_port
        self._next_port += 1
        return port

    def outbound_translate(self, *, inside_ip: str, inside_port: int, protocol: str, now: int) -> NatSession:
        key = (inside_ip, inside_port, protocol)
        session = self.sessions_by_inside.get(key)
        if session is None:
            session = NatSession(
                inside_ip=inside_ip,
                inside_port=inside_port,
                protocol=protocol,
                outside_ip=self.public_ip,
                outside_port=self._allocate_port(),
                last_seen=now,
            )
        else:
            session = NatSession(
                inside_ip=session.inside_ip,
                inside_port=session.inside_port,
                protocol=session.protocol,
                outside_ip=session.outside_ip,
                outside_port=session.outside_port,
                last_seen=now,
            )
        self.sessions_by_inside[key] = session
        self.sessions_by_outside[(session.outside_port, session.protocol)] = session
        return session

    def inbound_translate(self, *, outside_port: int, protocol: str, now: int) -> NatSession | None:
        # TODO(student): perform inbound NAT session lookup and refresh.
        raise NotImplementedError("TODO: implement Nat44Table.inbound_translate")

    def expire(self, *, now: int, timeout: int) -> list[NatSession]:
        expired: list[NatSession] = []
        for key, session in list(self.sessions_by_inside.items()):
            if now - session.last_seen >= timeout:
                expired.append(session)
                del self.sessions_by_inside[key]
                self.sessions_by_outside.pop((session.outside_port, session.protocol), None)
        return expired
