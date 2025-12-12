import streamlit as st
import pandas as pd
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from my_app.repositories.user_repository import UserRepository
from my_app.services.user_service import UserService
from my_app.utilities.db_init import ensure_database_initialized

# Ensure database is initialized
ensure_database_initialized()

st.set_page_config(page_title="Login / Register", page_icon="🔑", layout="centered")

# Set light pink background for this page
st.markdown("""
    <style>
    .stApp {
        background-color: #FFE5F1 !important;
        background: #FFE5F1 !important;
    }
    .main .block-container {
        background-color: #FFE5F1 !important;
        background: #FFE5F1 !important;
    }
    body {
        background-color: #FFE5F1 !important;
        background: #FFE5F1 !important;
    }
    [data-testid="stSidebar"] {
        background-color: #FFDDF4 !important;
        background: #FFDDF4 !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        background-color: #FFDDF4 !important;
        background: #FFDDF4 !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #FFDDF4 !important;
        background: #FFDDF4 !important;
    }
    header[data-testid="stHeader"] {
        background-color: #FFE5F1 !important;
        background: #FFE5F1 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------- Initialise session state ----------
if "users" not in st.session_state:
    # Store user data: {username: {"password": pwd, "role": role}}
    st.session_state.users = {}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "user_role" not in st.session_state:
    st.session_state.user_role = ""

# Initialize services
# Use database for persistence, but fall back to session state if needed
user_repository = UserRepository(use_database=True)
user_service = UserService(user_repository)

# Role to page mapping
ROLE_PAGES = {
    "Cyber Security": "pages/1_cybersecurity.py",
    "Data Scientist": "pages/2_datascience.py",
    "IT Operations": "pages/3_IToperations.py"
}

st.title("🔐 Welcome")

# If already logged in, redirect to appropriate page
if st.session_state.logged_in and st.session_state.user_role:
    st.success(f"Already logged in as **{st.session_state.username}** ({st.session_state.user_role}).")
    if st.button("Go to dashboard"):
        page = ROLE_PAGES.get(st.session_state.user_role, "pages/1_cybersecurity.py")
        st.switch_page(page)
    st.stop()  # Don't show login/register again


# ---------- Tabs: Login / Register ----------
tab_login, tab_register = st.tabs(["Login", "Register"])

# ----- LOGIN TAB -----
with tab_login:
    st.subheader("Login")

    login_username = st.text_input("Username", key="login_username")
    login_password = st.text_input("Password", type="password", key="login_password")

    if st.button("Log in", type="primary"):
        user = user_service.login(login_username, login_password)
        if user:
            st.session_state.logged_in = True
            st.session_state.username = user.username
            st.session_state.user_role = user.role
            st.success(f"Welcome back, {login_username}! Redirecting to your dashboard...")

            # Redirect to appropriate page based on role
            page = ROLE_PAGES.get(st.session_state.user_role, "pages/1_cybersecurity.py")
            st.switch_page(page)
        else:
            st.error("Invalid username or password.")


# ----- REGISTER TAB -----
with tab_register:
    st.subheader("Register")

    new_username = st.text_input("Choose a username", key="register_username")
    new_password = st.text_input("Choose a password", type="password", key="register_password")
    confirm_password = st.text_input("Confirm password", type="password", key="register_confirm")
    user_role = st.selectbox(
        "Select your role",
        ["Cyber Security", "Data Scientist", "IT Operations"],
        key="register_role"
    )

    if st.button("Create account"):
        # Basic checks
        if not new_username or not new_password:
            st.warning("Please fill in all fields.")
        elif new_password != confirm_password:
            st.error("Passwords do not match.")
        else:
            # Use service to register user
            success, error_msg = user_service.register_user(new_username, new_password, user_role)
            if success:
                st.success(f"Account created for {user_role}! You can now log in from the Login tab.")
                st.info("Tip: go to the Login tab and sign in with your new account.")
            else:
                st.error(error_msg)
