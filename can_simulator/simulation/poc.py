import time

from can_simulator.core.bus import BusConfig, CanBus
from can_simulator.core.monitor import PCANStyleMonitor
from can_simulator.core.sender import PeriodicSender


def main() -> None:
    can0 = CanBus(
        BusConfig(
            channel="CAN0",
            interface="virtual",
            bitrate=500_000,
            receive_own_messages=True,
        )
    )

    can1 = CanBus(
        BusConfig(
            channel="CAN1",
            interface="virtual",
            bitrate=500_000,
            receive_own_messages=True,
        )
    )

    monitor = PCANStyleMonitor("GLOBAL_MONITOR", update_interval=0.1)
    
    can0.add_listener(monitor)
    can1.add_listener(monitor)

    sender0 = PeriodicSender("Sender_CAN0", can0)
    sender1 = PeriodicSender("Sender_CAN1", can1)

    sender0.add_raw("status_node1", arbitration_id=0x100, period_s=0.1, data=b"\x01\x02\x03\x04\x05\x06\x07\x08")
    sender0.add_raw("status_node2", arbitration_id=0x200, period_s=0.5, data=b"\x10\x20\x30\x40\x50\x60\x70\x80")

    sender1.add_raw("status_node3", arbitration_id=0x300, period_s=0.2, data=b"\xAA\xBB\xCC\xDD\xEE\xFF\x00\x11")
    sender1.add_raw("status_node4", arbitration_id=0x400, period_s=1.0, data=b"\x11\x22\x33\x44\x55\x66\x77\x88")

    sender0.start()
    sender1.start()

    print("CAN simulator running (Unified PCAN Style Monitor with Periodic Dynamic Updates)")
    print("Press Ctrl+C to stop")

    counter = 0

    try:
        while True:
            time.sleep(2.0)
            counter = (counter + 1) % 256

            sender0.set_byte("status_node1", index=0, value=counter)
            sender0.set_byte("status_node2", index=1, value=(counter * 2) % 256)
            sender1.set_byte("status_node3", index=7, value=255 - counter)

    except KeyboardInterrupt:
        print("\nStopping simulation gracefully...")

    finally:
        sender0.stop()
        sender1.stop()

        for bus in [can0, can1]:
            try:
                bus.shutdown()
            except Exception:
                pass
        
        print("Simulator stopped successfully.")


if __name__ == "__main__":
    main()