# components/visualizations.py

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import numpy as np

def plot_time_distribution_by_category(df, category_dict):
    """
    Creates a pie chart showing the distribution of time spent per category.

    Args:
        df (pd.DataFrame): DataFrame containing activity data with 'duration' and 'category_id' columns.
        category_dict (dict): Dictionary mapping category_id to category_name.
    """
    df['category'] = df['category_id'].map(category_dict)
    duration_per_category = df.groupby('category')['duration'].sum().reset_index()

    fig = px.pie(
        duration_per_category,
        names='category',
        values='duration',
        title='Time Distribution by Category',
        hole=0.4
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)

def plot_daily_activity_duration(df):
    """
    Creates a bar chart showing total time spent on activities each day.

    Args:
        df (pd.DataFrame): DataFrame containing activity data with 'duration' and 'date' columns.
    """
    daily_totals = df.groupby('date')['duration'].sum().reset_index()

    fig = px.bar(
        daily_totals,
        x='date',
        y='duration',
        title='Total Time Spent Each Day',
        labels={'date': 'Date', 'duration': 'Duration (mins)'}
    )
    fig.update_layout(xaxis_title='Date', yaxis_title='Total Duration (mins)')
    st.plotly_chart(fig, use_container_width=True)

def plot_activity_heatmap(df):
    """
    Creates a heatmap of activity duration by day of the week and hour of the day.

    Args:
        df (pd.DataFrame): DataFrame containing activity data with 'duration', 'day_of_week', and 'hour' columns.
    """
    # Prepare data for heatmap
    heatmap_data = df.groupby(['day_of_week', 'hour'])['duration'].sum().reset_index()

    # Reorder days of the week
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    heatmap_data['day_of_week'] = pd.Categorical(heatmap_data['day_of_week'], categories=days_order, ordered=True)

    # Pivot data for heatmap
    heatmap_pivot = heatmap_data.pivot('day_of_week', 'hour', 'duration').fillna(0)

    fig = px.imshow(
        heatmap_pivot,
        labels=dict(x="Hour of Day", y="Day of Week", color="Total Duration (mins)"),
        x=np.arange(0, 24),
        y=days_order,
        aspect="auto",
        title='Activity Heatmap: Duration by Day and Hour',
        color_continuous_scale='Viridis'
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_goal_progress(goals_df, activities_df, category_dict, today):
    """
    Displays goal progress bars and details.

    Args:
        goals_df (pd.DataFrame): DataFrame containing goals data.
        activities_df (pd.DataFrame): DataFrame containing activities data.
        category_dict (dict): Dictionary mapping category_id to category_name.
        today (datetime.date): Current date.
    """
    for index, row in goals_df.iterrows():
        goal_start = datetime.fromisoformat(row['start_date']).date()
        goal_end = datetime.fromisoformat(row['end_date']).date() if pd.notnull(row['end_date']) else today

        # Filter activities within goal period
        goal_activities = activities_df[
            (activities_df['date'] >= goal_start) & (activities_df['date'] <= goal_end)
        ]

        if row['category_id'] is not None:
            goal_activities = goal_activities[goal_activities['category_id'] == row['category_id']]

        total_time = goal_activities['duration'].sum()
        progress = (total_time / row['time_target']) * 100 if row['time_target'] > 0 else 0

        category_name = category_dict.get(row['category_id'], 'Uncategorized')
        st.subheader(f"Goal: {category_name} ({row['period']})")
        st.progress(min(progress / 100, 1.0))
        st.write(f"Progress: {total_time} mins / {row['time_target']} mins ({progress:.2f}%)")

def plot_activity_distribution(df, category_dict):
    """
    Creates a stacked bar chart showing the distribution of time spent on activities per day.

    Args:
        df (pd.DataFrame): DataFrame containing activity data with 'duration', 'date', and 'category_id' columns.
        category_dict (dict): Dictionary mapping category_id to category_name.
    """
    df['category'] = df['category_id'].map(category_dict)
    daily_category_totals = df.groupby(['date', 'category'])['duration'].sum().reset_index()

    fig = px.bar(
        daily_category_totals,
        x='date',
        y='duration',
        color='category',
        title='Daily Activity Distribution by Category',
        labels={'date': 'Date', 'duration': 'Duration (mins)', 'category': 'Category'}
    )
    fig.update_layout(barmode='stack')
    st.plotly_chart(fig, use_container_width=True)

def plot_weekly_trends(df):
    """
    Creates a line chart showing the trends of total time spent per week.

    Args:
        df (pd.DataFrame): DataFrame containing activity data with 'duration' and 'week' columns.
    """
    weekly_totals = df.groupby('week')['duration'].sum().reset_index()

    fig = px.line(
        weekly_totals,
        x='week',
        y='duration',
        title='Weekly Trends of Total Time Spent',
        labels={'week': 'Week Number', 'duration': 'Total Duration (mins)'}
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_category_pie_chart(df):
    """
    Creates a pie chart showing the percentage of time spent on each category.

    Args:
        df (pd.DataFrame): DataFrame containing activity data with 'category' and 'duration' columns.
    """
    duration_per_category = df.groupby('category')['duration'].sum().reset_index()

    fig = px.pie(
        duration_per_category,
        names='category',
        values='duration',
        title='Percentage of Time Spent per Category',
        hole=0.3
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)

def plot_monthly_activity(df):
    """
    Creates a bar chart showing total time spent on activities each month.

    Args:
        df (pd.DataFrame): DataFrame containing activity data with 'duration' and 'month' columns.
    """
    monthly_totals = df.groupby('month')['duration'].sum().reset_index()

    fig = px.bar(
        monthly_totals,
        x='month',
        y='duration',
        title='Total Time Spent Each Month',
        labels={'month': 'Month', 'duration': 'Duration (mins)'}
    )
    st.plotly_chart(fig, use_container_width=True)