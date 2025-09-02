import streamlit as st
import json
import pandas as pd

from streamlit_elements import elements, dashboard, html, mui, sync
from streamlit_elements.core.callback import ElementsCallback

from db import get_initiatives, update_position, get_last_updated

def load_css() -> None:
    """Inject base CSS for fonts and sidebar controls.

    The dashboard previously wrapped the page in a custom container with an
    explicit white background. That wrapper has been removed so the app uses the
    default Streamlit styling. Only minimal rules are kept here to match the
    project typography and button colours.
    """

    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        header[data-testid="stHeader"] { display: none; }

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

        h1 {
            background: #007bff;
            color: white;
            padding: 0.25em 0.5em;
            border-radius: 4px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def create_draggable_matrix(username: str) -> None:
    """Render initiatives as draggable notes over a visible 3×3 grid."""

    df = get_initiatives()
    if df.empty:
        # Show a few example items so the board always has content.
        df = pd.DataFrame(
            [
                {"id": -1, "title": "Example Initiative 1", "color": "#FFFB7D", "x": 25, "y": 75},
                {"id": -2, "title": "Example Initiative 2", "color": "#7DFBFF", "x": 50, "y": 50},
                {"id": -3, "title": "Example Initiative 3", "color": "#B3FF7D", "x": 75, "y": 25},
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
        board_style = {
            "position": "relative",
            "width": "100%",
            "height": "80vh",
            "backgroundColor": "#fafafa",
            # Draw vertical and horizontal lines at one-third and two-thirds.
            "backgroundImage": (
                "linear-gradient(to right, #666 2px, transparent 2px),"
                "linear-gradient(to right, #666 2px, transparent 2px),"
                "linear-gradient(to bottom, #666 2px, transparent 2px),"
                "linear-gradient(to bottom, #666 2px, transparent 2px)"
            ),
            "backgroundSize": "1px 100%, 1px 100%, 100% 1px, 100% 1px",
            "backgroundPosition": "33.33% 0, 66.66% 0, 0 33.33%, 0 66.66%",
            "backgroundRepeat": "no-repeat",
            "border": "1px solid #e0e0e0",
            "overflow": "hidden",
        }
        with html.div(style=board_style):
            with dashboard.Grid(
                layout,
                onLayoutChange=sync("layout"),
                cols=100,
                rowHeight=8,
                isDraggable=True,
                isResizable=False,
                style={
                    "position": "absolute",
                    "top": 0,
                    "left": 0,
                    "right": 0,
                    "bottom": 0,
                    "background": "transparent",
                    "zIndex": 1,
                },
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


            html.div(
                "Effort",
                style={
                    "position": "absolute",
                    "bottom": "-30px",
                    "left": "50%",
                    "transform": "translateX(-50%)",
                    "fontWeight": "bold",
                    "pointerEvents": "none",
                },
            )
            html.div(
                "Value",
                style={
                    "position": "absolute",
                    "top": "50%",
                    "left": "-40px",
                    "transform": "translateY(-50%) rotate(-90deg)",
                    "fontWeight": "bold",
                    "pointerEvents": "none",

                },
            )

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

