from __future__ import annotations

import pytest
from can_simulator.core.message import Message, Signal, MessageDB


def test_when_encoding_and_decoding_signal_then_physical_value_is_preserved() -> None:
    signal = Signal(name="Speed", start_bit=0, length=12, scale=0.1, offset=0.0)
    
    encoded_raw = signal.encode(120.0)
    assert encoded_raw == 1200

    decoded_val = signal.decode(encoded_raw)
    assert decoded_val == pytest.approx(120.0)


def test_when_packing_and_unpacking_message_signals_then_all_values_match_original() -> None:
    msg = Message(name="VehicleStatus", arbitration_id=0x301, dlc=8)
    msg.add_signal(Signal(name="RPM", start_bit=0, length=16, scale=1.0))
    msg.add_signal(Signal(name="Throttle", start_bit=16, length=8, scale=0.5))

    data = msg.encode({"RPM": 3000, "Throttle": 50.0})
    assert len(data) == 8

    decoded_values = msg.decode(data)
    assert decoded_values["RPM"] == 3000
    assert decoded_values["Throttle"] == 50.0


def test_when_registering_messages_in_db_then_retrieval_by_name_and_id_succeeds() -> None:
    msg = Message(name="EngineData", arbitration_id=0x100)
    db = MessageDB([msg])

    assert db.by_name("EngineData") == msg
    assert db.by_id(0x100) == msg
    assert db.by_id(0x999) is None