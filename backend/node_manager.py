import io
import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from contextlib import redirect_stdout
from typing import Any, Dict, List, Optional

from clock_sync import LamportClock
from election import BullyElection
from load_balancer import LoadBalancer
from replication import ReplicatedStore
from utils.logger import log


class NodeInfo:
    def __init__(self, node_id: int, port: int) -> None:
        self.node_id = node_id
        self.port = port
        self.load = 0
        self.alive = True


class NodeManager:
    """
    Manages evaluator nodes, their clocks, replication stores, and election.
    Provides helpers for load updates and choosing nodes for submissions.
    """

    def __init__(self, node_ports: Dict[int, int]) -> None:
        self.nodes: Dict[int, NodeInfo] = {nid: NodeInfo(nid, port) for nid, port in node_ports.items()}
        self.clocks: Dict[int, LamportClock] = {nid: LamportClock(nid) for nid in node_ports}
        self.stores: Dict[int, ReplicatedStore] = {nid: ReplicatedStore(nid) for nid in node_ports}
        self.balancer = LoadBalancer()
        self.election: Optional[BullyElection] = None
        self._leader_id: Optional[int] = None
        self._lock = threading.Lock()
        self._executors: Dict[int, ThreadPoolExecutor] = {nid: ThreadPoolExecutor(max_workers=2, thread_name_prefix=f"N{nid}") for nid in node_ports}
        self._running = False
        self._problems: Dict[str, Dict[str, Any]] = {}
        self._task_seq = 0
        self._running_tasks: Dict[int, Dict[int, Dict[str, Any]]] = {nid: {} for nid in node_ports}
        self._recent_results: List[Dict[str, Any]] = []

        for nid in self.nodes:
            self.balancer.update_load(nid, 0)

    def ensure_leader(self) -> int:
        with self._lock:
            if self._leader_id is not None and self.nodes.get(self._leader_id, NodeInfo(-1, 0)).alive:
                return self._leader_id
            ids = sorted(self.nodes.keys())
            alive_ids = [nid for nid, info in self.nodes.items() if info.alive]
            initiator = random.choice(alive_ids)
            self.election = BullyElection(initiator, alive_ids)
            leader = self.election.start_election()
            self._leader_id = leader
            log("Manager", f"leader elected node={leader}")
            return leader

    def get_leader(self) -> Optional[int]:
        return self._leader_id

    def update_load(self, node_id: int, delta: int) -> None:
        node = self.nodes[node_id]
        node.load = max(0, node.load + delta)
        self.balancer.update_load(node_id, node.load)

    def choose_node_for_submission(self) -> Optional[int]:
        alive_ids = [nid for nid, info in self.nodes.items() if info.alive]
        return self.balancer.choose_from(alive_ids)

    def replicate_problem(self, key: str, value: str) -> None:
        # Fan out from leader to others
        leader = self.ensure_leader()
        peers = [self.stores[n] for n in self.nodes if n != leader]
        self.stores[leader].update_and_replicate(key, value, peers)

    def broadcast_clock_tick(self) -> None:
        for nid, clk in self.clocks.items():
            clk.tick()

    def _safe_globals(self) -> Dict[str, Any]:
        allowed_builtins = {
            "range": range,
            "len": len,
            "sum": sum,
            "min": min,
            "max": max,
            "print": print,
            "abs": abs,
            "enumerate": enumerate,
            "map": map,
            "filter": filter,
            "list": list,
            "dict": dict,
            "set": set,
            "int": int,
            "float": float,
            "str": str,
            "bool": bool,
            "zip": zip,
        }
        return {"__builtins__": allowed_builtins}

    def execute_submission(self, code: str, tests: str, timeout_seconds: float = 2.0) -> str:
        node_id = self.choose_node_for_submission()
        if node_id is None:
            return "No nodes available"
        # Lamport send event for assigning
        self.clocks[node_id].send_event()
        self.update_load(node_id, +1)
        log("Exec", f"assign submission to node={node_id}")

        with self._lock:
            self._task_seq += 1
            task_id = self._task_seq
            self._running_tasks[node_id][task_id] = {"start": time.time(), "thread": None}

        def _run() -> str:
            # Local event before run
            self.clocks[node_id].tick()
            stdout = io.StringIO()
            g = self._safe_globals()
            try:
                # record thread name once running
                with self._lock:
                    if task_id in self._running_tasks[node_id]:
                        self._running_tasks[node_id][task_id]["thread"] = threading.current_thread().name
                with redirect_stdout(stdout):
                    exec(code, g, g)
                    if tests.strip():
                        exec(tests, g, g)
                result = stdout.getvalue()
                return result if result else "OK"
            except Exception as ex:  # noqa: BLE001
                return f"ERROR: {ex}"
            finally:
                stdout.close()

        future = self._executors[node_id].submit(_run)
        try:
            output = future.result(timeout=timeout_seconds)
        except TimeoutError:
            output = "TIMEOUT"
        finally:
            # Receive event (simulate completion notification)
            self.clocks[node_id].receive_event(self.clocks[node_id].now())
            self.update_load(node_id, -1)
            log("Exec", f"finished submission on node={node_id} -> {output[:60]}")
            with self._lock:
                info = self._running_tasks[node_id].pop(task_id, {"start": time.time(), "thread": None})
                duration = time.time() - info.get("start", time.time())
                self._recent_results.append({
                    "node": node_id,
                    "task": task_id,
                    "duration": round(duration, 3),
                    "thread": info.get("thread"),
                    "status": output,
                })
                if len(self._recent_results) > 50:
                    self._recent_results = self._recent_results[-50:]
        return output

    # Cluster controls
    def crash_node(self, node_id: int) -> bool:
        info = self.nodes.get(node_id)
        if not info:
            return False
        info.alive = False
        self.update_load(node_id, 0 - info.load)
        exe = self._executors.get(node_id)
        if exe:
            exe.shutdown(wait=False, cancel_futures=True)
        log("Manager", f"node crashed node={node_id}")
        # trigger re-election if leader crashed
        if self._leader_id == node_id:
            self._leader_id = None
            self.ensure_leader()
        return True

    def recover_node(self, node_id: int) -> bool:
        info = self.nodes.get(node_id)
        if not info:
            return False
        info.alive = True
        if node_id not in self._executors or self._executors[node_id]._shutdown:  # type: ignore[attr-defined]
            self._executors[node_id] = ThreadPoolExecutor(max_workers=2, thread_name_prefix=f"N{node_id}")
        self.update_load(node_id, 0)  # ensure recorded
        log("Manager", f"node recovered node={node_id}")
        self.ensure_leader()
        return True

    def force_election(self) -> int:
        self._leader_id = None
        return self.ensure_leader()

    # Problem surfacing (for frontend convenience)
    def set_problems(self, problems: Dict[str, Dict[str, Any]]) -> None:
        self._problems = problems

    def list_problems(self) -> Dict[str, Dict[str, Any]]:
        return self._problems or {}

    def get_status(self) -> Dict[str, Any]:
        # Ensure dictionary keys are strings for XML-RPC compatibility
        return {
            "leader": self._leader_id,
            "nodes": {
                str(nid): {"alive": info.alive, "load": info.load, "port": info.port, "clock": self.clocks[nid].now()}
                for nid, info in self.nodes.items()
            },
        }

    def get_runtime_metrics(self) -> Dict[str, Any]:
        with self._lock:
            running = {
                str(nid): {
                    str(tid): {"start": meta.get("start"), "thread": meta.get("thread")}
                    for tid, meta in tasks.items()
                }
                for nid, tasks in self._running_tasks.items()
            }
            results = list(self._recent_results)
        return {"running": running, "recent": results}

    def submit_batch(self, count: int) -> Dict[str, Any]:
        count = max(1, min(20, int(count)))
        outputs: List[str] = []
        for _ in range(count):
            outputs.append(self.execute_submission("print('batch')", ""))
        return {"submitted": count, "outputs": outputs}

    def start(self) -> None:
        if self._running:
            return
        self._running = True

        def _background() -> None:
            while self._running:
                self.broadcast_clock_tick()
                self.ensure_leader()
                time.sleep(0.5)

        threading.Thread(target=_background, name="BG:manager", daemon=True).start()

    def stop(self) -> None:
        self._running = False
        for exe in self._executors.values():
            exe.shutdown(wait=False, cancel_futures=True)


