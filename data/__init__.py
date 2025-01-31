# data/__init__.py

from .database import create_connection, initialize_database
from .models import (
    # Password hashing functions
    hash_password,
    verify_password,

    # User functions
    add_user,
    get_user_by_username,
    verify_user,

    # Category functions
    add_category,
    get_categories,
    update_category,
    delete_category,

    # Activity functions
    add_activity,
    get_activities,
    calculate_duration,

    # Goal functions
    add_goal,
    get_goals,
    update_goal,
    delete_goal,

    # Setting functions
    add_setting,
    get_settings,

    # Data Management functions
    export_user_data,
    import_user_data,
)

# Initialize the database when the package is imported
initialize_database()