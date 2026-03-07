from __future__ import annotations

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--tdl-target",
        action="store",
        default=None,
        help="Run tests marked for one TDL challenge id.",
    )


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "tdl(challenge_id): TDL challenge test marker")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    raw = config.getoption("--tdl-target")
    if raw is None:
        return

    target = str(raw).strip()
    if not target or target.lower() == "all":
        return

    selected: list[pytest.Item] = []
    deselected: list[pytest.Item] = []
    for item in items:
        marker = item.get_closest_marker("tdl")
        if marker is None or not marker.args or not isinstance(marker.args[0], str):
            deselected.append(item)
            continue
        if marker.args[0] == target:
            selected.append(item)
        else:
            deselected.append(item)

    if deselected:
        config.hook.pytest_deselected(items=deselected)
    items[:] = selected
