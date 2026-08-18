from __future__ import annotations

import can

from can_simulator.core.bus import CanBus
from can_simulator.core.sender import PeriodicSender
from can_simulator.testing.client import CanTestClient

STATUS_ID = 0x201
TRIGGER_ID = 0x100
EMCY_ID = 0x081


class _FaultResponder(can.Listener):
    def __init__(self, bus: CanBus, sender: PeriodicSender) -> None:
        self._bus: CanBus = bus
        self._sender: PeriodicSender = sender
        self._fault_sent: bool = False

    def on_message_received(self, msg: can.Message) -> None:
        if msg.arbitration_id != TRIGGER_ID:
            return
        if msg.data[0] != 1:
            return
        self._sender.set_byte("status", 2, 0xFF)
        if not self._fault_sent:
            self._bus.send_raw(EMCY_ID, bytes([0x10, 0x23, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))
            self._fault_sent = True


def test_byte_change_in_existing_message(bus: CanBus) -> None:
    sender = PeriodicSender("stimulus", bus)
    sender.add_raw("status", arbitration_id=STATUS_ID, period_s=0.05, data=bytes(8))
    sender.start()
    bus.add_listener(_FaultResponder(bus, sender))

    client = CanTestClient(bus)
    client.drain()
    client.send_bytes(TRIGGER_ID, bytes([1, 0, 0, 0, 0, 0, 0, 0]))

    frame = client.expect_byte(STATUS_ID, byte_index=2, value=0xFF, timeout=1.0)
    assert frame.data[2] == 0xFF

    sender.stop()
    client.close()


def test_new_message_appears_on_trigger(bus: CanBus) -> None:
    sender = PeriodicSender("stimulus", bus)
    sender.add_raw("status", arbitration_id=STATUS_ID, period_s=0.05, data=bytes(8))
    sender.start()
    bus.add_listener(_FaultResponder(bus, sender))

    client = CanTestClient(bus)
    baseline = client.observed_ids(window_s=0.3)
    assert EMCY_ID not in baseline

    client.send_bytes(TRIGGER_ID, bytes([1, 0, 0, 0, 0, 0, 0, 0]))
    frame = client.expect_new_id(known_ids=baseline | {TRIGGER_ID}, timeout=1.0)

    assert frame.arbitration_id == EMCY_ID
    assert frame.data[0] == 0x10
    assert frame.data[1] == 0x23

    sender.stop()
    client.close()
