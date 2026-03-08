"""Trace replay and explain helpers for student workflows."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_trace(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def replay_lines(records: list[dict[str, Any]]) -> list[str]:
    lines: list[str] = []
    for record in sorted(records, key=lambda row: int(row.get("seq", 0))):
        checkpoints = ",".join(record.get("checkpoints", [])) or "none"
        lines.append(
            "seq={seq} step={step} action={action} reason={reason} checkpoints={checkpoints}".format(
                seq=record.get("seq", "?"),
                step=record.get("step", "?"),
                action=record.get("action", "?"),
                reason=record.get("reason", "?"),
                checkpoints=checkpoints,
            )
        )
    return lines


def explain_lines(records: list[dict[str, Any]], *, step: str | None = None) -> list[str]:
    if not records:
        return ["no trace records"]

    if step is None:
        actions: dict[str, int] = {}
        checkpoints: set[str] = set()
        for record in records:
            action = str(record.get("action", "UNKNOWN"))
            actions[action] = actions.get(action, 0) + 1
            checkpoints.update(record.get("checkpoints", []))

        action_summary = ", ".join(f"{name}:{count}" for name, count in sorted(actions.items()))
        checkpoint_summary = ", ".join(sorted(checkpoints)) if checkpoints else "none"
        return [
            f"records: {len(records)}",
            f"actions: {action_summary}",
            f"checkpoints: {checkpoint_summary}",
        ]

    matches = [record for record in records if record.get("step") == step]
    if not matches:
        return [f"step not found: {step}"]

    record = matches[0]
    egress = record.get("egress", [])
    egress_ports = ", ".join(str(item.get("interface")) for item in egress) if egress else "none"
    checkpoints = ", ".join(record.get("checkpoints", [])) or "none"
    lines = [
        f"step: {step}",
        f"action: {record.get('action', '?')}",
        f"reason: {record.get('reason', '?')}",
        f"ingress: {record.get('ingress_interface', '?')} vlan={record.get('ingress_vlan', '?')}",
        f"egress_ports: {egress_ports}",
        f"checkpoints: {checkpoints}",
    ]
    # Emit protocol-specific detail fields (OSPF state, BGP path attributes, L3
    # decisions, etc.) so students see context without writing a custom parser.
    if details := record.get("details"):
        for key, value in sorted(details.items()):
            lines.append(f"  {key}: {value}")
    return lines
