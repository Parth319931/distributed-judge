from typing import Dict, Optional

from utils.logger import log


class LoadBalancer:
    """
    Minimal least-load balancer. Tracks node_id -> load (int) and returns the
    node with the smallest load.
    """

    def __init__(self) -> None:
        self.node_loads: Dict[int, int] = {}

    def update_load(self, node_id: int, load: int) -> None:
        self.node_loads[node_id] = load
        log("LoadBalancer", f"update node={node_id} load={load}")

    def choose_node(self) -> Optional[int]:
        if not self.node_loads:
            return None
        # Least-load (ties broken by smallest id for determinism)
        chosen = sorted(self.node_loads.items(), key=lambda kv: (kv[1], kv[0]))[0][0]
        log("LoadBalancer", f"chosen node={chosen}")
        return chosen

    def choose_from(self, allowed_node_ids: list[int]) -> Optional[int]:
        if not allowed_node_ids:
            return None
        candidates = [(nid, self.node_loads.get(nid, 0)) for nid in allowed_node_ids]
        chosen = sorted(candidates, key=lambda kv: (kv[1], kv[0]))[0][0]
        log("LoadBalancer", f"chosen among {allowed_node_ids} -> node={chosen}")
        return chosen




