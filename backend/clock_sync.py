from typing import Dict

from utils.logger import log


class LamportClock:
    """
    Minimal Lamport logical clock implementation.
    Rules:
      - Local event: c <- c + 1
      - Send event: include c in message after increment
      - Receive event: c <- max(c, received) + 1
    """

    def __init__(self, node_id: int) -> None:
        self.node_id = node_id
        self._counter = 0

    def tick(self) -> int:
        self._counter += 1
        log("Clock", f"node={self.node_id} local tick -> {self._counter}")
        return self._counter

    def send_event(self) -> int:
        self._counter += 1
        log("Clock", f"node={self.node_id} send -> {self._counter}")
        return self._counter

    def receive_event(self, received_counter: int) -> int:
        self._counter = max(self._counter, received_counter) + 1
        log("Clock", f"node={self.node_id} recv({received_counter}) -> {self._counter}")
        return self._counter

    def now(self) -> int:
        return self._counter




