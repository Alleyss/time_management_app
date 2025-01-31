# utils/authentication.py

import streamlit as st
from data import get_user_by_username, add_user
from data.models import verify_user

def login():
    """Handle user login."""
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    if st.button("Login"):
        if verify_user(username, password):
            st.success("Logged in successfully!")
            st.session_state['authenticated'] = True
            st.session_state['username'] = username
            # Redirect to the dashboard or another page
            st.rerun()
        else:
            st.error("Invalid username or password.")

def logout():
    """Handle user logout."""
    if 'authenticated' in st.session_state and st.session_state['authenticated']:
        st.session_state['authenticated'] = False
        st.session_state.pop('username', None)
        st.success("Logged out successfully.")
        # Redirect to the login page or home
        st.rerun()

def signup():
    """Handle user registration."""
    st.title("Sign Up")
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type='password')
    password_confirm = st.text_input("Confirm Password", type='password')
    if st.button("Sign Up"):
        if password != password_confirm:
            st.error("Passwords do not match.")
        elif get_user_by_username(username):
            st.error("Username already exists.")
        else:
            add_user(username, email, password)
            st.success("User registered successfully! Please log in.")
            # Redirect to the login page
            st.session_state['navigation'] = 'Login'
            st.rerun()

def is_authenticated():
    """Check if the user is authenticated."""
    return 'authenticated' in st.session_state and st.session_state['authenticated']

def get_current_user():
    """Get the current logged-in user."""
    if 'username' in st.session_state:
        return get_user_by_username(st.session_state['username'])
    else:
        return None

def require_auth(func):
    """Decorator to require authentication for a function."""
    def wrapper(*args, **kwargs):
        if not is_authenticated():
            st.warning("Please log in to access this page.")
            st.stop()
        else:
            return func(*args, **kwargs)
    return wrapper