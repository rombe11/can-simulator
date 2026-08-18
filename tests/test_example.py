from __future__ import annotations

from typing import Dict

import can

from can_simulator.core.bus import CanBus
from can_simulator.core.message import Message, MessageDB, Signal
from can_simulator.core.sender import PeriodicSender
from can_simulator.testing.client import CanTestClient

REQUEST = Message("SpeedRequest", arbitration_id=0x100, dlc=2)
REQUEST.add_signal(Signal("target_speed", start_bit=0, length=16))

RESPONSE = Message("SpeedStatus", arbitration_id=0x101, dlc=2)
RESPONSE.add_signal(Signal("current_speed", start_bit=0, length=16))

DB = MessageDB([REQUEST, RESPONSE])


class _EchoResponder(can.Listener):
    def __init__(self, bus: CanBus) -> None:
        self._bus: CanBus = bus

    def on_message_received(self, msg: can.Message) -> None:
        if msg.arbitration_id != REQUEST.arbitration_id:
            return
        values: Dict[str, float] = REQUEST.decode(bytes(msg.data))
        data = RESPONSE.encode({"current_speed": values["target_speed"]})
        self._bus.send_raw(RESPONSE.arbitration_id, data)


def test_send_periodic_and_check_response(bus: CanBus) -> None:
    bus.add_listener(_EchoResponder(bus))

    sender = PeriodicSender("stimulus", bus)
    sender.add_message(REQUEST, period_s=0.05, target_speed=0)
    sender.start()

    client = CanTestClient(bus, DB)
    client.drain()

    sender.set_values("SpeedRequest", target_speed=120)
    status = client.expect("SpeedStatus", timeout=1.0, current_speed=120)
    assert status["current_speed"] == 120

    sender.stop()
    client.close()


def test_two_lines_in_parallel(real_buses: Dict[str, CanBus]) -> None:
    line1 = real_buses["line1"]
    line2 = real_buses["line2"]

    line1.add_listener(_EchoResponder(line1))
    line2.add_listener(_EchoResponder(line2))

    sender1 = PeriodicSender("s1", line1)
    sender1.add_message(REQUEST, period_s=0.05, target_speed=10)
    sender1.start()

    sender2 = PeriodicSender("s2", line2)
    sender2.add_message(REQUEST, period_s=0.05, target_speed=99)
    sender2.start()

    client1 = CanTestClient(line1, DB)
    client2 = CanTestClient(line2, DB)
    client1.drain()
    client2.drain()

    status1 = client1.expect("SpeedStatus", timeout=1.0, current_speed=10)
    status2 = client2.expect("SpeedStatus", timeout=1.0, current_speed=99)

    assert status1["current_speed"] == 10
    assert status2["current_speed"] == 99

    sender1.stop()
    sender2.stop()
    client1.close()
    client2.close()
