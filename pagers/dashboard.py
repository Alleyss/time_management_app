# pages/dashboard.py

import streamlit as st
from datetime import date, datetime, timedelta
import pandas as pd
import plotly.express as px

# Import functions from the data package
from data import (
    get_user_by_username,
    get_activities,
    get_categories,
    get_goals,
)

# Authentication check (assuming you have an authentication system)
def is_authenticated():
    return 'authenticated' in st.session_state and st.session_state['authenticated']

def get_current_user():
    if 'username' in st.session_state:
        return get_user_by_username(st.session_state['username'])
    else:
        return None

def dashboard_page():
    st.title("Dashboard")

    if not is_authenticated():
        st.warning("Please log in to view your dashboard.")
        return

    user = get_current_user()
    if not user:
        st.error("User not found.")
        return

    user_id = user[0]  # Extract user_id from the tuple

    # Fetch data
    today = date.today()
    start_of_today = datetime.combine(today, datetime.min.time())
    end_of_today = datetime.combine(today, datetime.max.time())

    # Today's Activities
    activities_today = get_activities(
        user_id,
        start_date=start_of_today.isoformat(),
        end_date=end_of_today.isoformat()
    )

    total_time_today = sum(activity[5] for activity in activities_today)  # Assuming duration is at index 5

    # Recent Activities (last 5 entries)
    recent_activities = get_activities(user_id)
    recent_activities = recent_activities[-5:] if recent_activities else []

    # Goals
    goals = get_goals(user_id)

    # Categories
    categories = get_categories(user_id)
    category_dict = {None: 'Uncategorized'}
    for cat in categories:
        category_dict[cat[0]] = cat[1]  # category_id: name

    # Display Summary Widgets
    st.subheader("Today's Summary")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Time Tracked Today (mins)", total_time_today)
    with col2:
        total_activities_today = len(activities_today)
        st.metric("Activities Tracked Today", total_activities_today)
    with col3:
        # Compute time remaining towards daily goals (if any)
        daily_goals = [goal for goal in goals if goal[3] == 'Daily']
        if daily_goals:
            time_target = sum(goal[2] for goal in daily_goals)  # time_target is at index 2
            time_spent = 0
            for goal in daily_goals:
                goal_activities = [activity for activity in activities_today if activity[1] == goal[1]]  # category_id matches
                time_spent += sum(activity[5] for activity in goal_activities)
            time_remaining = max(time_target - time_spent, 0)
            st.metric("Time Remaining Toward Daily Goals (mins)", time_remaining)
        else:
            st.metric("Time Remaining Toward Daily Goals (mins)", "No Goals Set")

    # Display Recent Activities
    st.subheader("Recent Activities")
    if recent_activities:
        df_recent = pd.DataFrame(recent_activities, columns=['activity_id', 'category_id', 'name', 'start_time', 'end_time', 'duration', 'notes'])
        df_recent['start_time'] = pd.to_datetime(df_recent['start_time'])
        df_recent['end_time'] = pd.to_datetime(df_recent['end_time'])
        df_recent['Category'] = df_recent['category_id'].map(category_dict)
        df_recent['Start'] = df_recent['start_time'].dt.strftime('%Y-%m-%d %H:%M')
        df_recent['End'] = df_recent['end_time'].dt.strftime('%Y-%m-%d %H:%M')
        st.table(df_recent[['name', 'Category', 'Start', 'End', 'duration', 'notes']].sort_values(by='Start', ascending=False).reset_index(drop=True))
    else:
        st.info("No recent activities.")

    # Display Goals Progress
    st.subheader("Goals Progress")
    if goals:
        for goal in goals:
            goal_id, category_id, time_target, period, start_date_str, end_date_str = goal[:6]
            goal_start = datetime.strptime(start_date_str, '%Y-%m-%d')
            goal_end = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else today
            # Fetch activities within the goal period
            activities_in_goal = get_activities(
                user_id,
                start_date=goal_start.isoformat(),
                end_date=(goal_end + timedelta(days=1)).isoformat()
            )
            # Filter by category if applicable
            if category_id:
                activities_in_goal = [act for act in activities_in_goal if act[1] == category_id]
            total_time = sum(act[5] for act in activities_in_goal)
            progress = (total_time / time_target) * 100 if time_target > 0 else 0
            category_name = category_dict.get(category_id, 'Uncategorized')
            st.subheader(f"Goal: {category_name} ({period})")
            st.progress(min(progress / 100, 1.0))
            st.write(f"Progress: {total_time} mins / {time_target} mins ({progress:.2f}%)")
    else:
        st.info("No goals found.")

    # Quick Actions
    st.subheader("Quick Actions")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Start a Timer"):
            st.session_state['navigation'] = 'Time Tracking'
            st.rerun()
    with col2:
        if st.button("Add a New Activity"):
            st.session_state['navigation'] = 'Add Activity'
            st.rerun()
    with col3:
        if st.button("Set a New Goal"):
            st.session_state['navigation'] = 'Goals'
            st.rerun()

    # Additional Insights or Visualizations
    st.subheader("Activity Distribution")
    # Fetch activities for the past 7 days
    start_date = today - timedelta(days=6)
    activities_week = get_activities(
        user_id,
        start_date=start_date.isoformat(),
        end_date=(today + timedelta(days=1)).isoformat()
    )
    if activities_week:
        df_week = pd.DataFrame(activities_week, columns=['activity_id', 'category_id', 'name', 'start_time', 'end_time', 'duration', 'notes'])
        df_week['date'] = pd.to_datetime(df_week['start_time']).dt.date
        daily_totals = df_week.groupby('date')['duration'].sum().reset_index()
        fig = px.bar(daily_totals, x='date', y='duration', title='Daily Total Time Spent (Last 7 Days)')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No activities found for the past week.")

if __name__ == "__main__":
    dashboard_page()