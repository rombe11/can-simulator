from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum

from .bus import CanBus
from .message import Message
from .sender import PeriodicSender


class NodeState(Enum):
    CREATED = "created"
    INITIALIZING = "initializing"
    INITIALIZED = "initialized"
    OPERATIONAL = "operational"
    STOPPED = "stopped"
    ERROR = "error"


class Node(ABC):
    def __init__(self, name: str, bus: CanBus) -> None:
        self.name = name
        self.bus = bus
        self.state = NodeState.CREATED

        self.sender = PeriodicSender(
            name=f"{name}_sender",
            bus=bus,
        )

    def initialize(self) -> None:
        if self.state != NodeState.CREATED:
            raise RuntimeError(
                f"Node '{self.name}' cannot initialize "
                f"from state {self.state.value}"
            )

        self.state = NodeState.INITIALIZING

        try:
            self.init()
            self.state = NodeState.INITIALIZED
        except Exception:
            self.state = NodeState.ERROR
            raise

    @abstractmethod
    def init(self) -> None:
        pass

    def add_periodic_message(
        self,
        message: Message,
        period_s: float,
        **initial_values: float,
    ) -> None:
        self.sender.add_message(
            message,
            period_s=period_s,
            **initial_values,
        )

    def set_message_values(
        self,
        message_name: str,
        **values: float,
    ) -> None:
        self.sender.set_values(
            message_name,
            **values,
        )

    def start(self) -> None:
        if self.state != NodeState.INITIALIZED:
            raise RuntimeError(
                f"Node '{self.name}' must be initialized "
                f"before start()"
            )

        self.sender.start()
        self.state = NodeState.OPERATIONAL

    def stop(self) -> None:
        if self.state == NodeState.STOPPED:
            return

        self.sender.stop()
        self.state = NodeState.STOPPED