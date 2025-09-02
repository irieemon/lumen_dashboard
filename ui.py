import streamlit as st
import plotly.express as px

from db import get_initiatives


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
            background: linear-gradient(135deg, #555, #ddd);
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
        div.stButton > button:first-child {
            position: fixed;
            bottom: 0;
            left: 0;
            z-index: 1000;
            margin: 0;
            padding: 0.25rem 0.75rem;
            font-size: 0.8rem;
        }
        * {
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', sans-serif;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def create_draggable_matrix(username: str) -> None:
    """Display initiatives on a simple value/effort scatter plot."""
    df = get_initiatives()
    if df.empty:
        st.info("No initiatives added yet.")
        return

    fig = px.scatter(
        df,
        x="x",
        y="y",
        color="color",
        text="title",
        hover_data={"details": True, "category": True},
        labels={"x": "Effort", "y": "Value"},
        range_x=[0, 100],
        range_y=[0, 100],
    )
    fig.update_traces(textposition="top center")
    fig.update_layout(yaxis=dict(scaleanchor="x", scaleratio=1))
    fig.add_hline(y=33, line_dash="dash", line_color="gray")
    fig.add_hline(y=66, line_dash="dash", line_color="gray")
    fig.add_vline(x=33, line_dash="dash", line_color="gray")
    fig.add_vline(x=66, line_dash="dash", line_color="gray")
    st.plotly_chart(fig, use_container_width=True)
