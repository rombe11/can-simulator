from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Signal:
    name: str
    start_bit: int
    length: int
    scale: float = 1.0
    offset: float = 0.0
    signed: bool = False

    def encode(self, value: float) -> int:
        raw = int(round((value - self.offset) / self.scale))
        mask = (1 << self.length) - 1
        return raw & mask

    def decode(self, raw: int) -> float:
        if self.signed and raw & (1 << (self.length - 1)):
            raw -= 1 << self.length
        return raw * self.scale + self.offset


@dataclass
class Message:
    name: str
    arbitration_id: int
    dlc: int = 8
    is_extended_id: bool = False
    signals: Dict[str, Signal] = field(default_factory=dict)

    def add_signal(self, signal: Signal) -> "Message":
        self.signals[signal.name] = signal
        return self

    def encode(self, values: Dict[str, float]) -> bytes:
        payload = 0
        for name, value in values.items():
            signal = self.signals[name]
            payload |= signal.encode(value) << signal.start_bit
        return payload.to_bytes(self.dlc, byteorder="little")

    def decode(self, data: bytes) -> Dict[str, float]:
        payload = int.from_bytes(data, byteorder="little")
        result: Dict[str, float] = {}
        for name, signal in self.signals.items():
            mask = (1 << signal.length) - 1
            raw = (payload >> signal.start_bit) & mask
            result[name] = signal.decode(raw)
        return result

    def default_values(self) -> Dict[str, float]:
        return {name: 0.0 for name in self.signals}


class MessageDB:
    def __init__(self, messages: Optional[List[Message]] = None) -> None:
        self._by_name: Dict[str, Message] = {}
        self._by_id: Dict[int, Message] = {}
        for message in messages or []:
            self.register(message)

    def register(self, message: Message) -> None:
        self._by_name[message.name] = message
        self._by_id[message.arbitration_id] = message

    def by_name(self, name: str) -> Message:
        return self._by_name[name]

    def by_id(self, arbitration_id: int) -> Optional[Message]:
        return self._by_id.get(arbitration_id)

    def __iter__(self):
        return iter(self._by_name.values())
