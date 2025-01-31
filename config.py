# config.py

import os

# Database configuration
DATABASE_NAME = 'timemanagement.db'

# Secret key for session management and other security-related operations
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')

# Time zone settings (default to UTC)
DEFAULT_TIMEZONE = 'UTC'

# Date format settings
DEFAULT_DATE_FORMAT = '%Y-%m-%d'

# Streamlit configuration
APP_NAME = 'Personal Time Management Dashboard'