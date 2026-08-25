#!/bin/bash

set -e

# Check if an argument was passed
if [ -z "$1" ]; then
    echo "Usage: ./run_systems.sh [front|back]"
    exit 1
fi

MODE="$1"

echo "=== Setting up Virtual CAN interfaces for System Front (user_can) ==="

sudo modprobe vcan

for ch in can2 can3 can4 can5; do
    interface="user_${ch}"

    if ip link show "$interface" &> /dev/null; then
        echo "Interface $interface already exists, bringing it up..."
        sudo ip link set up "$interface"
    else
        echo "Creating and bringing up $interface..."
        sudo ip link add dev "$interface" type vcan
        sudo ip link set up "$interface"
    fi
done

echo "=== Setting up Virtual CAN interfaces for System Back (sysB_) ==="

for ch in can3 can4 can5; do
    interface="sysB_${ch}"

    if ip link show "$interface" &> /dev/null; then
        echo "Interface $interface already exists, bringing it up..."
        sudo ip link set up "$interface"
    else
        echo "Creating and bringing up $interface..."
        sudo ip link add dev "$interface" type vcan
        sudo ip link set up "$interface"
    fi
done

echo "=== All Virtual CAN interfaces are ready ==="
echo "=== Starting Python Simulation ($MODE) ==="

python3 -m can_simulator.main "$MODE"
echo "=== Simulation completed ==="