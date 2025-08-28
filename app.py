import streamlit as st
from pathlib import Path

from auth import login
from db import init_db


def main() -> None:
    """Load and display the static index.html page after authentication."""
    st.set_page_config(
        page_title="Lumen Strategic Dashboard",
        page_icon="⊙",
        layout="wide",
    )

    init_db()
    authenticator, authenticated = login()
    if not authenticated:
        st.stop()
    authenticator.logout("Logout", "main")

    st.markdown(
        """
        <style>
            /* Remove Streamlit's default padding and background so the
               embedded dashboard can span edge-to-edge without a white border */
            div[data-testid="stAppViewContainer"] {
                padding: 0;
                background: transparent;
            }
            div[data-testid="stAppViewContainer"] > .main {
                padding: 0;
            }
            div[data-testid="stAppViewContainer"] > .main .block-container {
                padding: 0;
                margin: 0;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    index_path = Path(__file__).with_name("index.html")
    with index_path.open(encoding="utf-8") as f:
        html = f.read()

    st.components.v1.html(html, height=1000, scrolling=False)


if __name__ == "__main__":
    main()
