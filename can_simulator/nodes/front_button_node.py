from __future__ import annotations

from can_simulator.core.bus import CanBus
from can_simulator.core.node import Node


class ButtonControllerNode(Node):
    def __init__(self, name: str, bus: CanBus) -> None:
        super().__init__(name, bus)

    def init(self) -> None:
        self.sender.add_raw(
            name="button_status",
            arbitration_id=0x0C22D890,
            period_s=0.1,
            data=bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
            is_extended_id=True
        )

    def trigger_reset(self, bit_index: int) -> None:
        val = (1 << bit_index) if bit_index in (0, 2) else 0
        self.sender.set_byte("button_status", index=7, value=val)