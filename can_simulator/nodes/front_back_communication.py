from __future__ import annotations

import can
from can_simulator.core.bus import CanBus
from can_simulator.core.node import Node


class SystemFrontGatewayNode(Node, can.Listener):
    def __init__(self, name: str, bus: CanBus) -> None:
        super().__init__(name, bus)

    def init(self) -> None:
        self.bus.add_listener(self)
        self.sender.add_raw(
            "to_back_diagnostic",
            arbitration_id=0x510,
            period_s=0.2,
            data=bytes([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        )

    def on_message_received(self, msg: can.Message) -> None:
        if msg.arbitration_id in (0x500, 0x501):
            pass
        elif msg.arbitration_id == 0x100:
            pass

    def send_alarm(self, alarm_code: int) -> None:
        self.bus.send_raw(
            arbitration_id=0x100,
            data=bytes([alarm_code, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
            is_extended_id=False
        )