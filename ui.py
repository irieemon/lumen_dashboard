import streamlit as st
import json
import pandas as pd

from streamlit_elements import elements, dashboard, html, mui, sync
from streamlit_elements.core.callback import ElementsCallback

from db import get_initiatives, update_position, get_last_updated

def load_css() -> None:
    """Inject CSS to mimic the original HTML dashboard styling."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        html, body {
            margin: 0;
            padding: 0;
            height: 100%;
            min-height: 100vh;
        }

        div[data-testid="stApp"] {
            background: transparent;
        }

        div[data-testid="stAppViewContainer"] {
            padding: 0;
            background: transparent;
        }

        div[data-testid="stAppViewContainer"] > .main {
            padding: 0;
            background: transparent;
        }

        div[data-testid="stAppViewContainer"] > .main .block-container {
            padding: 0;
            margin: 0;
            background: transparent;
        }

        header[data-testid="stHeader"] {
            display: none;
        }

        /* Sidebar styling to match previous control panel look */
        div[data-testid="stSidebar"] {
            background: #f8f9fa;
            padding: 20px 10px;
        }

        div[data-testid="stSidebar"] * {
            font-family: 'Inter', sans-serif;
        }

        div[data-testid="stSidebar"] .stButton > button {
            width: 100%;
            border-radius: 5px;
            background: #667eea;
            color: white;
            border: none;
        }

        div[data-testid="stSidebar"] .stButton > button:hover {
            background: #5a67d8;
        }

        * {
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', sans-serif;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def create_draggable_matrix(username: str) -> None:
    """Render initiatives as draggable "post-it" notes."""
    df = get_initiatives()
    if df.empty:
        st.info("No initiatives added yet. Showing sample initiatives.")
        df = pd.DataFrame(
            [
                {"id": -1, "title": "Sample Initiative 1", "color": "#FFFB7D", "x": 20, "y": 80},
                {"id": -2, "title": "Sample Initiative 2", "color": "#FFD6A5", "x": 50, "y": 50},
                {"id": -3, "title": "Sample Initiative 3", "color": "#CBF3F0", "x": 80, "y": 20},
            ]
        )

    last_updated = get_last_updated()
    if "layout" not in st.session_state or st.session_state.get("layout_ts") != last_updated:
        st.session_state["layout"] = [
            dashboard.Item(str(row.id), x=int(row.x), y=int(row.y), w=10, h=6)
            for row in df.itertuples()
        ]
        st.session_state["layout_ts"] = last_updated

    layout = st.session_state.get("layout", [])

    with elements("board"):
        # ``dashboard.Grid`` acts as a context manager. The previous implementation
        # instantiated it without entering the context, which resulted in an empty
        # white canvas being rendered on Streamlit Cloud. By using ``with`` the
        # grid properly wraps each sticky note allowing them to display and drag.
        with dashboard.Grid(
            layout,
            onLayoutChange=sync("layout"),
            cols=100,
            rowHeight=5,
            isDraggable=True,
            isResizable=False,
            style={"width": "100%", "minHeight": 500},
        ):
            for row in df.itertuples():
                edit_callback = ElementsCallback(
                    lambda r_id=row.id: st.session_state.update(edit=r_id)
                )
                with html.div(
                    key=str(row.id),
                    style={
                        "backgroundColor": row.color or "#FFFB7D",
                        "width": "100%",
                        "height": "100%",
                        "padding": "8px",
                        "border": "1px solid #e0e0e0",
                        "borderRadius": "4px",
                        "boxShadow": "0 2px 4px rgba(0,0,0,0.2)",
                        "cursor": "move",
                        "userSelect": "none",
                    },
                    onDoubleClick=edit_callback,
                ):
                    mui.Typography(row.title, variant="body2")

    if "layout" in st.session_state:
        layout_json = json.dumps(st.session_state["layout"])
        if layout_json != st.session_state.get("_layout_snapshot"):
            st.session_state["_layout_snapshot"] = layout_json
            for item in st.session_state["layout"]:
                item_id = int(item["i"])
                if item_id > 0:
                    update_position(item_id, float(item["x"]), float(item["y"]), username)

    if "edit" in st.session_state:
        st.session_state["edit_initiative_id"] = int(st.session_state.pop("edit"))
        st.rerun()

