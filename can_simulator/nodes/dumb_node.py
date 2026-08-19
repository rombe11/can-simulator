from __future__ import annotations

from ..core.node import Node
from ..core.message import Message


class DumbNode(Node):
    def __init__(
        self,
        name: str,
        bus,
        arbitration_id: int,
        period_s: float,
        data: bytes,
    ) -> None:
        super().__init__(name, bus)

        self.arbitration_id = arbitration_id
        self.period_s = period_s
        self.data = data

    def init(self) -> None:
        message = Message(
            name=f"{self.name}_message",
            arbitration_id=self.arbitration_id,
            dlc=len(self.data),
        )

        self.sender.add_raw(
            name=message.name,
            arbitration_id=self.arbitration_id,
            period_s=self.period_s,
            data=self.data,
        )