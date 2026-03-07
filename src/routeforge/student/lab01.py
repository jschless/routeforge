"""Student implementation surface for Lab 1.

Edit only this file for `routeforge run lab01_frame_and_headers --student`.
"""

from __future__ import annotations


def validate_mac(mac: str) -> bool:
    """Return True for valid colon-delimited lowercase/uppercase hex MAC addresses."""
    raise NotImplementedError("implement validate_mac")


def validate_ipv4(ip: str) -> bool:
    """Return True for syntactically valid IPv4 addresses."""
    raise NotImplementedError("implement validate_ipv4")


def validate_ttl(ttl: int) -> bool:
    """Return True when TTL is valid for forwarding (>= 1)."""
    raise NotImplementedError("implement validate_ttl")


def frame_should_parse(src_mac: str, dst_mac: str, src_ip: str, dst_ip: str, ttl: int) -> bool:
    """Return True only when MAC/IP/TTL validation should allow parsing to continue."""
    raise NotImplementedError("implement frame_should_parse")
