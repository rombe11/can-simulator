# CAN Simulator

## Structure

```
can_simulator/
  core/
    message.py   Message + Signal, bit-level encode/decode
    bus.py       BusConfig, CanBus, BusManager - N independent CAN lines
    config.py    loads config/buses.yaml into BusConfig objects
    sender.py    PeriodicSender - sends a message repeatedly at a frequency
  testing/
    client.py    CanTestClient - send stimuli, expect()/wait_for_raw() responses
config/
  buses.yaml     one entry per CAN line: channel, interface, bitrate
tests/
  conftest.py    bus fixtures + pytest hook that writes test_results.csv
  test_example.py
```

## Install

```
pip install -r requirements.txt
```

## Run

```
pytest -v
```

After the run, `test_results.csv` is written at the project root with one row per test: `test,result,duration_s`.

## Point a line at real hardware

Edit `config/buses.yaml`:

```yaml
buses:
  line1:
    interface: socketcan
    channel: can0
    bitrate: 500000
```

`interface: virtual` only works within a single Python process. For a real
controller, or two independent processes on the same wire, use
`socketcan` with a real adapter (`can0`) or a kernel virtual CAN device:

```
sudo modprobe vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0
```

## Test pattern

```python
sender = PeriodicSender("stimulus", bus)
sender.add_message(REQUEST, period_s=0.05, target_speed=0)
sender.start()

client = CanTestClient(bus, DB)
sender.set_values("SpeedRequest", target_speed=120)
status = client.expect("SpeedStatus", timeout=1.0, current_speed=120)
assert status["current_speed"] == 120
```

`test_two_lines_in_parallel` in `test_example.py` shows the same pattern on
two lines at once via the `real_buses` fixture (`config/buses.yaml`). One
single-channel USB-CAN adapter can only drive one physical line at a time -
running two lines concurrently against real hardware needs a multi-channel
adapter (one transceiver per line) or two adapters.

## Working with raw bytes (no Signal per byte)

`Message`/`Signal` is optional. Skip it entirely and work with a frame's
raw payload directly - `data` is plain `bytes`, indexed like `data[i]`:

```python
sender.add_raw("status", arbitration_id=0x201, period_s=0.05, data=bytes(8))
sender.set_byte("status", index=2, value=0xFF)

client = CanTestClient(bus)
frame = client.expect_byte(0x201, byte_index=2, value=0xFF, timeout=1.0)
frame.data[2]
```

## Catching a message you never declared (EMCY-style)

Take a baseline of which arbitration ids are on the bus, then wait for one
outside that set - this doesn't require knowing the new message's layout
ahead of time:

```python
baseline = client.observed_ids(window_s=0.3)
client.send_bytes(0x100, bytes([1, 0, 0, 0, 0, 0, 0, 0]))
frame = client.expect_new_id(known_ids=baseline, timeout=1.0)
frame.arbitration_id
frame.data[0]
```

See `tests/test_raw_bytes.py` for both in a runnable test.
