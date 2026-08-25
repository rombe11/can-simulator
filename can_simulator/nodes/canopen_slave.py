from __future__ import annotations

import can
from can_simulator.core.bus import CanBus
from can_simulator.core.node import Node, NodeState


class CANopenSlaveNode(Node, can.Listener):
    def __init__(self, name: str, bus: CanBus, node_id: int) -> None:
        super().__init__(name, bus)
        self.node_id: int = node_id
        self.cob_bootup: int = 0x700 + node_id
        self.cob_sdo_tx: int = 0x580 + node_id
        self.cob_sdo_rx: int = 0x600 + node_id
        self.cob_nmt: int = 0x000
        self.cob_feedback: int = 0x100 + node_id
        self.cob_rpdo1: int = 0x200 + node_id

    def init(self) -> None:
        self.bus.add_listener(self)
        self.sender.add_raw(
            "bootup",
            arbitration_id=self.cob_bootup,
            period_s=0.5,
            data=bytes([0x00])
        )
        self.sender.add_raw(
            "feedback",
            arbitration_id=self.cob_feedback,
            period_s=0.1,
            data=bytes([0x55, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        )

    def on_message_received(self, msg: can.Message) -> None:
        if msg.arbitration_id == self.cob_sdo_rx:
            self.bus.send_raw(
                arbitration_id=self.cob_sdo_tx,
                data=bytes([0x60, msg.data[1], msg.data[2], msg.data[3], 0x00, 0x00, 0x00, 0x00]),
                is_extended_id=False
            )
        elif msg.arbitration_id == self.cob_nmt:
            command: int = msg.data[0]
            target_node: int = msg.data[1]
            if target_node == 0 or target_node == self.node_id:
                if command == 0x01:
                    self.state = NodeState.OPERATIONAL
                elif command == 0x02:
                    self.state = NodeState.STOPPED
        elif msg.arbitration_id == self.cob_rpdo1:
            cmd_type: int = msg.data[0]
            if cmd_type == 0x01:
                self.sender.set_byte("feedback", index=1, value=0x01)
            elif cmd_type == 0x02:
                self.sender.set_byte("feedback", index=1, value=0x02)
            elif cmd_type == 0x03:
                self.sender.set_byte("feedback", index=1, value=0x00)

    def send_command_command(self, cmd_value: int) -> None:
        self.bus.send_raw(
            arbitration_id=self.cob_rpdo1,
            data=bytes([cmd_value, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
            is_extended_id=False
        )

    def stop(self) -> None:
        try:
            self.bus.remove_listener(self)
        except Exception:
            pass
        super().stop()