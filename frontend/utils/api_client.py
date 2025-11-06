import time
import xmlrpc.client
from typing import Any, Dict, Tuple

import config


class APIClient:
    def __init__(self, host: str | None = None, port: int | None = None) -> None:
        self.host = host or config.BACKEND_HOST
        self.port = port or config.BACKEND_PORT
        self._client = xmlrpc.client.ServerProxy(f"http://{self.host}:{self.port}")

    def submit(self, code: str, tests: str) -> Dict[str, str]:
        start = time.time()
        try:
            result = self._client.submit_code(code, tests)
            duration = f"{(time.time() - start):.3f}s"
            return {"output": str(result), "duration": duration, "error": ""}
        except Exception as ex:  # noqa: BLE001
            duration = f"{(time.time() - start):.3f}s"
            return {"output": "", "duration": duration, "error": str(ex)}

    def get_problems(self) -> Tuple[Dict[str, Dict], str]:
        """
        Try to fetch problems from backend via optional XML-RPC method `list_problems`.
        Fallback to local config.PROBLEMS if backend doesn't provide it.
        Returns (problems_dict, message).
        """
        try:
            problems = self._client.list_problems()
            # Expecting a plain dict[str, dict]
            return problems, "Fetched from backend"
        except Exception:
            return config.PROBLEMS, "Using local problem set"

    # Admin helpers
    def get_cluster_status(self) -> Tuple[Dict[str, Any] | None, str]:
        try:
            status = self._client.get_cluster_status()
            return status, "OK"
        except Exception as ex:  # noqa: BLE001
            return None, str(ex)

    def crash_node(self, node_id: int) -> Tuple[bool, str]:
        try:
            ok = bool(self._client.crash_node(int(node_id)))
            return ok, "OK" if ok else "Failed"
        except Exception as ex:  # noqa: BLE001
            return False, str(ex)

    def recover_node(self, node_id: int) -> Tuple[bool, str]:
        try:
            ok = bool(self._client.recover_node(int(node_id)))
            return ok, "OK" if ok else "Failed"
        except Exception as ex:  # noqa: BLE001
            return False, str(ex)

    def force_election(self) -> Tuple[int | None, str]:
        try:
            new_leader = int(self._client.force_election())
            return new_leader, "OK"
        except Exception as ex:  # noqa: BLE001
            return None, str(ex)

    def get_runtime_metrics(self) -> Tuple[Dict[str, Any] | None, str]:
        try:
            data = self._client.get_runtime_metrics()
            return data, "OK"
        except Exception as ex:  # noqa: BLE001
            return None, str(ex)

    def submit_batch(self, count: int) -> Tuple[Dict[str, Any] | None, str]:
        try:
            data = self._client.submit_batch(int(count))
            return data, "OK"
        except Exception as ex:  # noqa: BLE001
            return None, str(ex)


