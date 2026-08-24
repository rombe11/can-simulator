from __future__ import annotations

import time
import threading
from can_simulator.core.bus import BusConfig, CanBus
from can_simulator.core.monitor import PCANStyleMonitor
from can_simulator.core.node_manager import NodeManager
from can_simulator.nodes.j1939_sensors_node import J1939SensorNode
from can_simulator.core.message import MessageCollector


def create_buses(bus_prefix: str = "") -> dict[str, CanBus]:
    channels = ["can3", "can4", "can5"]
    buses = {}
    for ch in channels:
        channel_name = f"{bus_prefix}{ch}" if bus_prefix else f"v{ch}"
        buses[ch] = CanBus(
            BusConfig(
                channel=channel_name,
                interface="socketcan",
                bitrate=250_000,
                receive_own_messages=True,
            )
        )
    return buses


def setup_monitor(buses: dict[str, CanBus], name: str) -> PCANStyleMonitor:
    monitor = PCANStyleMonitor(name, update_interval=0.1)
    for bus in buses.values():
        bus.add_listener(monitor)
    return monitor


def setup_collector(buses: dict[str, CanBus], collector: MessageCollector | None = None) -> MessageCollector:
    active_collector = collector if collector is not None else MessageCollector()
    for bus in buses.values():
        bus.add_listener(active_collector)
    return active_collector


def setup_devices(buses: dict[str, CanBus], bus_prefix: str = "") -> tuple[NodeManager, J1939SensorNode]:
    manager = NodeManager()
    device = J1939SensorNode(f"{bus_prefix}J1939Device", buses["can4"])
    manager.add(device)
    return manager, device


def run_system_simulation(
    bus_prefix: str = "", 
    stop_event: threading.Event | None = None, 
    collector: MessageCollector | None = None
) -> MessageCollector:
    buses = create_buses(bus_prefix)
    monitor_name = f"{bus_prefix.upper()}SYSTEM_MONITOR" if bus_prefix else "SYSTEM_GLOBAL_MONITOR"
    setup_monitor(buses, monitor_name)
    active_collector = setup_collector(buses, collector)
    manager, device = setup_devices(buses, bus_prefix)

    manager.initialize_all()
    manager.start_all()

    counter = 0

    try:
        while True:
            time.sleep(0.3)
            counter = (counter + 1) % 250

            device.update_sensor_value("sensor_1", 0, 50 + counter)
            device.update_sensor_value("sensor_2", 2, counter)
            device.update_sensor_value("sensor_3", 0, max(10, 100 - counter))
            device.update_sensor_value("sensor_4", 1, counter)

            device.update_sensor_value("alt_manufacturer_sensor", 0, 22 + (counter % 5))
            device.update_sensor_value("alt_manufacturer_sensor", 1, 50 + (counter % 10))

            device.update_sensor_value("gas_analyzer_sensor", 0, 21 + (counter % 3))
            device.update_sensor_value("gas_analyzer_sensor", 1, 40 + (counter % 15))
            device.update_sensor_value("gas_analyzer_sensor", 2, 2 + (counter % 5))

    except KeyboardInterrupt:
        pass

    finally:
        manager.shutdown()
        for bus in buses.values():
            bus.shutdown()

    return active_collector


def main() -> None:
    run_system_simulation()


if __name__ == "__main__":
    main()