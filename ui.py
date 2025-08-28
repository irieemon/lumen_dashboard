import streamlit as st
import plotly.express as px

from db import get_initiatives


def load_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        * { font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', sans-serif; }
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
