from __future__ import annotations

import csv
import itertools
from pathlib import Path
from typing import Dict, Iterator, List

import pytest

from can_simulator.core.bus import BusConfig, BusManager, CanBus
from can_simulator.core.config import load_bus_configs

_channel_counter = itertools.count()
_results: List[Dict[str, str]] = []


@pytest.fixture
def bus_manager() -> Iterator[BusManager]:
    manager = BusManager()
    yield manager
    manager.shutdown_all()


@pytest.fixture
def bus(bus_manager: BusManager) -> CanBus:
    channel = f"test_channel_{next(_channel_counter)}"
    config = BusConfig(channel=channel, interface="virtual", bitrate=500_000)
    return bus_manager.create_bus("line1", config)


@pytest.fixture
def real_buses(bus_manager: BusManager) -> Dict[str, CanBus]:
    configs = load_bus_configs(Path(__file__).parent.parent / "config" / "buses.yaml")
    return {name: bus_manager.create_bus(name, config) for name, config in configs.items()}


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call":
        _results.append({
            "test": item.nodeid,
            "result": "PASS" if report.passed else "FAIL",
            "duration_s": f"{report.duration:.3f}",
        })


def pytest_sessionfinish(session, exitstatus) -> None:
    output_path = Path(__file__).parent.parent / "test_results.csv"
    with output_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["test", "result", "duration_s"])
        writer.writeheader()
        writer.writerows(_results)
