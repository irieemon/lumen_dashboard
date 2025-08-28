import streamlit as st
import streamlit_authenticator as stauth
from typing import Tuple

# Pre-hashed password for user "admin" with password "admin"
_CREDENTIALS = {
    "usernames": {
        "admin": {
            "name": "Admin",
            "password": "$2b$12$w5VqKNSI4kWgXurVeZ6AV.PXla59qqQm5yt62HRcKMD8uii98.3Ae",
        }
    }
}


def login() -> Tuple[stauth.Authenticate, bool]:
    """Render login form and return the authenticator and status."""
    authenticator = stauth.Authenticate(
        _CREDENTIALS,
        "lumen_dashboard",
        "abcdef",
        cookie_expiry_days=1,
    )
    authenticator.login(location="main", key="Login")
    auth_status = st.session_state.get("authentication_status")
    if auth_status:
        st.session_state["username"] = st.session_state.get("username")
    elif auth_status is False:
        st.error("Invalid credentials")
    return authenticator, bool(auth_status)
