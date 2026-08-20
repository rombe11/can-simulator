import time

from can_simulator.core.bus import BusConfig, CanBus
from can_simulator.core.monitor import BusMonitor, PCANStyleMonitor
from can_simulator.nodes.dumb_node import DumbNode


def main() -> None:
    can0 = CanBus(
        BusConfig(
            channel="poc_can0",
            interface="virtual",
            bitrate=500_000,
            receive_own_messages=True,
        )
    )

    can1 = CanBus(
        BusConfig(
            channel="poc_can1",
            interface="virtual",
            bitrate=500_000,
            receive_own_messages=True,
        )
    )

    monitor = PCANStyleMonitor("GLOBAL_MONITOR", update_interval=0.1)
    
    can0.add_listener(monitor)
    can1.add_listener(monitor)
    
    node1 = DumbNode(
        name="NODE_1",
        bus=can0,
        arbitration_id=0x100,
        period_s=0.1,
        data=bytearray(b"\x01\x02\x03\x04\x05\x06\x07\x08"),
    )

    node2 = DumbNode(
        name="NODE_2",
        bus=can0,
        arbitration_id=0x200,
        period_s=0.5,
        data=bytearray(b"\x10\x20\x30\x40\x50\x60\x70\x80"),
    )

    node3 = DumbNode(
        name="NODE_3",
        bus=can1,
        arbitration_id=0x300,
        period_s=0.2,
        data=bytearray(b"\xAA\xBB\xCC\xDD\xEE\xFF\x00\x11"),
    )

    node4 = DumbNode(
        name="NODE_4",
        bus=can1,
        arbitration_id=0x400,
        period_s=1.0,
        data=bytearray(b"\x11\x22\x33\x44\x55\x66\x77\x88"),
    )

    nodes = [
        node1,
        node2,
        node3,
        node4,
    ]

    for node in nodes:
        node.initialize()

    for node in nodes:
        node.start()

    print("CAN simulator running (PCAN Style with Dynamic Data)")
    print("Press Ctrl+C to stop")

    counter = 0

    try:
        while True:
            time.sleep(1)
            counter = (counter + 1) % 256
            
            node1.data[0] = counter
            node3.data[0] = (counter * 2) % 256

    except KeyboardInterrupt:
        print("\nStopping simulation gracefully...")

    finally:
        for node in nodes:
            try:
                node.stop()
            except Exception:
                pass

        for bus in [can0, can1]:
            try:
                bus.shutdown()
            except Exception:
                pass
        
        print("Simulator stopped successfully.")


if __name__ == "__main__":
    main()