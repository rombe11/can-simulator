from __future__ import annotations

import pytest
import can
from can_simulator.core.bus import BusConfig, CanBus


class BusMessageCatcher(can.Listener):
    def __init__(self) -> None:
        super().__init__()
        self.received_messages: list[can.Message] = []

    def on_message_received(self, msg: can.Message) -> None:
        self.received_messages.append(msg)


@pytest.fixture
def vcan_bus() -> CanBus:
    config = BusConfig(
        channel="vcan0",
        interface="socketcan",
        bitrate=500_000,
        receive_own_messages=True,
    )
    try:
        bus = CanBus(config)
    except Exception as e:
        pytest.skip(f"SocketCAN interface vcan0 not available: {e}")
        
    yield bus
    bus.shutdown()


@pytest.fixture
def mock_bus() -> CanBus:
    config = BusConfig(channel="test_node_bus", interface="virtual")
    bus = CanBus(config)
    yield bus
    bus.shutdown()


@pytest.fixture
def virtual_bus() -> CanBus:
    config = BusConfig(channel="test_sender_bus", interface="virtual", receive_own_messages=True)
    bus = CanBus(config)
    yield bus
    bus.shutdown()


@pytest.fixture
def bus_catcher() -> BusMessageCatcher:
    return BusMessageCatcher()