#!/bin/bash

set -e

echo "=== Setting up Virtual CAN interfaces for System A (user_can) ==="

sudo modprobe vcan

# Create and bring up the vcan interfaces for System A
for ch in can3 can4 can5; do
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

echo "=== Setting up Virtual CAN interfaces for System B (sysB_) ==="

# Create and bring up the vcan interfaces for System B
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
echo "=== Starting Python Simulation ==="

python -m can_simulator.main
echo "=== Simulation completed ==="