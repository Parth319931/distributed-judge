import threading
from typing import Callable, Optional
from xmlrpc.server import SimpleXMLRPCServer
from socketserver import ThreadingMixIn

from utils.logger import log


class ThreadingXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    daemon_threads = True


class RMIServer:
    """
    Minimal XML-RPC server exposing submit_code to simulate remote submissions.
    The actual code execution is simulated by a callback.
    """

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self._server: Optional[SimpleXMLRPCServer] = None
        self._thread: Optional[threading.Thread] = None
        self._process_submission: Optional[Callable[[str, str], str]] = None
        self._default_executor: Optional[Callable[[str, str], str]] = None
        self._extra_functions: dict[str, Callable[..., object]] = {}

    def bind_processor(self, processor: Callable[[str, str], str]) -> None:
        self._process_submission = processor

    def _submit_code(self, code: str, tests: str) -> str:
        if not self._process_submission and not self._default_executor:
            return "Processor not ready"
        log("RMI", f"received submission len(code)={len(code)} len(tests)={len(tests)}")
        # Delegate to provided processor; expected to be thread-safe
        if self._process_submission:
            return self._process_submission(code, tests)
        return self._default_executor(code, tests)  # type: ignore[func-returns-value]

    def start(self) -> None:
        def _serve() -> None:
            with ThreadingXMLRPCServer((self.host, self.port), allow_none=True, logRequests=False) as server:
                self._server = server
                server.register_function(self._submit_code, "submit_code")
                # register extra functions if provided
                for name, fn in self._extra_functions.items():
                    server.register_function(fn, name)
                log("RMI", f"listening on {self.host}:{self.port}")
                server.serve_forever()

        self._thread = threading.Thread(target=_serve, name=f"RMI:{self.port}", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if self._server:
            self._server.shutdown()
            log("RMI", "server shutdown initiated")
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

    # Optional: allow setting a fallback executor if manager isn't bound yet
    def set_default_executor(self, executor: Callable[[str, str], str]) -> None:
        self._default_executor = executor

    def register(self, name: str, fn: Callable[..., object]) -> None:
        # If server already running, register immediately; else store for later
        if self._server is not None:
            self._server.register_function(fn, name)
        self._extra_functions[name] = fn


