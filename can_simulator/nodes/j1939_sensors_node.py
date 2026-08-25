from __future__ import annotations

from can_simulator.core.bus import CanBus
from can_simulator.core.node import Node, NodeState


class J1939SensorNode(Node):
    def __init__(self, name: str, bus: CanBus) -> None:
        super().__init__(name, bus)

    def init(self) -> None:
        self.sender.add_raw(
            name="sensor_1",
            arbitration_id=0x0CFF9101,
            period_s=0.5,
            data=bytes([0x50, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]),
            is_extended_id=True,
        )

        self.sender.add_raw(
            name="sensor_2",
            arbitration_id=0x0CFF9102,
            period_s=0.5,
            data=bytes([0x00, 0x00, 0x12, 0x34, 0xFF, 0xFF, 0xFF, 0xFF]),
            is_extended_id=True,
        )

        self.sender.add_raw(
            name="sensor_3",
            arbitration_id=0x0CFF9103,
            period_s=0.5,
            data=bytes([0x45, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]),
            is_extended_id=True,
        )

        self.sender.add_raw(
            name="sensor_4",
            arbitration_id=0x0CFF9104,
            period_s=0.5,
            data=bytes([0x00, 0x64, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]),
            is_extended_id=True,
        )

        self.sender.add_raw(
            name="alt_manufacturer_sensor",
            arbitration_id=0x18FEF320,
            period_s=0.2,
            data=bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
            is_extended_id=True,
        )

        self.sender.add_raw(
            name="gas_analyzer_sensor",
            arbitration_id=0x18FEF430,
            period_s=0.25,
            data=bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
            is_extended_id=True,
        )

    def update_sensor_value(self, sensor_name: str, index: int, value: int) -> None:
        self.sender.set_byte(sensor_name, index=index, value=value)