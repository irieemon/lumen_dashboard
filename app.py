import streamlit as st

from auth import login
from db import get_initiative, init_db, upsert_initiative
from ui import load_css, create_draggable_matrix


def main() -> None:
    """Render the Streamlit dashboard used on Streamlit Cloud.

    The app no longer embeds a separate HTML/JS application or spins up
    an additional Flask API server. Instead it interacts with the
    database directly and displays initiatives as draggable sticky notes
    using Streamlit Elements. This makes the app compatible with
    Streamlit Cloud which exposes only the main Streamlit port.
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
        edit_id = st.session_state.pop("edit_initiative_id", None)
        if edit_id:
            data = get_initiative(edit_id)
            if data:
                st.session_state["form_id"] = data["id"]
                st.session_state["form_title"] = data["title"]
                st.session_state["form_details"] = data.get("details", "")
                st.session_state["form_color"] = data.get("color", "#ff0000")
                st.session_state["form_category"] = data.get("category", "")
                st.session_state["form_x"] = int(data.get("x", 50))
                st.session_state["form_y"] = int(data.get("y", 50))

        with st.form("initiative_form", clear_on_submit=True):
            initiative_id = st.number_input(
                "ID (leave 0 for new)",
                min_value=0,
                step=1,
                value=int(st.session_state.get("form_id", 0)),
            )
            title = st.text_input("Title", value=st.session_state.get("form_title", ""))
            details = st.text_area("Details", value=st.session_state.get("form_details", ""))
            color = st.color_picker("Color", st.session_state.get("form_color", "#ff0000"))
            category = st.text_input("Category", value=st.session_state.get("form_category", ""))
            x = st.slider("Effort", 0, 100, st.session_state.get("form_x", 50))
            y = st.slider("Value", 0, 100, st.session_state.get("form_y", 50))
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
            for key in [
                "form_id",
                "form_title",
                "form_details",
                "form_color",
                "form_category",
                "form_x",
                "form_y",
            ]:
                st.session_state.pop(key, None)
            st.rerun()

        authenticator.logout("Logout", "sidebar")

    create_draggable_matrix(st.session_state.get("username", "user"))
    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
