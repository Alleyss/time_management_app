# data/database.py

import sqlite3
import os

# Database file name
DATABASE_NAME = 'timemanagement.db'

def create_connection():
    """Create a database connection to the SQLite database."""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        # Enable foreign key support
        conn.execute("PRAGMA foreign_keys = 1")
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def create_tables(conn):
    """Create tables in the SQLite database."""
    try:
        cursor = conn.cursor()
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash BLOB NOT NULL,
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
        print("Tables created successfully.")
    except sqlite3.Error as e:
        print(f"Error creating tables: {e}")
        conn.rollback()

def initialize_database():
    """Initialize the database and create tables if they don't exist."""
    if not os.path.exists(DATABASE_NAME):
        conn = create_connection()
        if conn is not None:
            create_tables(conn)
            conn.close()
            print("Database and tables created successfully.")
        else:
            print("Error! Cannot create the database connection.")
    else:
        # Optionally check if all tables exist and create any missing ones
        conn = create_connection()
        if conn is not None:
            # Check for missing tables and create them
            cursor = conn.cursor()
            tables = ['users', 'categories', 'activities', 'goals', 'settings']
            existing_tables = []
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            rows = cursor.fetchall()
            for row in rows:
                existing_tables.append(row[0])
            missing_tables = set(tables) - set(existing_tables)
            if missing_tables:
                create_tables(conn)
                print(f"Created missing tables: {missing_tables}")
            else:
                print("All tables already exist.")
            conn.close()
        else:
            print("Error! Cannot create the database connection.")

# Initialize the database when this module is imported
initialize_database()