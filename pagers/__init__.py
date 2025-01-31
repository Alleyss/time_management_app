# pages/__init__.py

from .dashboard import dashboard_page
from .time_tracking import time_tracking_page
from .analytics import analytics_page
from .goals import goals_page
from .settings import settings_page

__all__ = [
    'dashboard_page',
    'time_tracking_page',
    'analytics_page',
    'goals_page',
    'settings_page',
]