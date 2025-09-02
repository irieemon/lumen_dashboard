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

        /* Container mimicking the original centered white card */
        .app-container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 30px;
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
    fig.update_layout(
        yaxis=dict(scaleanchor="x", scaleratio=1, showgrid=False, zeroline=False),
        xaxis=dict(showgrid=False, zeroline=False),
        plot_bgcolor="#f8f9fa",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter"),
        margin=dict(l=40, r=40, t=40, b=40),
    )
    fig.add_hline(y=33, line_dash="dash", line_color="gray")
    fig.add_hline(y=66, line_dash="dash", line_color="gray")
    fig.add_vline(x=33, line_dash="dash", line_color="gray")
    fig.add_vline(x=66, line_dash="dash", line_color="gray")
    st.plotly_chart(fig, use_container_width=True)
