# components/timers.py

import streamlit as st
import time
from datetime import datetime, timedelta
import threading

# Import necessary modules for custom components
import streamlit.components.v1 as components

# Initialize or update session state variables for timers
def init_timer_state(timer_id):
    """Initialize timer state variables."""
    if 'timers' not in st.session_state:
        st.session_state['timers'] = {}
    if timer_id not in st.session_state['timers']:
        st.session_state['timers'][timer_id] = {
            'timer_running': False,
            'start_time': None,
            'elapsed_time': timedelta(0),
            'activity_name': '',
            'category_id': None,
            'notes': ''
        }

def timer_component(timer_id, activity_name='', category_id=None, notes='', auto_start=False):
    """
    Render a timer component with start, pause, and reset functionality.

    Args:
        timer_id (str): Unique identifier for the timer instance.
        activity_name (str): Name of the activity.
        category_id (int): ID of the activity category.
        notes (str): Additional notes for the activity.
        auto_start (bool): If True, the timer starts immediately.
    """
    init_timer_state(timer_id)
    timer_state = st.session_state['timers'][timer_id]

    # Update activity details if provided
    if activity_name:
        timer_state['activity_name'] = activity_name
    if category_id is not None:
        timer_state['category_id'] = category_id
    if notes:
        timer_state['notes'] = notes

    st.subheader(f"Timer: {timer_state['activity_name'] or 'Unnamed Activity'}")

    # Timer Controls
    col1, col2, col3 = st.columns(3)
    with col1:
        if not timer_state['timer_running']:
            if st.button("Start", key=f"start_{timer_id}"):
                timer_state['timer_running'] = True
                timer_state['start_time'] = datetime.now()
        else:
            if st.button("Pause", key=f"pause_{timer_id}"):
                timer_state['timer_running'] = False
                timer_state['elapsed_time'] += datetime.now() - timer_state['start_time']
    with col2:
        if st.button("Reset", key=f"reset_{timer_id}"):
            timer_state['timer_running'] = False
            timer_state['start_time'] = None
            timer_state['elapsed_time'] = timedelta(0)
    with col3:
        st.write("")  # Placeholder for alignment

    # Calculate Elapsed Time
    if timer_state['timer_running']:
        elapsed = datetime.now() - timer_state['start_time'] + timer_state['elapsed_time']
    else:
        elapsed = timer_state['elapsed_time']

    # Format elapsed time
    total_seconds = int(elapsed.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    timer_display = f"{hours:02}:{minutes:02}:{seconds:02}"

    # Display Timer
    st.write(f"## {timer_display}")

    # Animated Timer Display
    animate_timer(elapsed, timer_display, timer_id)

    # Auto-refresh to update timer display
    if timer_state['timer_running']:
        time.sleep(1)
        st.rerun()

def animate_timer(elapsed, timer_display, timer_id):
    """
    Render an animated circular timer.

    Args:
        elapsed (timedelta): The elapsed time of the timer.
        timer_display (str): Formatted time string.
        timer_id (str): Unique identifier for the timer instance.
    """
    # Calculate progress (0 to 1) based on elapsed time
    progress = (elapsed.total_seconds() % 60) / 60  # Progress within a minute

    circle_timer = f"""
    <div class="circle" id="circle_{timer_id}">
      <div class="circle-inner">
        <div class="timer-text">{timer_display}</div>
      </div>
    </div>
    <style>
    #circle_{timer_id} {{
      position: relative;
      width: 200px;
      height: 200px;
      background: conic-gradient(#4caf50 {progress * 360}deg, #dddddd 0deg);
      border-radius: 50%;
    }}
    #circle_{timer_id} .circle-inner {{
      position: absolute;
      top: 10px;
      left: 10px;
      right: 10px;
      bottom: 10px;
      background: white;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
    }}
    #circle_{timer_id} .timer-text {{
      font-size: 2em;
      font-weight: bold;
    }}
    </style>
    """

    st.markdown(circle_timer, unsafe_allow_html=True)

def get_elapsed_time(timer_id):
    """
    Get the elapsed time for a timer.

    Args:
        timer_id (str): Unique identifier for the timer instance.

    Returns:
        timedelta: The elapsed time.
    """
    timer_state = st.session_state['timers'][timer_id]
    if timer_state['timer_running']:
        elapsed = datetime.now() - timer_state['start_time'] + timer_state['elapsed_time']
    else:
        elapsed = timer_state['elapsed_time']
    return elapsed

def stop_timer(timer_id):
    """
    Stop the timer and return the total elapsed time.

    Args:
        timer_id (str): Unique identifier for the timer instance.

    Returns:
        timedelta: The total elapsed time.
    """
    timer_state = st.session_state['timers'][timer_id]
    if timer_state['timer_running']:
        timer_state['timer_running'] = False
        timer_state['elapsed_time'] += datetime.now() - timer_state['start_time']
    return timer_state['elapsed_time']

def reset_timer(timer_id):
    """
    Reset the timer to zero.

    Args:
        timer_id (str): Unique identifier for the timer instance.
    """
    timer_state = st.session_state['timers'][timer_id]
    timer_state['timer_running'] = False
    timer_state['start_time'] = None
    timer_state['elapsed_time'] = timedelta(0)

def timer_active(timer_id):
    """
    Check if the timer is active.

    Args:
        timer_id (str): Unique identifier for the timer instance.

    Returns:
        bool: True if the timer is running, False otherwise.
    """
    timer_state = st.session_state['timers'][timer_id]
    return timer_state['timer_running']