from __future__ import annotations

from can_simulator.core.bus import CanBus
from can_simulator.core.node import Node


class GenericSensorNode(Node):
    def __init__(
        self,
        name: str,
        bus: CanBus,
        arbitration_id: int,
        period_s: float,
        initial_data: bytes,
        is_extended_id: bool = True,
    ) -> None:
        super().__init__(name, bus)
        self.arbitration_id = arbitration_id
        self.period_s = period_s
        self.initial_data = initial_data
        self.is_extended_id = is_extended_id

    def init(self) -> None:
        self.sender.add_raw(
            name=self.name,
            arbitration_id=self.arbitration_id,
            period_s=self.period_s,
            data=self.initial_data,
            is_extended_id=self.is_extended_id,
        )

    def update_value(self, index: int, value: int) -> None:
        self.sender.set_byte(self.name, index=index, value=value)