"""ACL policy evaluation helpers."""

from __future__ import annotations

from dataclasses import dataclass
from ipaddress import IPv4Address, IPv4Network


@dataclass(frozen=True)
class AclRule:
    action: str
    src_prefix: str
    src_prefix_len: int

    @property
    def network(self) -> IPv4Network:
        return IPv4Network(f"{self.src_prefix}/{self.src_prefix_len}", strict=False)


def evaluate_acl(*, rules: list[AclRule], src_ip: str) -> str:
    ip = IPv4Address(src_ip)
    for rule in rules:
        if ip in rule.network:
            return rule.action.lower()
    return "deny"
