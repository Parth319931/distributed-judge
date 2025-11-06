import streamlit as st


def _init() -> None:
    if "last_result" not in st.session_state:
        st.session_state.last_result = {}


def main() -> None:
    _init()
    st.title("Results")

    res = st.session_state.last_result or {}
    if not res:
        st.info("No submissions yet. Go to Problems page to submit.")
        return

    st.write(f"User: {res.get('username','-')}")
    st.write(f"Problem: {res.get('problem_key','-')}")
    st.write(f"Duration: {res.get('duration','-')}")
    if res.get("error"):
        st.error(f"Error: {res['error']}")
    else:
        output = res.get("output", "")
        status = "PASS" if output and not output.startswith("ERROR") and output != "TIMEOUT" else "FAIL"
        st.write(f"Status: {status}")
        st.success("Output:")
        st.code(output)


if __name__ == "__main__":
    main()


