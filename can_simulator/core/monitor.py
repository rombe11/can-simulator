from __future__ import annotations

import can


class BusMonitor(can.Listener):
    def __init__(self, name: str) -> None:
        super().__init__()
        self.name: str = name

    def on_message_received(self, msg: can.Message) -> None:
        if msg.is_extended_id:
            arb_id = f"0x{msg.arbitration_id:08X}"
        else:
            arb_id = f"0x{msg.arbitration_id:03X}"

        data_hex = " ".join(f"{b:02X}" for b in msg.data)

        print(
            f"[{self.name}] "
            # f"Time: {msg.timestamp:.4f} | "
            f"ID: {arb_id} | "
            f"DLC: {msg.dlc} | "
            f"Data: [{data_hex}]"
        )

    def on_error(self, exc: Exception) -> None:
        print(f"[{self.name}] Bus Error: {exc}")