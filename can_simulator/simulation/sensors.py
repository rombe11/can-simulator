from __future__ import annotations

import time
from can_simulator.core.bus import BusConfig, CanBus
from can_simulator.core.monitor import PCANStyleMonitor
from can_simulator.nodes.j1939_sensors_node import J1939SensorNode


def main() -> None:
    bus = CanBus(
        BusConfig(
            channel="vcan0",
            interface="socketcan",
            bitrate=250_000,
            receive_own_messages=True,
        )
    )

    monitor = PCANStyleMonitor("J1939_GLOBAL_MONITOR", update_interval=0.1)
    bus.add_listener(monitor)

    node = J1939SensorNode("J1939_Simulated_Device", bus)
    node.initialize()
    node.start()

    counter: int = 0

    try:
        while True:
            time.sleep(0.3)
            counter = (counter + 1) % 250

            node.update_sensor_value("sensor_1", index=0, value=50 + counter)
            node.update_sensor_value("sensor_2", index=2, value=counter)
            node.update_sensor_value("sensor_2", index=3, value=(counter * 2) % 256)
            node.update_sensor_value("sensor_3", index=0, value=max(10, 100 - counter))

    except KeyboardInterrupt:
        pass

    finally:
        node.stop()
        bus.shutdown()


if __name__ == "__main__":
    main()