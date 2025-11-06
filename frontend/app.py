import pathlib

import streamlit as st

import config


def _inject_css() -> None:
    css_path = pathlib.Path(__file__).parent / "assets" / "style.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)


def _init_session() -> None:
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "selected_problem_key" not in st.session_state:
        st.session_state.selected_problem_key = "two-sum"
    if "last_result" not in st.session_state:
        st.session_state.last_result = {}


def main() -> None:
    st.set_page_config(page_title="Distributed Judge", layout="wide")
    _inject_css()
    _init_session()

    st.title("Distributed Judge")
    st.write("Welcome. Use the pages sidebar to login, choose a problem, and submit code.")
    st.info(f"Backend: http://{config.BACKEND_HOST}:{config.BACKEND_PORT}")

    if st.session_state.username:
        st.success(f"Logged in as {st.session_state.username}")
    else:
        st.warning("Not logged in. Go to Login page.")

    with st.sidebar:
        st.header("Navigation")
        st.write("Use the sidebar's Pages to switch between Login, Problems, Results.")
        st.write(":blue[Tip:] Save your username on the Login page before submitting.")


if __name__ == "__main__":
    main()


