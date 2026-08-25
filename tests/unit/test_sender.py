from __future__ import annotations

import time
import pytest
from can_simulator.core.bus import CanBus
from can_simulator.core.sender import PeriodicSender


def test_when_periodic_sender_emits_raw_message_and_updates_byte_then_new_value_is_transmitted(virtual_bus: CanBus, bus_catcher) -> None:
    virtual_bus.add_listener(bus_catcher)

    sender = PeriodicSender("SenderTest", virtual_bus)
    sender.add_raw("test_msg", arbitration_id=0x500, period_s=0.02, data=bytes([1, 2, 3, 4, 5, 6, 7, 8]))
    sender.start()

    try:
        time.sleep(0.08)
        assert len(bus_catcher.received_messages) > 0
        assert bus_catcher.received_messages[-1].data[0] == 1

        sender.set_byte("test_msg", index=0, value=0xAB)
        
        time.sleep(0.08)
        
        updated_msgs = [m for m in bus_catcher.received_messages if m.data[0] == 0xAB]
        assert len(updated_msgs) > 0

    finally:
        sender.stop()
        virtual_bus.remove_listener(bus_catcher)


def test_when_sending_periodic_message_over_socketcan_then_frames_are_received_successfully(vcan_bus: CanBus, bus_catcher) -> None:
    vcan_bus.add_listener(bus_catcher)
    sender = PeriodicSender("VcanSender", vcan_bus)
    
    sender.add_raw("vcan_msg", arbitration_id=0x123, period_s=0.05, data=b"\x55\x66\x77\x88\x11\x22\x33\x44")
    sender.start()

    try:
        time.sleep(0.15)
        assert len(bus_catcher.received_messages) > 0
        assert bus_catcher.received_messages[-1].arbitration_id == 0x123
    finally:
        sender.stop()
        vcan_bus.remove_listener(bus_catcher)