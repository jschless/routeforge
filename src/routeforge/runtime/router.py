"""Minimal router state for early L2 labs."""

from __future__ import annotations

from dataclasses import dataclass, field

from routeforge.runtime.interface import Interface


@dataclass
class Router:
    node_id: str
    interfaces: dict[str, Interface] = field(default_factory=dict)
    mac_table: dict[int, dict[str, str]] = field(default_factory=dict)

    def add_interface(self, interface: Interface) -> None:
        self.interfaces[interface.name] = interface

    def get_interface(self, name: str) -> Interface | None:
        return self.interfaces.get(name)

    def learn_mac(self, *, vlan: int, mac: str, interface_name: str) -> None:
        table = self.mac_table.setdefault(vlan, {})
        table[mac] = interface_name

    def lookup_mac(self, *, vlan: int, mac: str) -> str | None:
        return self.mac_table.get(vlan, {}).get(mac)

    def forwarding_ports(self, *, vlan: int, ingress_interface: str) -> list[str]:
        ports: list[str] = []
        for name, interface in self.interfaces.items():
            if name == ingress_interface:
                continue
            _, allowed = interface.egress_vlan(vlan)
            if allowed:
                ports.append(name)
        return sorted(ports)
