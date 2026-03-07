"""Interface and VLAN admission helpers."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Interface:
    name: str
    mode: str = "access"
    access_vlan: int = 1
    native_vlan: int = 1
    allowed_vlans: set[int] = field(default_factory=lambda: {1})
    admin_up: bool = True

    def ingress_vlan(self, incoming_vlan: int | None) -> tuple[int | None, str | None]:
        if not self.admin_up:
            return None, "L2_PORT_DOWN"

        if self.mode == "access":
            if incoming_vlan is not None:
                return None, "L2_TAGGED_ON_ACCESS"
            return self.access_vlan, None

        if self.mode == "trunk":
            vlan = incoming_vlan if incoming_vlan is not None else self.native_vlan
            if vlan not in self.allowed_vlans:
                return None, "L2_VLAN_NOT_ALLOWED"
            return vlan, None

        return None, "L2_INVALID_PORT_MODE"

    def egress_vlan(self, vlan: int) -> tuple[int | None, bool]:
        """Return outgoing VLAN tag and whether the frame can egress."""

        if not self.admin_up:
            return None, False

        if self.mode == "access":
            if vlan != self.access_vlan:
                return None, False
            return None, True

        if self.mode == "trunk":
            if vlan not in self.allowed_vlans:
                return None, False
            if vlan == self.native_vlan:
                return None, True
            return vlan, True

        return None, False
