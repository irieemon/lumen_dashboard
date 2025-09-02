import streamlit as st

from auth import login
from db import init_db, upsert_initiative
from ui import load_css, create_draggable_matrix


def main() -> None:
    """Render the Streamlit dashboard used on Streamlit Cloud.

    The app no longer embeds a separate HTML/JS application or spins up
    an additional Flask API server.  Instead it interacts with the
    database directly and renders visualizations using Plotly.  This
    makes the app compatible with Streamlit Cloud which exposes only the
    main Streamlit port.
    """
    st.set_page_config(
        page_title="Lumen Strategic Dashboard",
        page_icon="⊙",
        layout="wide",
    )

    init_db()
    authenticator, authenticated = login()
    if not authenticated:
        st.stop()

    load_css()
    st.markdown("<div class='app-container'>", unsafe_allow_html=True)
    st.title("Lumen Strategic Dashboard")

    with st.sidebar:
        st.header("Add / Update Initiative")
        with st.form("initiative_form", clear_on_submit=True):
            initiative_id = st.number_input(
                "ID (leave 0 for new)", min_value=0, step=1, value=0
            )
            title = st.text_input("Title")
            details = st.text_area("Details")
            color = st.color_picker("Color", "#ff0000")
            category = st.text_input("Category")
            x = st.slider("Effort", 0, 100, 50)
            y = st.slider("Value", 0, 100, 50)
            submitted = st.form_submit_button("Save")
        if submitted and title:
            new_id = upsert_initiative(
                initiative_id if initiative_id else None,
                title,
                details,
                color,
                category,
                float(x),
                float(y),
                st.session_state.get("username", "user"),
            )
            st.success(f"Saved initiative {new_id}")
            st.rerun()


        authenticator.logout("Logout", "sidebar")

    create_draggable_matrix(st.session_state.get("username", "user"))
    st.markdown("</div>", unsafe_allow_html=True)



if __name__ == "__main__":
    main()
