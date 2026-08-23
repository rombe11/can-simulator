from __future__ import annotations

import can
from can_simulator.core.bus import CanBus
from can_simulator.core.node import Node, NodeState


class CANopenSlaveNode(Node, can.Listener):
    def __init__(self, name: str, bus: CanBus, node_id: int = 0x20) -> None:
        super().__init__(name, bus)
        self.node_id: int = node_id
        self.cob_bootup: int = 0x700 + node_id
        self.cob_sdo_tx: int = 0x580 + node_id
        self.cob_sdo_rx: int = 0x600 + node_id
        self.cob_nmt: int = 0x000
        self.cob_tpdo1: int = 0x180 + node_id
        self.cob_rpdo1: int = 0x200 + node_id

    def init(self) -> None:
        self.bus.add_listener(self)

        self.sender.add_raw(
            "bootup",
            arbitration_id=self.cob_bootup,
            period_s=0.1,
            data=bytes([0x00])
        )

        self.sender.add_raw(
            "tpdo1",
            arbitration_id=self.cob_tpdo1,
            period_s=0.05,
            data=bytes([0x00, 0x00, 0x00, 0x81, 0x00, 0x00, 0x00, 0xC0])
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
            if cmd_type == 0x00:
                self.sender.set_bytes("tpdo1", b"\x00\x00\x00\x81\x00\x00\x00\xC0")
            elif cmd_type == 0x01:
                self.sender.set_bytes("tpdo1", b"\x1A\x00\x06\x88\x00\x31\x00\xC0")
            elif cmd_type == 0x02:
                self.sender.set_bytes("tpdo1", b"\x60\x00\x06\x90\x00\x32\x00\xC0")

    def stop(self) -> None:
        try:
            self.bus.remove_listener(self)
        except Exception:
            pass
        super().stop()