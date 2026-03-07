from __future__ import annotations

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--stage-max",
        action="store",
        default=None,
        help="Run tests with stage marker <= this value.",
    )


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "stage(n): stage gate for student progression")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    raw = config.getoption("--stage-max")
    if raw is None:
        return
    stage_max = int(raw)

    selected: list[pytest.Item] = []
    deselected: list[pytest.Item] = []
    for item in items:
        marker = item.get_closest_marker("stage")
        if marker is None:
            selected.append(item)
            continue
        if not marker.args or not isinstance(marker.args[0], int):
            selected.append(item)
            continue
        stage = marker.args[0]
        if stage <= stage_max:
            selected.append(item)
        else:
            deselected.append(item)

    if deselected:
        config.hook.pytest_deselected(items=deselected)
    items[:] = selected
