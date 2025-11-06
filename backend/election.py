import random
import time
from typing import List, Optional

from utils.logger import log


class BullyElection:
    """
    Bully election algorithm (skeleton) for leader selection among nodes.
    Higher node_id "bullies" lower ones to become leader.
    """

    def __init__(self, node_id: int, alive_node_ids: List[int]) -> None:
        self.node_id = node_id
        self.all_node_ids = sorted(alive_node_ids)
        self.leader_id: Optional[int] = None

    def start_election(self) -> int:
        """
        Start an election by notifying higher-id nodes (simulated locally).
        If none respond (simulated by random), become leader.
        """
        log("Election", f"node={self.node_id} starting election")

        higher = [n for n in self.all_node_ids if n > self.node_id]
        any_higher_alive = False
        for n in higher:
            # Simulate whether higher node responds (alive) deterministically via randomness
            responded = random.random() > 0.2  # 80% chance alive
            log("Election", f"node={self.node_id} -> node={n} ELECTION, responded={responded}")
            if responded:
                any_higher_alive = True

        if any_higher_alive:
            # Assume a higher node will take over election and eventually declare victory
            time.sleep(0.05)
            winner = max(higher)
            self.leader_id = winner
            log("Election", f"node={self.node_id} acknowledges leader node={winner}")
        else:
            # Become leader (bully wins)
            self.leader_id = self.node_id
            log("Election", f"node={self.node_id} became leader")

        return self.leader_id or self.node_id

    def get_leader(self) -> Optional[int]:
        return self.leader_id


