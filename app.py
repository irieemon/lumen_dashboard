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
    st.markdown(
        """
        <style>
            /* Make the entire Streamlit page adopt the dashboard background */
            html, body {
                margin: 0;
                padding: 0;
                height: 100%;
                min-height: 100vh;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }

            div[data-testid="stApp"] {
                background: transparent;
            }

            /* Remove Streamlit's default padding so the iframe reaches the edges */
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
            /* Hide Streamlit's default header to remove extra white space */
            header[data-testid="stHeader"] {
                display: none;
            }

            /* Fix the logout button to the bottom-left corner */
            div.stButton > button:first-child {
                position: fixed;
                bottom: 20px;
                left: 20px;
                z-index: 1000;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    index_path = Path(__file__).with_name("index.html")
    with index_path.open(encoding="utf-8") as f:
        html = f.read()

    st.components.v1.html(html, height=1000, scrolling=False)

    # Place logout button below the dashboard instead of at the top
    authenticator.logout("Logout", "main")


if __name__ == "__main__":
    main()
