# components/navbar.py

import streamlit as st
from utils.authentication import is_authenticated

def navbar():
    """Render the navigation bar."""
    st.sidebar.title("Navigation")

    # Check if 'navigation' is in session_state; if not, initialize it
    if 'navigation' not in st.session_state:
        st.session_state['navigation'] = 'Login'  # Default to Login page

    # Define the available pages based on authentication status
    if is_authenticated():
        pages = {
            "Dashboard": "Dashboard",
            "Time Tracking": "Time Tracking",
            "Goals": "Goals",
            "Analytics": "Analytics",
            "Settings": "Settings",
            "Logout": "Logout",
        }
    else:
        pages = {
            "Login": "Login",
            "Sign Up": "Sign Up",
        }

    # Available page values
    page_names = list(pages.values())

    # Ensure the current navigation choice is valid
    if st.session_state['navigation'] not in page_names:
        # If not valid, reset it to the first available page
        st.session_state['navigation'] = page_names[0]

    # Create the navigation radio button in the sidebar
    selection = st.sidebar.radio(
        "Go to",
        options=page_names,
        index=page_names.index(st.session_state['navigation'])
    )

    # Update the session state with the selected navigation option
    st.session_state['navigation'] = selection

    return selection