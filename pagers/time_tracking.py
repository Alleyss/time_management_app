# pages/time_tracking.py

import streamlit as st
from datetime import datetime, timedelta
from data import (
    get_user_by_username,
    add_activity,
    get_categories,
)
from components.timers import timer_component, stop_timer, reset_timer

def is_authenticated():
    return 'authenticated' in st.session_state and st.session_state['authenticated']

def get_current_user():
    if 'username' in st.session_state:
        return get_user_by_username(st.session_state['username'])
    else:
        return None

def time_tracking_page():
    st.title("Real-Time Time Tracking")

    if not is_authenticated():
        st.warning("Please log in to access the time tracker.")
        return

    user = get_current_user()
    if not user:
        st.error("User not found.")
        return

    user_id = user[0]  # Extract user_id from the tuple

    # Initialize activity details in session state
    if 'activity_name' not in st.session_state:
        st.session_state['activity_name'] = ''
    if 'category_selection' not in st.session_state:
        st.session_state['category_selection'] = 'Select Category'
    if 'notes' not in st.session_state:
        st.session_state['notes'] = ''

    st.subheader("Activity Details")

    # Activity Details Form
    with st.form(key='activity_form'):
        activity_name_input = st.text_input("Activity Name", value=st.session_state['activity_name'], key='activity_name_input')
        categories = get_categories(user_id)
        if not categories:
            st.warning("No categories found. Please add categories in the Settings page.")
            return
        category_options = ["Select Category"] + [cat[1] for cat in categories]
        category_selection_input = st.selectbox("Category", category_options, index=category_options.index(st.session_state['category_selection']), key='category_selection_input')
        notes_input = st.text_area("Notes", value=st.session_state['notes'], key='notes_input')
        submitted = st.form_submit_button("Update Activity Details")
        if submitted:
            if not activity_name_input:
                st.error("Please enter an activity name.")
            elif category_selection_input == "Select Category":
                st.error("Please select a category.")
            else:
                # Update session state variables
                st.session_state['activity_name'] = activity_name_input
                st.session_state['category_selection'] = category_selection_input
                st.session_state['notes'] = notes_input
                st.success("Activity details updated.")

    # Retrieve category_id from the selection
    category_dict = {cat[1]: cat[0] for cat in categories}
    category_id = category_dict.get(st.session_state['category_selection'])

    # Render the timer component
    timer_component(
        timer_id='main_timer',
        activity_name=st.session_state['activity_name'],
        category_id=category_id,
        notes=st.session_state['notes']
    )

    # Stop and Save Activity Button
    if st.button("Stop and Save Activity"):
        if st.session_state['activity_name'] == '' or category_id is None:
            st.error("Please provide activity name and category before saving.")
        else:
            # Stop the timer and get elapsed time
            elapsed_time = stop_timer('main_timer')
            timer_state = st.session_state['timers']['main_timer']
            start_time = timer_state['start_time']
            end_time = datetime.now()

            # Save activity to database
            add_activity(
                user_id=user_id,
                category_id=category_id,
                name=st.session_state['activity_name'],
                start_time=start_time.isoformat(),
                end_time=end_time.isoformat(),
                notes=st.session_state['notes']
            )
            st.success(f"Activity '{st.session_state['activity_name']}' saved.")

            # Reset timer and activity details
            reset_timer('main_timer')
            # Reset session state variables
            st.session_state['activity_name'] = ''
            st.session_state['category_selection'] = 'Select Category'
            st.session_state['notes'] = ''
            # Rerun the script to update widgets
            st.rerun()

    # Optional: Provide a Reset Activity Details Button
    if st.button("Reset Activity Details"):
        # Reset session state variables
        st.session_state['activity_name'] = ''
        st.session_state['category_selection'] = 'Select Category'
        st.session_state['notes'] = ''
        # Rerun the script to update widgets
        st.rerun()

if __name__ == "__main__":
    time_tracking_page()