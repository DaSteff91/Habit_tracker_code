import pytest
import os
from tests.db import DatabaseConnectorTesting
from datetime import datetime

@pytest.fixture
def test_db():
    """Provide test database connection"""
    db_name = "test.db"
    db = DatabaseConnectorTesting(db_name)
    db.connect()
    yield db
    # Teardown
    db.close()
    if os.path.exists(db_name):
        os.remove(db_name)

@pytest.fixture
def sample_habit_data():
    """Provide complete sample habit data"""
    return {
        'name': 'Test Habit',
        'category': 'Health',
        'description': 'Test Description',
        'start': '2024-01-01',
        'end': '2024-12-31',     
        'importance': 'High',
        'repeat': 'Daily',
        'tasks': 1,
        'tasks_description': 'Test Task',
        'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'streak': 0,
        'streak_reset_count': 0,
        'longest_streak': 0
    }

@pytest.fixture
def sample_task_data():
    """Provide sample task data"""
    return {
        'habit_id': 1,
        'task_number': 1,
        'task_description': 'Test Task',
        'due_date': '2024-01-01'
    }
