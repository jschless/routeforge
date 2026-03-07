"""Deterministic tunnel and IPsec helpers for labs 25-27."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TunnelPacket:
    inner_src: str
    inner_dst: str
    outer_src: str
    outer_dst: str
    payload_id: str


def encapsulate(*, payload_id: str, inner_src: str, inner_dst: str, tunnel_src: str, tunnel_dst: str) -> TunnelPacket:
    return TunnelPacket(
        inner_src=inner_src,
        inner_dst=inner_dst,
        outer_src=tunnel_src,
        outer_dst=tunnel_dst,
        payload_id=payload_id,
    )


def decapsulate(packet: TunnelPacket) -> tuple[str, str, str]:
    return packet.payload_id, packet.inner_src, packet.inner_dst


def evaluate_ipsec_policy(*, destination_ip: str, protected_prefixes: tuple[str, ...]) -> str:
    # TODO(student): evaluate destination against protected prefixes.
    raise NotImplementedError("TODO: implement evaluate_ipsec_policy")


def lookup_sa(*, sa_db: dict[str, int], peer_ip: str) -> int | None:
    return sa_db.get(peer_ip)
