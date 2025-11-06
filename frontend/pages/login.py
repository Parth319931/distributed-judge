import streamlit as st


def _init() -> None:
    if "username" not in st.session_state:
        st.session_state.username = ""


def main() -> None:
    _init()
    st.title("Login")
    st.write("Enter a username to start using the judge.")
    username = st.text_input("Username", value=st.session_state.username)
    if st.button("Save"):
        st.session_state.username = username.strip()
        if st.session_state.username:
            st.success(f"Logged in as {st.session_state.username}")
        else:
            st.warning("Username cleared.")
    if st.session_state.username:
        go = st.button("Continue to Problems →")
        if go:
            # Best-effort navigation hint; multipage sidebar will show pages automatically
            st.experimental_set_query_params(page="Problems")
            st.info("Open the Problems page from the sidebar.")


if __name__ == "__main__":
    main()


