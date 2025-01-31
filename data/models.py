# models.py

import sqlite3
from datetime import datetime, date
import hashlib
import os
import pandas as pd

# Database file name
DATABASE_NAME = 'timemanagement.db'

def create_connection():
    """Create a database connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_NAME)
    # Enable foreign key support
    conn.execute("PRAGMA foreign_keys = 1")
    return conn

def create_tables():
    """Create tables in the SQLite database."""
    conn = create_connection()
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT
        )
    ''')

    # Create categories table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            UNIQUE (user_id, name)
        )
    ''')

    # Create activities table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            activity_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category_id INTEGER,
            name TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            duration INTEGER,
            notes TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE SET NULL
        )
    ''')

    # Create goals table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS goals (
            goal_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category_id INTEGER,
            time_target INTEGER NOT NULL,
            period TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE SET NULL
        )
    ''')

    # Create settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            setting_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            setting_name TEXT NOT NULL,
            setting_value TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            UNIQUE (user_id, setting_name)
        )
    ''')

    conn.commit()
    conn.close()

def hash_password(password):
    """Hash a password for storing."""
    # Use hashlib with salt for hashing passwords
    salt = os.urandom(32)  # A new salt for this user
    pwdhash = hashlib.pbkdf2_hmac(
        'sha256',          # The hash digest algorithm for HMAC
        password.encode('utf-8'),  # Convert the password to bytes
        salt,              # Provide the salt
        100000             # It is recommended to use at least 100,000 iterations of SHA-256
    )
    return salt + pwdhash  # Store salt with hash for later verification

def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user."""
    salt = stored_password[:32]  # Get the salt stored with the hash
    stored_hash = stored_password[32:]
    pwdhash = hashlib.pbkdf2_hmac(
        'sha256',
        provided_password.encode('utf-8'),
        salt,
        100000
    )
    return pwdhash == stored_hash

def add_user(username, email, password):
    """Add a new user to the database."""
    conn = create_connection()
    cursor = conn.cursor()
    password_hash = hash_password(password)
    try:
        cursor.execute('''
            INSERT INTO users (username, email, password_hash)
            VALUES (?, ?, ?)
        ''', (username, email, password_hash))
        conn.commit()
    except sqlite3.IntegrityError as e:
        print(f'Error: {e}')
        conn.rollback()
    finally:
        conn.close()

def get_user_by_username(username):
    """Retrieve a user by username."""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT user_id, username, email, password_hash FROM users WHERE username = ?
    ''', (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def verify_user(username, password):
    """Verify a user's credentials."""
    user = get_user_by_username(username)
    if user:
        user_id, username, email, stored_password = user
        if verify_password(stored_password, password):
            return True
    return False

def add_category(user_id, name, description=None):
    """Add a new category."""
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO categories (user_id, name, description)
            VALUES (?, ?, ?)
        ''', (user_id, name, description))
        conn.commit()
    except sqlite3.IntegrityError as e:
        print(f'Error: {e}')
        conn.rollback()
    finally:
        conn.close()

def get_categories(user_id):
    """Get categories for a user."""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT category_id, name, description FROM categories WHERE user_id = ?
    ''', (user_id,))
    categories = cursor.fetchall()
    conn.close()
    return categories

def add_activity(user_id, category_id, name, start_time, end_time, notes=None):
    """Add a new activity."""
    duration = calculate_duration(start_time, end_time)
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO activities (user_id, category_id, name, start_time, end_time, duration, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, category_id, name, start_time, end_time, duration, notes))
        conn.commit()
    except sqlite3.IntegrityError as e:
        print(f'Error: {e}')
        conn.rollback()
    finally:
        conn.close()

def get_activities(user_id, start_date=None, end_date=None):
    """Get activities for a user, optionally filtered by date range."""
    conn = create_connection()
    cursor = conn.cursor()
    query = '''
        SELECT activity_id, category_id, name, start_time, end_time, duration, notes
        FROM activities
        WHERE user_id = ?
    '''
    params = [user_id]
    if start_date:
        query += ' AND start_time >= ?'
        params.append(start_date)
    if end_date:
        query += ' AND end_time <= ?'
        params.append(end_date)
    cursor.execute(query, params)
    activities = cursor.fetchall()
    conn.close()
    return activities

def calculate_duration(start_time_str, end_time_str):
    """Calculate duration in minutes between start_time and end_time."""
    start_time = datetime.fromisoformat(start_time_str)
    end_time = datetime.fromisoformat(end_time_str)
    delta = end_time - start_time
    return int(delta.total_seconds() / 60)

def add_goal(user_id, category_id, time_target, period, start_date_str, end_date_str=None):
    """Add a new goal."""
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO goals (user_id, category_id, time_target, period, start_date, end_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, category_id, time_target, period, start_date_str, end_date_str))
        conn.commit()
    except sqlite3.Error as e:
        print(f'Error: {e}')
        conn.rollback()
    finally:
        conn.close()

def get_goals(user_id):
    """Get goals for a user."""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT goal_id, category_id, time_target, period, start_date, end_date
        FROM goals
        WHERE user_id = ?
    ''', (user_id,))
    goals = cursor.fetchall()
    conn.close()
    return goals

def add_setting(user_id, setting_name, setting_value):
    """Add or update a user setting."""
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO settings (user_id, setting_name, setting_value)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, setting_name) DO UPDATE SET setting_value=excluded.setting_value
        ''', (user_id, setting_name, setting_value))
        conn.commit()
    except sqlite3.Error as e:
        print(f'Error: {e}')
        conn.rollback()
    finally:
        conn.close()

def get_settings(user_id):
    """Get settings for a user."""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT setting_name, setting_value FROM settings WHERE user_id = ?
    ''', (user_id,))
    settings = cursor.fetchall()
    conn.close()
    return settings

# Additional functions for updating and deleting records can be added here.

# Function to initialize the database
def initialize_database():
    """Initialize the database and create tables."""
    if not os.path.exists(DATABASE_NAME):
        create_tables()
        print('Database and tables created successfully.')
    else:
        print('Database already exists.')

# data/models.py

def update_goal(goal_id, category_id, time_target, period, start_date, end_date=None):
    """Update an existing goal."""
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE goals
            SET category_id = ?, time_target = ?, period = ?, start_date = ?, end_date = ?
            WHERE goal_id = ?
        ''', (category_id, time_target, period, start_date, end_date, goal_id))
        conn.commit()
    except sqlite3.Error as e:
        print(f'Error updating goal: {e}')
        conn.rollback()
    finally:
        conn.close()

def delete_goal(goal_id):
    """Delete a goal."""
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM goals WHERE goal_id = ?', (goal_id,))
        conn.commit()
    except sqlite3.Error as e:
        print(f'Error deleting goal: {e}')
        conn.rollback()
    finally:
        conn.close()
# data/models.py

def update_category(category_id, name, description):
    """Update an existing category."""
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE categories
            SET name = ?, description = ?
            WHERE category_id = ?
        ''', (name, description, category_id))
        conn.commit()
    except sqlite3.Error as e:
        print(f'Error updating category: {e}')
        conn.rollback()
    finally:
        conn.close()

def delete_category(category_id):
    """Delete a category."""
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM categories WHERE category_id = ?', (category_id,))
        conn.commit()
    except sqlite3.Error as e:
        print(f'Error deleting category: {e}')
        conn.rollback()
    finally:
        conn.close()

# Setting-related functions
def add_setting(user_id, setting_name, setting_value):
    """Add or update a user setting."""
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO settings (user_id, setting_name, setting_value)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, setting_name) DO UPDATE SET setting_value=excluded.setting_value
        ''', (user_id, setting_name, setting_value))
        conn.commit()
    except sqlite3.Error as e:
        print(f'Error adding/updating setting: {e}')
        conn.rollback()
    finally:
        conn.close()

def get_settings(user_id):
    """Get all settings for a user."""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT setting_name, setting_value FROM settings WHERE user_id = ?
    ''', (user_id,))
    settings = cursor.fetchall()
    conn.close()
    return settings  # Returns a list of tuples
# data/models.py

def export_user_data(user_id):
    """Export all user data."""
    conn = create_connection()
    cursor = conn.cursor()

    # Export activities
    cursor.execute('''
        SELECT * FROM activities WHERE user_id = ?
    ''', (user_id,))
    activities = cursor.fetchall()
    activities_df = pd.DataFrame(activities, columns=['activity_id', 'user_id', 'category_id', 'name', 'start_time', 'end_time', 'duration', 'notes', 'created_at'])

    # Export categories
    cursor.execute('''
        SELECT * FROM categories WHERE user_id = ?
    ''', (user_id,))
    categories = cursor.fetchall()
    categories_df = pd.DataFrame(categories, columns=['category_id', 'user_id', 'name', 'description', 'created_at'])

    # Combine data into a single DataFrame or dictionary
    data = {
        'activities': activities_df,
        'categories': categories_df,
        # Include other data as needed
    }
    conn.close()
    return data  # Return as needed for download

def import_user_data(user_id, uploaded_file):
    """Import data from a CSV file."""
    # Read the CSV file into a DataFrame
    data_df = pd.read_csv(uploaded_file)

    conn = create_connection()
    cursor = conn.cursor()
    try:
        # Insert data into activities or categories tables accordingly
        # This is a simplified example; adjust column names as needed
        for index, row in data_df.iterrows():
            cursor.execute('''
                INSERT INTO activities (user_id, category_id, name, start_time, end_time, duration, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                row['category_id'],
                row['name'],
                row['start_time'],
                row['end_time'],
                row['duration'],
                row['notes']
            ))
        conn.commit()
    except sqlite3.Error as e:
        print(f'Error importing data: {e}')
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    # This block will run if the script is executed directly
    initialize_database()