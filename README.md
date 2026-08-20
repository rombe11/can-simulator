# CAN Simulator

The CAN Simulator is a lightweight, Python-based framework designed for simulating, testing, and monitoring Controller Area Network (CAN) communication buses. It bridges the gap between virtual prototyping and real-world hardware testing, making it ideal for automotive, industrial, and embedded systems development.

## Run

# set up environment:
python3 -m venv venv 
source venv/bin/activate
pip install -r requirements.txt

- python -m can_simulator.simulation.poc // or other simulation file
- python -m pytest /tests

# set up virtual can on Linux:

sudo modprobe vcan

sudo ip link add dev vcan0 type vcan
sudo ip link add dev vcan1 type vcan

sudo ip link set up vcan0
sudo ip link set up vcan1