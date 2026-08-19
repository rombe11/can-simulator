from __future__ import annotations

from typing import Dict

from .node import Node


class NodeManager:
    def __init__(self) -> None:
        self._nodes: Dict[str, Node] = {}

    def add(self, node: Node) -> None:
        if node.name in self._nodes:
            raise ValueError(
                f"Node '{node.name}' already exists"
            )

        self._nodes[node.name] = node

    def get(self, name: str) -> Node:
        return self._nodes[name]

    def remove(self, name: str) -> Node:
        return self._nodes.pop(name)

    def initialize_all(self) -> None:
        for node in self._nodes.values():
            node.initialize()

    def start_all(self) -> None:
        for node in self._nodes.values():
            node.start()

    def stop_all(self) -> None:
        for node in self._nodes.values():
            node.stop()

    def shutdown(self) -> None:
        self.stop_all()
        self._nodes.clear()

    def __iter__(self):
        return iter(self._nodes.values())