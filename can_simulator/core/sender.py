from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .bus import CanBus
from .message import Message


@dataclass
class _TxState:
    arbitration_id: int
    is_extended_id: bool
    period_s: float
    message: Optional[Message] = None
    values: Dict[str, float] = field(default_factory=dict)
    raw: Optional[bytearray] = None


class PeriodicSender:
    def __init__(self, name: str, bus: CanBus) -> None:
        self.name: str = name
        self.bus: CanBus = bus
        self._states: Dict[str, _TxState] = {}
        self._lock: threading.RLock = threading.RLock()
        self._stop_event: threading.Event = threading.Event()
        self._threads: List[threading.Thread] = []

    def add_message(self, message: Message, period_s: float, **initial_values: float) -> None:
        with self._lock:
            self._states[message.name] = _TxState(
                arbitration_id=message.arbitration_id,
                is_extended_id=message.is_extended_id,
                period_s=period_s,
                message=message,
                values=dict(initial_values),
            )

    def add_raw(self, name: str, arbitration_id: int, period_s: float, data: bytes, is_extended_id: bool = False) -> None:
        with self._lock:
            self._states[name] = _TxState(
                arbitration_id=arbitration_id,
                is_extended_id=is_extended_id,
                period_s=period_s,
                raw=bytearray(data),
            )

    def set_values(self, name: str, **values: float) -> None:
        with self._lock:
            self._states[name].values.update(values)

    def set_byte(self, name: str, index: int, value: int) -> None:
        with self._lock:
            self._states[name].raw[index] = value & 0xFF

    def set_bytes(self, name: str, data: bytes) -> None:
        with self._lock:
            self._states[name].raw = bytearray(data)

    def start(self) -> None:
        self._stop_event.clear()
        with self._lock:
            names = list(self._states.keys())
        for name in names:
            thread = threading.Thread(target=self._loop, args=(name,), daemon=True)
            self._threads.append(thread)
            thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        for thread in self._threads:
            thread.join(timeout=2.0)
        self._threads.clear()

    def _loop(self, name: str) -> None:
        while not self._stop_event.is_set():
            with self._lock:
                state = self._states[name]
                if state.raw is not None:
                    data = bytes(state.raw)
                else:
                    data = state.message.encode(state.values)
                arbitration_id = state.arbitration_id
                is_extended_id = state.is_extended_id
                period_s = state.period_s
            self.bus.send_raw(arbitration_id, data, is_extended_id)
            self._stop_event.wait(period_s)
