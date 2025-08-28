import streamlit as st
import streamlit_authenticator as stauth

# Pre-hashed password for user "admin" with password "admin"
_CREDENTIALS = {
    "usernames": {
        "admin": {
            "name": "Admin",
            "password": "$2b$12$w5VqKNSI4kWgXurVeZ6AV.PXla59qqQm5yt62HRcKMD8uii98.3Ae",
        }
    }
}


def login() -> bool:
    """Render login form and return authentication status."""
    authenticator = stauth.Authenticate(
        _CREDENTIALS,
        "lumen_dashboard",
        "abcdef",
        cookie_expiry_days=1,
    )
    name, auth_status, username = authenticator.login("Login", "main")
    if auth_status:
        st.session_state["username"] = username
        authenticator.logout("Logout", "sidebar")
        return True
    elif auth_status is False:
        st.error("Invalid credentials")
    return False
