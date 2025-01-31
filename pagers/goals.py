# pages/goals.py

import streamlit as st
from datetime import date, datetime, timedelta
import pandas as pd

# Import functions from the data package
from data import (
    get_user_by_username,
    get_categories,
    get_goals,
    add_goal,
    # You may need to implement update and delete functions in your data package
    # For this example, we'll assume they are called update_goal and delete_goal
    update_goal,
    delete_goal,
)

# Authentication check
def is_authenticated():
    return 'authenticated' in st.session_state and st.session_state['authenticated']

def get_current_user():
    if 'username' in st.session_state:
        return get_user_by_username(st.session_state['username'])
    else:
        return None

def goals_page():
    st.title("Goals Management")

    if not is_authenticated():
        st.warning("Please log in to manage your goals.")
        return

    user = get_current_user()
    if not user:
        st.error("User not found.")
        return

    user_id = user[0]  # Extract user_id from the tuple

    # Fetch categories
    categories = get_categories(user_id)
    category_dict = {None: 'Uncategorized'}
    for cat in categories:
        category_dict[cat[0]] = cat[1]  # category_id: name

    # Fetch goals
    goals = get_goals(user_id)

    # Map goals to DataFrame
    if goals:
        df_goals = pd.DataFrame(goals, columns=['goal_id', 'category_id', 'time_target', 'period', 'start_date', 'end_date'])
        df_goals['Category'] = df_goals['category_id'].map(category_dict)
        df_goals['Start Date'] = pd.to_datetime(df_goals['start_date']).dt.date
        df_goals['End Date'] = pd.to_datetime(df_goals['end_date']).dt.date if df_goals['end_date'].notnull().all() else None
    else:
        df_goals = pd.DataFrame(columns=['goal_id', 'Category', 'time_target', 'period', 'Start Date', 'End Date'])

    # Tabs for viewing and adding goals
    tab1, tab2 = st.tabs(["Current Goals", "Add New Goal"])

    with tab1:
        st.subheader("Current Goals")
        if not df_goals.empty:
            # Display goals with options to edit or delete
            for index, row in df_goals.iterrows():
                goal_id = row['goal_id']
                st.write(f"### {row['Category']} ({row['period']})")
                st.write(f"**Time Target:** {row['time_target']} mins")
                st.write(f"**Duration:** {row['Start Date']} to {row['End Date'] or 'Ongoing'}")
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("Edit", key=f"edit_{goal_id}"):
                        st.session_state[f"edit_goal_{goal_id}"] = True
                with col2:
                    if st.button("Delete", key=f"delete_{goal_id}"):
                        delete_goal(goal_id)
                        st.success("Goal deleted successfully.")
                        st.rerun()

                # Edit Goal Section
                if st.session_state.get(f"edit_goal_{goal_id}", False):
                    st.subheader("Edit Goal")
                    with st.form(key=f"edit_goal_form_{goal_id}"):
                        # Pre-fill the form with current values
                        category_options = ["Select Category"] + [cat[1] for cat in categories]
                        category_default = category_dict.get(row['category_id'], 'Select Category')
                        category_selection = st.selectbox("Category", category_options, index=category_options.index(category_default))
                        time_target = st.number_input("Time Target (mins)", min_value=1, value=int(row['time_target']))
                        period = st.selectbox("Period", ["Daily", "Weekly", "Monthly", "Custom"], index=["Daily", "Weekly", "Monthly", "Custom"].index(row['period']))
                        start_date = st.date_input("Start Date", value=row['Start Date'])
                        end_date = st.date_input("End Date", value=row['End Date'] or date.today())
                        submitted = st.form_submit_button("Update Goal")
                        if submitted:
                            if category_selection == "Select Category":
                                st.error("Please select a category.")
                            else:
                                # Map category selection to category_id
                                category_dict_reverse = {v: k for k, v in category_dict.items()}
                                category_id = category_dict_reverse.get(category_selection)
                                update_goal(
                                    goal_id=goal_id,
                                    category_id=category_id,
                                    time_target=time_target,
                                    period=period,
                                    start_date=start_date.isoformat(),
                                    end_date=end_date.isoformat() if end_date else None
                                )
                                st.success("Goal updated successfully.")
                                st.session_state[f"edit_goal_{goal_id}"] = False
                                st.rerun()

        else:
            st.info("No current goals. Add a new goal to get started.")

    with tab2:
        st.subheader("Add New Goal")
        with st.form(key="add_goal_form"):
            category_options = ["Select Category"] + [cat[1] for cat in categories]
            category_selection = st.selectbox("Category", category_options)
            time_target = st.number_input("Time Target (mins)", min_value=1)
            period = st.selectbox("Period", ["Daily", "Weekly", "Monthly", "Custom"])
            start_date = st.date_input("Start Date", value=date.today())
            end_date = st.date_input("End Date (Optional)", value=None)
            submitted = st.form_submit_button("Add Goal")
            if submitted:
                if category_selection == "Select Category":
                    st.error("Please select a category.")
                else:
                    # Map category selection to category_id
                    category_dict_reverse = {v: k for k, v in category_dict.items()}
                    category_id = category_dict_reverse.get(category_selection)
                    add_goal(
                        user_id=user_id,
                        category_id=category_id,
                        time_target=time_target,
                        period=period,
                        start_date_str=start_date.isoformat(),
                        end_date_str=end_date.isoformat() if end_date else None
                    )
                    st.success("Goal added successfully.")
                    st.rerun()

if __name__ == "__main__":
    goals_page()