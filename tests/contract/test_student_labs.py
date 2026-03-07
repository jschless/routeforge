from __future__ import annotations

from ipaddress import IPv4Address

from routeforge.labs.exercises import run_student_lab
from routeforge.model.packet import is_valid_mac
from routeforge.student import lab01 as student_lab01


def test_student_lab01_fails_when_todos_not_implemented() -> None:
    result = run_student_lab("lab01_frame_and_headers")
    assert result.passed is False
    assert any("not implemented" in step.detail.lower() for step in result.steps)


def test_student_lab01_passes_when_student_functions_are_correct(monkeypatch) -> None:
    def _validate_ipv4(value: str) -> bool:
        try:
            IPv4Address(value)
            return True
        except ValueError:
            return False

    def _validate_ttl(value: int) -> bool:
        return value >= 1

    def _frame_should_parse(src_mac: str, dst_mac: str, src_ip: str, dst_ip: str, ttl: int) -> bool:
        return is_valid_mac(src_mac) and is_valid_mac(dst_mac) and _validate_ipv4(src_ip) and _validate_ipv4(dst_ip) and _validate_ttl(ttl)

    monkeypatch.setattr(student_lab01, "validate_mac", is_valid_mac)
    monkeypatch.setattr(student_lab01, "validate_ipv4", _validate_ipv4)
    monkeypatch.setattr(student_lab01, "validate_ttl", _validate_ttl)
    monkeypatch.setattr(student_lab01, "frame_should_parse", _frame_should_parse)

    result = run_student_lab("lab01_frame_and_headers")
    assert result.passed is True
    assert {"PARSE_OK", "PARSE_DROP"} <= set(result.checkpoints)
