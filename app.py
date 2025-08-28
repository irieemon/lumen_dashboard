import streamlit as st
from auth import login
from db import init_db, add_initiative
from ui import load_css, create_draggable_matrix


def main() -> None:
    st.set_page_config(page_title="Lumen Strategic Dashboard", page_icon="⊙", layout="wide")
    init_db()
    if not login():
        st.stop()

    load_css()
    st.title("Lumen Strategic Dashboard")

    with st.sidebar:
        st.header("Add Initiative")
        with st.form("add_form"):
            title = st.text_input("Title")
            details = st.text_area("Details")
            color = st.selectbox("Color", ["pink", "yellow", "green", "blue"])
            category = st.text_input("Category")
            if st.form_submit_button("Add"):
                add_initiative(title, details, color, category, 50, 50, st.session_state.get("username", "user"))
                st.success("Added initiative")
                st.rerun()


    create_draggable_matrix(st.session_state.get("username", "user"))


if __name__ == "__main__":
    main()
