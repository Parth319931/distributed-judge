import streamlit as st

import config
from utils.api_client import APIClient


def _init() -> None:
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "selected_problem_key" not in st.session_state:
        st.session_state.selected_problem_key = "two-sum"
    if "last_result" not in st.session_state:
        st.session_state.last_result = {}


def main() -> None:
    _init()
    st.title("Problems")
    if not st.session_state.username:
        st.warning("Please login first (see Login page).")

    client = APIClient()
    with st.spinner("Loading problems..."):
        problems, source_msg = client.get_problems()
    if source_msg:
        st.caption(source_msg)

    keys = list(problems.keys())
    if not keys:
        st.error("No problems available.")
        return
    if st.session_state.selected_problem_key not in keys:
        st.session_state.selected_problem_key = keys[0]
    key = st.selectbox("Select a problem", keys, index=keys.index(st.session_state.selected_problem_key))
    st.session_state.selected_problem_key = key
    meta = problems[key]

    st.subheader(meta["title"]) 
    st.write(meta["prompt"]) 

    code = st.text_area("Your Python code", value=meta.get("starter_code", ""), height=240, key=f"code-{key}")
    show_tests = st.checkbox("Show tests", value=False)
    tests = st.text_area("Tests (executed after your code)", value=meta.get("tests", ""), height=160, key=f"tests-{key}") if show_tests else meta.get("tests", "")

    if st.button("Submit"):
        with st.spinner("Submitting to backend..."):
            result = client.submit(code, tests)
        st.session_state.last_result = {
            "problem_key": key,
            "output": result.get("output", ""),
            "duration": result.get("duration", ""),
            "error": result.get("error", ""),
            "username": st.session_state.username,
        }
        if result.get("error"):
            st.error(f"Error: {result['error']}")
        else:
            st.success("Submission sent. See Results page.")
            st.code(result.get("output", ""))


if __name__ == "__main__":
    main()


