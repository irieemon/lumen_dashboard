from streamlit_elements import elements, mui, dashboard
import streamlit as st

from db import get_initiatives, update_position


def load_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        * { font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', sans-serif; }
        .drag-handle { cursor: move; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def create_draggable_matrix(username: str) -> None:
    df = get_initiatives()
    layout = []
    for _, row in df.iterrows():
        grid_x = int((row["x"] / 100) * 12)
        grid_y = int(((100 - row["y"]) / 100) * 12)
        layout.append(dashboard.Item(str(row["id"]), grid_x, grid_y, 1, 1))

    def handle_layout_change(updated_layout):
        for item in updated_layout:
            x = (item["x"] / 12) * 100
            y = 100 - (item["y"] / 12) * 100
            update_position(int(item["i"]), x, y, username)
        st.rerun()

    with elements("matrix"):
        with dashboard.Grid(
            layout,
            rowHeight=50,
            cols=12,
            width=800,
            margin=[0, 0],
            containerPadding=[0, 0],
            draggableHandle=".drag-handle",
            onLayoutChange=handle_layout_change,
        ):
            for _, row in df.iterrows():
                with mui.Paper(
                    key=str(row["id"]),
                    className="drag-handle",
                    elevation=3,
                    sx={"padding": "8px", "background": "#f5f5f7"},
                ):
                    mui.Typography(row["title"], variant="body2")
