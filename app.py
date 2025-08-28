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

    index_path = Path(__file__).with_name("index.html")
    with index_path.open(encoding="utf-8") as f:
        html = f.read()

    st.components.v1.html(html, height=0, scrolling=True)


if __name__ == "__main__":
    main()
