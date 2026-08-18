from __future__ import annotations

from pathlib import Path
from typing import Dict, Union

import yaml

from .bus import BusConfig


def load_bus_configs(path: Union[str, Path]) -> Dict[str, BusConfig]:
    with open(path, "r") as f:
        raw = yaml.safe_load(f)
    configs: Dict[str, BusConfig] = {}
    for name, cfg in raw.get("buses", {}).items():
        configs[name] = BusConfig(
            channel=cfg["channel"],
            interface=cfg.get("interface", "virtual"),
            bitrate=cfg.get("bitrate", 500_000),
            receive_own_messages=cfg.get("receive_own_messages", True),
        )
    return configs
