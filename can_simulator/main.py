from __future__ import annotations

import sys
import time
import threading
from can_simulator.simulation.system_front import run_system_front_simulation
from can_simulator.simulation.system_back import run_system_simulation
from can_simulator.core.message import MessageCollector


def run_front() -> None:
    """Runs the System Front simulation indefinitely with its monitor."""
    stop_event = threading.Event()
    collector_front = MessageCollector()

    print("=== Starting System Front Simulation ===")
    thread_front = threading.Thread(
        target=run_system_front_simulation, 
        args=(stop_event, collector_front),
        daemon=True
    )
    thread_front.start()

    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\nStopping System Front...")
        stop_event.set()
        thread_front.join(timeout=2.0)
        print("System Front stopped.")


def run_back() -> None:
    """Runs the System Back simulation indefinitely with its monitor."""
    stop_event = threading.Event()
    collector_b = MessageCollector()

    print("=== Starting System Back Simulation ===")
    thread_sys_b = threading.Thread(
        target=run_system_simulation, 
        args=("sysB_", stop_event, collector_b),
        daemon=True
    )
    thread_sys_b.start()

    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\nStopping System Back...")
        stop_event.set()
        thread_sys_b.join(timeout=2.0)
        print("System Back stopped.")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 main.py front   # To run System Front")
        print("  python3 main.py back    # To run System Back")
        return

    command = sys.argv[1].lower()
    if command == "front":
        run_front()
    elif command == "back":
        run_back()
    else:
        print(f"Unknown argument: '{command}'. Use 'front' or 'back'.")


if __name__ == "__main__":
    main()