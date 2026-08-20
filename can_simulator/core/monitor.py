from __future__ import annotations

import can
import time


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


class PCANStyleMonitor(can.Listener):
    def __init__(self, name: str, update_interval: float = 0.1) -> None:
        super().__init__()
        self.name: str = name
        self.messages: dict[int, dict] = {}
        self.update_interval = update_interval
        self.last_update_time = 0.0

    def on_message_received(self, msg: can.Message) -> None:
        arb_id = msg.arbitration_id
        
        if arb_id in self.messages:
            self.messages[arb_id]["count"] += 1
            self.messages[arb_id]["msg"] = msg
        else:
            self.messages[arb_id] = {
                "count": 1,
                "msg": msg,
            }

        current_time = time.time()
        if current_time - self.last_update_time >= self.update_interval:
            self.last_update_time = current_time
            self.refresh_display()

    def refresh_display(self) -> None:
        output = [f"\n--- [{self.name}] CAN Bus Simulator Monitor (PCAN Style) ---"]
        output.append(f"{'Channel':<10} | {'ID':<10} | {'Count':<8} | {'DLC':<4} | {'Data'}")
        output.append("-" * 58)

        for arb_id in sorted(self.messages.keys()):
            item = self.messages[arb_id]
            msg = item["msg"]
            count = item["count"]

            channel_str = str(getattr(msg, "channel", self.name))

            if msg.is_extended_id:
                id_str = f"0x{arb_id:08X}"
            else:
                id_str = f"0x{arb_id:03X}"

            data_hex = " ".join(f"{b:02X}" for b in msg.data)
            
            output.append(f"{channel_str:<10} | {id_str:<10} | {count:<8} | {msg.dlc:<4} | [{data_hex}]")

        print("\033[H\033[J", end="")
        print("\n".join(output))

    def on_error(self, exc: Exception) -> None:
        print(f"\n[{self.name}] Bus Error: {exc}")