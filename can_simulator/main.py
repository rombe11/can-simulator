from __future__ import annotations

import time
import threading
from can_simulator.simulation.system_back import run_system_simulation
from can_simulator.core.message import MessageCollector


def main() -> None:
    stop_event = threading.Event()
    
    collector_b = MessageCollector()

    thread_sys_b = threading.Thread(
        target=run_system_simulation, 
        args=("sysB_", stop_event, collector_b)
    )

    thread_sys_b.start()

    try:
        time.sleep(2.0)
        
        assert collector_b.last_message is not None, "No messages captured on System B!"
        print("Last captured message ID on System B:", hex(collector_b.last_message.arbitration_id))

        stop_event.set()
        thread_sys_b.join()

    except KeyboardInterrupt:
        stop_event.set()
        thread_sys_b.join()


if __name__ == "__main__":
    main()