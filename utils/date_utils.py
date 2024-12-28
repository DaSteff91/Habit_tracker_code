from datetime import datetime, timedelta
from typing import Optional

def validate_date_format(date_str: str) -> bool:
    """Validate if string matches YYYY-MM-DD format"""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def calculate_days_between(start_date: str, end_date: str) -> Optional[int]:
    """Calculate days between two dates"""
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
        return (end - start).days
    except ValueError:
        return None

def get_next_date(current_date: str, repeat: str) -> Optional[str]:
    """Calculate next date based on repeat interval"""
    try:
        date = datetime.strptime(current_date, '%Y-%m-%d')
        if repeat == 'Daily':
            next_date = date + timedelta(days=1)
        elif repeat == 'Weekly':
            next_date = date + timedelta(weeks=1)
        else:
            return None
        return next_date.strftime('%Y-%m-%d')
    except ValueError:
        return None

def is_date_in_future(date_str: str) -> bool:
    """Check if date is in the future"""
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        return date > datetime.now().date()
    except ValueError:
        return False

def format_datetime(dt: datetime) -> str:
    """Format datetime to standard string format"""
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def get_days_passed(start_date: str) -> int:
    """Calculate days passed since start date"""
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        today = datetime.now().date()
        if start > today:
            return 0
        return (today - start).days
    except ValueError:
        return 0