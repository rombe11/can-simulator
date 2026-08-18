from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import can


@dataclass
class BusConfig:
    channel: str
    interface: str = "virtual"
    bitrate: int = 500_000
    receive_own_messages: bool = True


class CanBus:
    def __init__(self, config: BusConfig) -> None:
        self.config: BusConfig = config
        self.bus: can.BusABC = can.interface.Bus(
            channel=config.channel,
            interface=config.interface,
            bitrate=config.bitrate,
            receive_own_messages=config.receive_own_messages,
        )
        self.notifier: can.Notifier = can.Notifier(self.bus, listeners=[])

    def send_raw(self, arbitration_id: int, data: bytes, is_extended_id: bool = False) -> None:
        self.bus.send(can.Message(arbitration_id=arbitration_id, data=data, is_extended_id=is_extended_id))

    def add_listener(self, listener: can.Listener) -> None:
        self.notifier.add_listener(listener)

    def remove_listener(self, listener: can.Listener) -> None:
        self.notifier.remove_listener(listener)

    def shutdown(self) -> None:
        self.notifier.stop()
        self.bus.shutdown()


class BusManager:
    def __init__(self) -> None:
        self._buses: Dict[str, CanBus] = {}

    def create_bus(self, name: str, config: BusConfig) -> CanBus:
        bus = CanBus(config)
        self._buses[name] = bus
        return bus

    def get(self, name: str) -> CanBus:
        return self._buses[name]

    def shutdown_all(self) -> None:
        for bus in self._buses.values():
            bus.shutdown()
        self._buses.clear()
