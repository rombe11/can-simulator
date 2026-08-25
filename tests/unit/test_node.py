from __future__ import annotations

import pytest
from can_simulator.nodes.dumb_node import DumbNode
from can_simulator.core.bus import CanBus


def test_when_starting_node_before_initialization_then_runtime_error_is_raised(mock_bus: CanBus) -> None:
    node = DumbNode(
        name="TEST_NODE",
        bus=mock_bus,
        arbitration_id=0x150,
        period_s=0.1,
        data=bytearray(b"\x01\x02\x03\x04\x05\x06\x07\x08"),
    )

    with pytest.raises(RuntimeError):
        node.start()


def test_when_initializing_and_starting_node_then_operational_state_succeeds(mock_bus: CanBus) -> None:
    node = DumbNode(
        name="TEST_NODE",
        bus=mock_bus,
        arbitration_id=0x150,
        period_s=0.1,
        data=bytearray(b"\x01\x02\x03\x04\x05\x06\x07\x08"),
    )

    node.initialize()
    node.start()
    
    assert node.state.value == "operational"
    
    node.stop()
    assert node.state.value == "stopped"