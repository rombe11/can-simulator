from pathlib import Path
from can_simulator.core.bus import BusConfig, CanBus
from can_simulator.core.sender import PeriodicSender
from can_simulator.core.message import Message, Signal
import can

# Create a message definition
TEST_MSG = Message("TestMessage", arbitration_id=0x123, dlc=8)
TEST_MSG.add_signal(Signal("data", start_bit=0, length=16))

# Create and configure the bus
config = BusConfig(channel="test_channel", interface="virtual", bitrate=500_000)
bus = CanBus(config)

# Add a listener to print all messages
class MessagePrinter(can.Listener):
    def on_message_received(self, msg: can.Message) -> None:
        print(f"ID: 0x{msg.arbitration_id:X} | Data: {msg.data.hex()} | {msg}")

bus.add_listener(MessagePrinter())

# Send periodic messages
sender = PeriodicSender("test_sender", bus)
sender.add_message(TEST_MSG, period_s=1.0, data=42)
sender.start()

try:
    print("Bus running... Press Ctrl+C to stop")
    import time
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nStopping...")
    sender.stop()
    bus.shutdown()