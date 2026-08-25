from __future__ import annotations

import time
import threading
from can_simulator.core.bus import BusConfig, CanBus
from can_simulator.core.monitor import PCANStyleMonitor
from can_simulator.core.node_manager import NodeManager
from can_simulator.core.message import MessageCollector
from can_simulator.nodes.front_button_node import ButtonControllerNode
from can_simulator.nodes.front_back_communication import SystemFrontGatewayNode
from can_simulator.nodes.canopen_slave import CANopenSlaveNode


def create_system_front_buses() -> dict[str, CanBus]:
    buses = {
        "can2": CanBus(BusConfig(channel="user_can2", interface="socketcan", bitrate=125_000, receive_own_messages=True)),
        "can3": CanBus(BusConfig(channel="user_can3", interface="socketcan", bitrate=250_000, receive_own_messages=True)),
        "can4": CanBus(BusConfig(channel="user_can4", interface="socketcan", bitrate=250_000, receive_own_messages=True)),
        "can5": CanBus(BusConfig(channel="user_can5", interface="socketcan", bitrate=250_000, receive_own_messages=True)),
    }
    return buses


def run_system_front_simulation(
    stop_event: threading.Event | None = None, 
    collector: MessageCollector | None = None
) -> MessageCollector:
    buses = create_system_front_buses()
    
    monitor = PCANStyleMonitor("SYSTEM_FRONT_MONITOR", update_interval=0.1)
    for bus in buses.values():
        bus.add_listener(monitor)
        if collector:
            bus.add_listener(collector)

    manager = NodeManager()

    button_node = ButtonControllerNode("ButtonNode", buses["can2"])
    manager.add(button_node)

    node_1e_can3 = CANopenSlaveNode("Dev1E_Can3", buses["can3"], node_id=0x1E)
    node_1f_can3 = CANopenSlaveNode("Dev1F_Can3", buses["can3"], node_id=0x1F)
    
    node_1e_can4 = CANopenSlaveNode("Dev1E_Can4", buses["can4"], node_id=0x1E)
    node_1f_can4 = CANopenSlaveNode("Dev1F_Can4", buses["can4"], node_id=0x1F)

    manager.add(node_1e_can3)
    manager.add(node_1f_can3)
    manager.add(node_1e_can4)
    manager.add(node_1f_can4)

    gateway_node = SystemFrontGatewayNode("GatewayNode", buses["can5"])
    manager.add(gateway_node)

    manager.initialize_all()
    manager.start_all()

    counter = 0

    try:
        while stop_event is None or not stop_event.is_set():
            time.sleep(0.3)
            counter = (counter + 1) % 250

            if counter % 50 == 0:
                button_node.trigger_reset(bit_index=0)
            elif counter % 50 == 25:
                button_node.trigger_reset(bit_index=2)

            if counter == 10:
                node_1e_can3.send_command_command(0x01)

    except KeyboardInterrupt:
        pass

    finally:
        manager.shutdown()
        for bus in buses.values():
            bus.shutdown()

    return collector if collector else MessageCollector()