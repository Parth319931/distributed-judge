import random
import threading
import time
from typing import Dict

from node_manager import NodeManager
from rmi_server import RMIServer
from utils.logger import log


def simulate_execution(node_manager: NodeManager):
    # Wire RMI calls to real execution through the node manager
    def _processor(code: str, tests: str) -> str:
        return node_manager.execute_submission(code, tests)
    return _processor


def main() -> None:
    # Local cluster config
    nodes: Dict[int, int] = {1: 9101, 2: 9102, 3: 9103}
    manager = NodeManager(nodes)
    manager.start()

    # Prepare some replicated data (problems/tests)
    # Problem catalog surfaced to the frontend via RMI
    problems = {
        "two-sum": {
            "title": "Two Sum",
            "prompt": "Given nums and target, return indices of two numbers that add to target.",
            "starter_code": "def two_sum(nums, target):\n    return [-1, -1]",
            "tests": "assert two_sum([2,7,11,15], 9) == [0,1]",
        },
        "fizzbuzz": {
            "title": "FizzBuzz",
            "prompt": "Print numbers 1..n, replacing multiples of 3 with Fizz, 5 with Buzz.",
            "starter_code": "def fizzbuzz(n):\n    for i in range(1, n+1):\n        print(i)",
            "tests": "fizzbuzz(15)",
        },
    }
    manager.set_problems(problems)
    manager.replicate_problem("two-sum", "Find two numbers that add to target")
    manager.replicate_problem("fizzbuzz", "Print 1..n replacing multiples of 3/5")

    # Start RMI endpoint for submissions
    rmi = RMIServer("127.0.0.1", 9000)
    rmi.bind_processor(simulate_execution(manager))
    # Expose helpful cluster functions
    rmi.register("list_problems", manager.list_problems)
    rmi.register("get_cluster_status", manager.get_status)
    rmi.register("get_runtime_metrics", manager.get_runtime_metrics)
    rmi.register("crash_node", manager.crash_node)
    rmi.register("recover_node", manager.recover_node)
    rmi.register("force_election", manager.force_election)
    rmi.register("submit_batch", manager.submit_batch)
    rmi.start()

    log("Main", "Distributed Judge backend started on 127.0.0.1:9000")
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log("Main", "shutdown requested")
        manager.stop()


if __name__ == "__main__":
    main()


