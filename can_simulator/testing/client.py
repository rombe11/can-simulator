from __future__ import annotations

import queue
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Set

import can

from ..core.bus import CanBus
from ..core.message import Message, MessageDB


class TimeoutWaitingForMessage(AssertionError):
    pass


class SignalMismatch(AssertionError):
    pass


@dataclass
class ReceivedMessage:
    message: Message
    values: Dict[str, float]
    timestamp: float


@dataclass
class RawFrame:
    arbitration_id: int
    data: bytes
    timestamp: float


class _QueueListener(can.Listener):
    def __init__(self, q: "queue.Queue[can.Message]") -> None:
        self._q: "queue.Queue[can.Message]" = q

    def on_message_received(self, msg: can.Message) -> None:
        self._q.put(msg)


class CanTestClient:
    def __init__(self, bus: CanBus, db: Optional[MessageDB] = None) -> None:
        self.bus: CanBus = bus
        self.db: Optional[MessageDB] = db
        self._queue: "queue.Queue[can.Message]" = queue.Queue()
        self._listener: _QueueListener = _QueueListener(self._queue)
        bus.add_listener(self._listener)

    def close(self) -> None:
        self.bus.remove_listener(self._listener)

    def send(self, message_name: str, **signal_values: float) -> None:
        msg = self.db.by_name(message_name)
        values = msg.default_values()
        values.update(signal_values)
        data = msg.encode(values)
        self.bus.send_raw(msg.arbitration_id, data, msg.is_extended_id)

    def send_bytes(self, arbitration_id: int, data: bytes, is_extended_id: bool = False) -> None:
        self.bus.send_raw(arbitration_id, data, is_extended_id)

    def drain(self) -> None:
        while True:
            try:
                self._queue.get_nowait()
            except queue.Empty:
                break

    def wait_for_raw(self, message_name: str, timeout: float = 1.0) -> ReceivedMessage:
        msg_def = self.db.by_name(message_name)
        frame = self.wait_for_id(msg_def.arbitration_id, timeout=timeout)
        values = msg_def.decode(frame.data)
        return ReceivedMessage(msg_def, values, frame.timestamp)

    def expect(self, message_name: str, timeout: float = 1.0, **expected_signals: Any) -> Dict[str, float]:
        deadline = time.monotonic() + timeout
        last_seen: Optional[Dict[str, float]] = None
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            received = self.wait_for_raw(message_name, timeout=remaining)
            last_seen = received.values
            if all(received.values.get(name) == value for name, value in expected_signals.items()):
                return received.values
        raise SignalMismatch(f"{message_name} {expected_signals} last_seen={last_seen}")

    def wait_for_id(self, arbitration_id: int, timeout: float = 1.0) -> RawFrame:
        deadline = time.monotonic() + timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutWaitingForMessage(f"0x{arbitration_id:X}")
            try:
                raw = self._queue.get(timeout=remaining)
            except queue.Empty:
                raise TimeoutWaitingForMessage(f"0x{arbitration_id:X}")
            if raw.arbitration_id == arbitration_id:
                return RawFrame(raw.arbitration_id, bytes(raw.data), raw.timestamp)

    def expect_byte(self, arbitration_id: int, byte_index: int, value: int, timeout: float = 1.0) -> RawFrame:
        deadline = time.monotonic() + timeout
        last_seen: Optional[bytes] = None
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            frame = self.wait_for_id(arbitration_id, timeout=remaining)
            last_seen = frame.data
            if frame.data[byte_index] == value:
                return frame
        raise SignalMismatch(f"0x{arbitration_id:X} byte[{byte_index}]!={value} last_seen={last_seen}")

    def observed_ids(self, window_s: float) -> Set[int]:
        deadline = time.monotonic() + window_s
        ids: Set[int] = set()
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return ids
            try:
                raw = self._queue.get(timeout=remaining)
            except queue.Empty:
                return ids
            ids.add(raw.arbitration_id)

    def expect_new_id(self, known_ids: Set[int], timeout: float = 1.0) -> RawFrame:
        deadline = time.monotonic() + timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutWaitingForMessage("no new id")
            try:
                raw = self._queue.get(timeout=remaining)
            except queue.Empty:
                raise TimeoutWaitingForMessage("no new id")
            if raw.arbitration_id not in known_ids:
                return RawFrame(raw.arbitration_id, bytes(raw.data), raw.timestamp)
