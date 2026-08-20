## CAN Simulator & HIL Framework

The CAN Simulator is a lightweight, Python-based framework designed for simulating, testing, and monitoring Controller Area Network (CAN) communication buses. It bridges the gap between virtual prototyping and real-world Hardware-in-The-Loop (HIL) testing, enabling seamless integration between simulated virtual sensors/nodes and physical CAN hardware (such as PEAK USB-to-CAN interfaces). It is ideal for automotive, industrial, and embedded systems development.

# Features

- Virtual & Real Hardware Support: Easily switch between Linux virtual CAN (vcan) and real physical hardware (socketcan) like PEAK PCAN adapters.

- Mixed HIL Simulations: Run fake/simulated sensor nodes concurrently with real physical hardware devices on the same CAN bus.

- Dynamic Real-Time Control: Update message payloads, bytes, and signals on-the-fly while sender threads run in the background.

- PCAN-Style Live Monitor: Built-in terminal monitor to observe traffic, arbitration IDs, DLC, message counts, and data bytes in real time.

- Robust Core Architecture: Thread-safe design with comprehensive unit and integration testing via pytest.


# set up environment:

- python3 -m venv venv 
- source venv/bin/activa te
- pip install -r requirements.txt

# set up virtual can on Linux:

# Option A: Virtual CAN Setup (for prototyping & offline testing)

sudo modprobe vcan

sudo ip link add dev vcan0 type vcan
sudo ip link add dev vcan1 type vcan

sudo ip link set up vcan0
sudo ip link set up vcan1

# Option B: Real PEAK Hardware Setup (HIL mode)

sudo ip link set can0 up type can bitrate 500000

# Run Simulation:

- python -m can_simulator.simulation.poc // or other simulation file
- python -m pytest /tests