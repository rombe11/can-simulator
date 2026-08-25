from __future__ import annotations

import time
import can
from can_simulator.core.bus import CanBus
from can_simulator.core.node import Node


class CANopenMasterControllerNode(Node, can.Listener):
    def __init__(self, name: str, bus: CanBus, target_node_id: int = 0x1E) -> None:
        super().__init__(name, bus)
        self.target_node_id: int = target_node_id
        self.cob_sdo_rx: int = 0x600 + target_node_id
        self.cob_sdo_tx: int = 0x580 + target_node_id
        self.cob_nmt: int = 0x000
        self.cob_rpdo1: int = 0x200 + target_node_id
        self.cob_tpdo1: int = 0x180 + target_node_id
        self.cob_feedback: int = 0x180 + target_node_id
        self.bootup_received: bool = False
        self.last_feedback: bytes | None = None

    def init(self) -> None:
        self.bus.add_listener(self)

    def on_message_received(self, msg: can.Message) -> None:
        if msg.arbitration_id == (0x700 + self.target_node_id):
            self.bootup_received = True
        elif msg.arbitration_id == self.cob_feedback:
            self.last_feedback = msg.data

    def send_nmt_start(self) -> None:
        self.bus.send_raw(
            arbitration_id=self.cob_nmt,
            data=bytes([0x01, self.target_node_id]),
            is_extended_id=False
        )

    def send_nmt_stop(self) -> None:
        self.bus.send_raw(
            arbitration_id=self.cob_nmt,
            data=bytes([0x02, self.target_node_id]),
            is_extended_id=False
        )

    def send_nmt_reset(self) -> None:
        self.bus.send_raw(
            arbitration_id=self.cob_nmt,
            data=bytes([0x81, self.target_node_id]),
            is_extended_id=False
        )

    def send_sdo_config(self) -> None:
        self.bus.send_raw(
            arbitration_id=self.cob_sdo_rx,
            data=bytes([0x23, 0x16, 0x10, 0x01, 0xC8, 0x00, 0x01, 0x00]),
            is_extended_id=False
        )

    def send_run_out(self) -> None:
        self.bus.send_raw(
            arbitration_id=self.cob_rpdo1,
            data=bytes([0x01, 0xFB, 0xFB, 0xFB, 0xFB, 0x00, 0x00, 0x00]),
            is_extended_id=False
        )

    def send_run_in(self) -> None:
        self.bus.send_raw(
            arbitration_id=self.cob_rpdo1,
            data=bytes([0x02, 0xFB, 0xFB, 0xFB, 0xFB, 0x00, 0x00, 0x00]),
            is_extended_id=False
        )

    def send_stop_command(self) -> None:
        self.bus.send_raw(
            arbitration_id=self.cob_rpdo1,
            data=bytes([0x00, 0xFB, 0xFB, 0xFB, 0xFB, 0x00, 0x00, 0x00]),
            is_extended_id=False
        )

    def run_automatic_startup_sequence(self) -> None:
        while not self.bootup_received:
            time.sleep(0.05)

        time.sleep(0.2)
        self.send_sdo_config()

        time.sleep(0.3)
        self.send_nmt_start()

        time.sleep(0.5)
        self.send_stop_command()

    def stop(self) -> None:
        try:
            self.bus.remove_listener(self)
        except Exception:
            pass
        super().stop()