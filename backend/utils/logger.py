import time
import threading


def timestamp() -> str:
    """Return a simple human-readable timestamp."""
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def log(component: str, message: str) -> None:
    """
    Central logging utility for the Distributed Judge backend.

    - component: logical subsystem emitting the log (e.g., RMI, Election)
    - message: human readable detail
    """
    thread_name = threading.current_thread().name
    print(f"[{timestamp()}] [{thread_name}] [{component}] {message}")




