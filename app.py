# app.py

import streamlit as st
from components.navbar import navbar
from pagers import (
    dashboard_page,
    time_tracking_page,
    analytics_page,
    goals_page,
    settings_page,
)
from utils.authentication import (
    login,
    signup,
    logout,
    is_authenticated,
    get_current_user,
)
from config import APP_NAME

def main():
    # Set the app title and layout
    st.set_page_config(page_title=APP_NAME, layout='wide')

    # Display the navigation bar and get the selected page
    selection = navbar()

    # Handle authentication pages separately
    if selection == 'Login':
        login()
        return
    elif selection == 'Sign Up':
        signup()
        return
    elif selection == 'Logout':
        logout()
        return

    # Map page names to their corresponding functions
    pages = {
        "Dashboard": dashboard_page,
        "Time Tracking": time_tracking_page,
        "Goals": goals_page,
        "Analytics": analytics_page,
        "Settings": settings_page,
    }

    # Check if the user is authenticated
    if not is_authenticated():
        st.warning("Please log in to access the application.")
        st.session_state['navigation'] = 'Login'
        st.rerun()
        return

    # Render the selected page
    page = pages.get(selection)
    if page:
        page()
    else:
        st.error("Page not found.")

if __name__ == "__main__":
    main()