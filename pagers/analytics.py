import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date, timedelta

# Import functions from the data package
from data import (
    get_user_by_username,
    get_activities,
    get_categories,
    get_goals,
)
from utils.authentication import is_authenticated, get_current_user

def analytics_page():
    st.title("Productivity Analytics")

    if not is_authenticated():
        st.warning("Please log in to view analytics.")
        return

    user = get_current_user()
    if not user:
        st.error("User not found.")
        return

    user_id = user[0]  # Extract user_id from the tuple

    # Sidebar filters
    st.sidebar.header("Filter Data")

    # Date range selection
    today = date.today()
    default_start = today - timedelta(days=30)
    start_date = st.sidebar.date_input("Start Date", default_start)
    end_date = st.sidebar.date_input("End Date", today)

    if start_date > end_date:
        st.error("Error: End date must fall after start date.")
        return

    # Category selection
    categories = get_categories(user_id)
    category_options = ["All Categories"] + [cat[1] for cat in categories]
    selected_category = st.sidebar.selectbox("Select Category", category_options)

    # Fetch activities
    start_date_str = datetime.combine(start_date, datetime.min.time()).isoformat()
    end_date_str = datetime.combine(end_date, datetime.max.time()).isoformat()
    activities = get_activities(user_id, start_date=start_date_str, end_date=end_date_str)

    if not activities:
        st.info("No activities found for the selected date range.")
        return

    # Create DataFrame
    df = pd.DataFrame(activities, columns=['activity_id', 'category_id', 'name', 'start_time', 'end_time', 'duration', 'notes'])
    df['start_time'] = pd.to_datetime(df['start_time'])
    df['end_time'] = pd.to_datetime(df['end_time'])
    df['date'] = df['start_time'].dt.date

    # Map category IDs to names
    cat_dict = {None: 'Uncategorized'}
    for cat in categories:
        cat_dict[cat[0]] = cat[1]  # category_id: name

    df['category'] = df['category_id'].map(cat_dict)

    # Filter by category if selected
    if selected_category != "All Categories":
        df = df[df['category'] == selected_category]
        if df.empty:
            st.info(f"No activities found for the selected category '{selected_category}' and date range.")
            return

    # Total duration per category
    duration_per_category = df.groupby('category')['duration'].sum().reset_index()

    # Line chart of daily total durations
    daily_totals = df.groupby('date')['duration'].sum().reset_index()

    # Ensure 'start_time' is in datetime format
    df['start_time'] = pd.to_datetime(df['start_time'])

    # Create 'day_of_week' and 'hour' columns
    df['day_of_week'] = df['start_time'].dt.day_name()
    df['hour'] = df['start_time'].dt.hour

    # Prepare data for heatmap
    heatmap_data = df.groupby(['day_of_week', 'hour'])['duration'].sum().reset_index()

    # Reorder days of the week and ensure all days are included
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    heatmap_data['day_of_week'] = pd.Categorical(heatmap_data['day_of_week'], categories=days_order, ordered=True)

    # Pivot data for heatmap
    heatmap_pivot = heatmap_data.pivot(index="day_of_week", columns="hour", values="duration")

    # Reindex to include all days and hours
    all_hours = range(0, 24)
    heatmap_pivot = heatmap_pivot.reindex(index=days_order, columns=all_hours, fill_value=0)

    # Visualization
    st.header("Activity Heatmap")
    if not heatmap_pivot.empty:
        fig3 = px.imshow(
            heatmap_pivot.values,  # Use .values to get NumPy array
            labels=dict(x="Hour of Day", y="Day of Week", color="Total Duration (mins)"),
            x=list(all_hours),  # Convert range to list here
            y=days_order,
            aspect="auto",
            title='Activity Heatmap: Duration by Day and Hour'
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No data available to display the Activity Heatmap.")
    st.header("Daily Activity Duration")
    if not daily_totals.empty:
        fig2 = px.bar(daily_totals, x='date', y='duration', title='Total Time Spent Each Day')
        fig2.update_layout(xaxis_title='Date', yaxis_title='Total Duration (mins)')
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No data available to display the Daily Activity Duration chart.")

    # Visualization: Activity Heatmap
    st.header("Activity Heatmap")
    if not heatmap_pivot.empty:
        fig3 = px.imshow(
            heatmap_pivot,
            labels=dict(x="Hour of Day", y="Day of Week", color="Total Duration (mins)"),
            x=all_hours,
            y=days_order,
            aspect="auto",
            title='Activity Heatmap: Duration by Day and Hour'
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No data available to display the Activity Heatmap.")

    # Goals Progress
    st.header("Goals Progress")
    goals = get_goals(user_id)
    if goals:
        goal_df = pd.DataFrame(goals, columns=['goal_id', 'category_id', 'time_target', 'period', 'start_date', 'end_date'])
        # Map category IDs to names
        goal_df['category'] = goal_df['category_id'].map(cat_dict)
        # Calculate progress
        for index, row in goal_df.iterrows():
            goal_start = datetime.strptime(row['start_date'], '%Y-%m-%d').date()
            goal_end = datetime.strptime(row['end_date'], '%Y-%m-%d').date() if row['end_date'] else today
            # Adjust goal period based on 'period' field
            if row['period'] == 'Daily':
                period_start = max(goal_start, today)
                period_end = period_start
            elif row['period'] == 'Weekly':
                period_start = max(goal_start, today - timedelta(days=today.weekday()))
                period_end = period_start + timedelta(days=6)
            elif row['period'] == 'Monthly':
                period_start = max(goal_start, date(today.year, today.month, 1))
                next_month = today.replace(day=28) + timedelta(days=4)
                period_end = next_month - timedelta(days=next_month.day)
            else:
                period_start = goal_start
                period_end = goal_end
            # Filter activities within the goal period
            goal_activities = df[(df['date'] >= period_start) & (df['date'] <= period_end)]
            if row['category'] != 'Uncategorized':
                goal_activities = goal_activities[goal_activities['category'] == row['category']]
            total_time = goal_activities['duration'].sum()
            progress = (total_time / row['time_target']) * 100 if row['time_target'] > 0 else 0
            st.subheader(f"Goal: {row['category']} ({row['period']})")
            st.progress(min(progress / 100, 1.0))
            st.write(f"Progress: {total_time} mins / {row['time_target']} mins ({progress:.2f}%)")
    else:
        st.info("No goals found.")

    # Insights
    st.header("Insights")
    # Most Active Day
    if not daily_totals.empty:
        most_active_day = daily_totals.loc[daily_totals['duration'].idxmax()]
        st.write(f"**Most Active Day:** {most_active_day['date']} with {most_active_day['duration']} minutes spent.")
    else:
        st.write("No activity data to determine the most active day.")

    # Most Frequent Activity
    activity_counts = df['name'].value_counts()
    if not activity_counts.empty:
        most_common_activity = activity_counts.idxmax()
        st.write(f"**Most Frequent Activity:** {most_common_activity}")
    else:
        st.write("No activities to analyze.")

if __name__ == "__main__":
    analytics_page()
