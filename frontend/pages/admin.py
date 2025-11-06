import time

import streamlit as st

from utils.api_client import APIClient


def _init() -> None:
    if "last_admin_msg" not in st.session_state:
        st.session_state.last_admin_msg = ""


def _render_status(status: dict | None, msg: str) -> None:
    if status is None:
        st.error(f"Failed to fetch cluster status: {msg}")
        return
    st.subheader("Cluster Status")
    st.write(f"Leader: {status.get('leader', '-')}")
    nodes = status.get("nodes", {})
    for nid, info in sorted(nodes.items()):
        st.write(f"Node {nid}: alive={info['alive']} load={info['load']} clock={info['clock']} port={info['port']}")


def _render_metrics(data: dict | None, msg: str) -> None:
    if data is None:
        st.error(msg)
        return
    running = data.get("running", {})
    recent = data.get("recent", [])

    with st.expander("Running tasks by node", expanded=False):
        any_running = False
        for nid, tasks in sorted(running.items()):
            rows = []
            for tid, meta in tasks.items():
                rows.append({"task": tid, "start": meta.get("start"), "thread": meta.get("thread")})
            if rows:
                any_running = True
                st.markdown(f"Node {nid}")
                st.table(rows)
        if not any_running:
            st.caption("No running tasks.")

    with st.expander("Recent results (last 50)", expanded=True):
        if recent:
            # Normalize recent into a lightweight table
            rows = [
                {"node": r.get("node"), "task": r.get("task"), "duration(s)": r.get("duration"), "thread": r.get("thread"), "status": r.get("status")}
                for r in recent
            ]
            st.table(rows)
        else:
            st.caption("No recent results.")


def main() -> None:
    _init()
    st.title("Admin")
    client = APIClient()

    with st.spinner("Fetching status..."):
        status, msg = client.get_cluster_status()
    _render_status(status, msg)

    st.divider()
    st.subheader("Controls")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        node_to_crash = st.number_input("Crash node id", min_value=1, value=1, step=1)
        if st.button("Crash Node"):
            with st.spinner("Crashing node..."):
                ok, m = client.crash_node(int(node_to_crash))
            st.toast("Crashed" if ok else f"Failed: {m}")
            time.sleep(0.2)
            status, msg = client.get_cluster_status()
            _render_status(status, msg)

    with col2:
        node_to_recover = st.number_input("Recover node id", min_value=1, value=1, step=1, key="recover")
        if st.button("Recover Node"):
            with st.spinner("Recovering node..."):
                ok, m = client.recover_node(int(node_to_recover))
            st.toast("Recovered" if ok else f"Failed: {m}")
            time.sleep(0.2)
            status, msg = client.get_cluster_status()
            _render_status(status, msg)

    with col3:
        if st.button("Force Election"):
            with st.spinner("Forcing election..."):
                leader, m = client.force_election()
            if leader is not None:
                st.success(f"New leader: {leader}")
            else:
                st.error(f"Failed: {m}")
            status, msg = client.get_cluster_status()
            _render_status(status, msg)

    with col4:
        if st.button("Refresh Status"):
            with st.spinner("Refreshing..."):
                status, msg = client.get_cluster_status()
            _render_status(status, msg)

    st.divider()
    st.subheader("Multithreading Demo")
    cols = st.columns(3)
    with cols[0]:
        n = st.number_input("Batch submissions", min_value=1, max_value=20, value=5, step=1)
    with cols[1]:
        run = st.button("Run Batch")
    with cols[2]:
        if st.button("Show Runtime Metrics"):
            with st.spinner("Fetching metrics..."):
                data, m = client.get_runtime_metrics()
            _render_metrics(data, m)
    if run:
        with st.spinner("Submitting batch to backend..."):
            data, m = client.submit_batch(int(n))
        if data is None:
            st.error(m)
        else:
            st.success(f"Submitted {data.get('submitted')} jobs. See Runtime Metrics for details.")
            # auto fetch metrics after batch
            data2, m2 = client.get_runtime_metrics()
            _render_metrics(data2, m2)


if __name__ == "__main__":
    main()


