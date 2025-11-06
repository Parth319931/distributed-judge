from typing import Any, Dict, List, Tuple

from utils.logger import log


class ReplicatedStore:
    """
    Simple replicated key-value store with integer version per key to simulate
    eventual consistency. Latest version wins.
    """

    def __init__(self, node_id: int) -> None:
        self.node_id = node_id
        self._data: Dict[str, Tuple[int, Any]] = {}

    def get_local(self, key: str) -> Any:
        entry = self._data.get(key)
        return entry[1] if entry else None

    def apply_update(self, key: str, value: Any, version: int) -> None:
        local = self._data.get(key)
        if local is None or version >= local[0]:
            self._data[key] = (version, value)
            log("Replication", f"node={self.node_id} apply key={key} v={version} val={value}")

    def update_and_replicate(self, key: str, value: Any, peers: List["ReplicatedStore"]) -> None:
        # Increment local version then push to peers
        current_version = (self._data.get(key) or (0, None))[0]
        new_version = current_version + 1
        self.apply_update(key, value, new_version)
        for peer in peers:
            peer.apply_update(key, value, new_version)
            log("Replication", f"node={self.node_id} -> node={peer.node_id} key={key} v={new_version}")

    def dump(self) -> Dict[str, Tuple[int, Any]]:
        return dict(self._data)

    def sync_from(self, other: "ReplicatedStore") -> None:
        # Merge by latest version per key
        other_data = other.dump()
        for k, (ver, val) in other_data.items():
            self.apply_update(k, val, ver)


