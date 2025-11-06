import threading
import time

from clock_sync import LamportClock
from election import BullyElection
from load_balancer import LoadBalancer
from node_manager import NodeManager
from replication import ReplicatedStore


def test_skeleton_components_import_and_basic_behavior():
    # Lamport clock basic operations
    clk = LamportClock(1)
    assert clk.tick() >= 1
    before = clk.now()
    clk.receive_event(5)
    assert clk.now() > before

    # Election select some leader
    elec = BullyElection(1, [1, 2, 3])
    leader = elec.start_election()
    assert leader in {1, 2, 3}

    # Replication latest-wins
    a = ReplicatedStore(1)
    b = ReplicatedStore(2)
    a.update_and_replicate("k", "v1", [b])
    assert a.get_local("k") == "v1"
    assert b.get_local("k") == "v1"

    # Load balancer choose least-load
    lb = LoadBalancer()
    lb.update_load(1, 2)
    lb.update_load(2, 1)
    assert lb.choose_node() == 2

    # Node manager choose node and adjust load
    mgr = NodeManager({1: 9101, 2: 9102})
    nid = mgr.choose_node_for_submission()
    assert nid in {1, 2}
    mgr.update_load(nid, +1)
    assert mgr.nodes[nid].load >= 1




