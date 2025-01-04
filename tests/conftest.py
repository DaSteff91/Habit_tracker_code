import pytest
from datetime import datetime
import os
import sqlite3
from database.connector import DatabaseConnector
from database.operations import DatabaseController

@pytest.fixture
def test_db():
    """Provide test database connection"""
    db_name = "test.db"
    # Setup
    db = DatabaseConnector(db_name)
    db.create_tables()
    yield db
    # Teardown
    db.close()
    if os.path.exists(db_name):
        os.remove(db_name)

@pytest.fixture
def sample_habit_data():
    """Provide sample habit data"""
    return {
        'name': 'Test Habit',
        'category': 'Test',
        'description': 'Test Description',
        'start': '2024-01-01',
        'stop': '2024-12-31',
        'importance': 'High',
        'repeat': 'Daily',
        'tasks': 1,
        'tasks_description': 'Test Task'
    }

@pytest.fixture
def sample_task_data():
    """Provide sample task data"""
    return {
        'habit_id': 1,
        'task_number': 1,
        'task_description': 'Test Task',
        'due_date': '2024-01-01',
        'status': 'pending'
    }

@pytest.fixture
def test_db_with_habit(test_db, sample_habit_data):
    """Provide test database with sample habit"""
    db = DatabaseController("test.db")
    habit_id = db.create_data('habit', sample_habit_data)
    yield db, habit_id

@pytest.fixture
def test_db_with_tasks(test_db_with_habit, sample_task_data):
    """Provide test database with sample tasks"""
    db, habit_id = test_db_with_habit
    task_data = sample_task_data.copy()
    task_data['habit_id'] = habit_id
    task_id = db.create_data('task', task_data)
    yield db, habit_id, task_id