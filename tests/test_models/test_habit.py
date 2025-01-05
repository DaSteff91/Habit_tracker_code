from models.habit import Habit
from tests.utils.db import TestDatabaseConnector
from typing import Any

def test_habit_creation(test_db: TestDatabaseConnector, sample_habit_data: dict[str, Any]):
    """Test creating a new habit with valid data"""
    habit = Habit.create(sample_habit_data, test_db)
    assert habit is not None
    assert habit.name == sample_habit_data['name']
    assert habit.category == sample_habit_data['category']
    assert habit.streak == 0
    assert habit.reset_count == 0

def test_habit_streak_increment(test_db: TestDatabaseConnector, sample_habit_data: dict[str, Any]):
    """Test streak increment functionality"""
    habit = Habit.create(sample_habit_data, test_db)
    initial_streak = habit.streak
    
    assert habit.increment_streak()
    assert habit.streak == initial_streak + 1
    
    # Check database persistence
    updated_habit = Habit.get_by_id(habit.id, test_db)
    assert updated_habit.streak == initial_streak + 1

def test_habit_streak_reset(test_db: TestDatabaseConnector, sample_habit_data: dict[str, Any]):
    """Test streak reset functionality"""
    habit = Habit.create(sample_habit_data, test_db)
    
    # First increment streak
    habit.increment_streak()
    assert habit.streak == 1
    
    # Then reset
    assert habit.reset_streak()
    assert habit.streak == 0
    assert habit.reset_count == 1

def test_invalid_habit_creation(test_db: TestDatabaseConnector):
    """Test creating habit with invalid data fails"""
    invalid_data = {'name': '', 'category': ''}  # Missing required fields
    habit = Habit.create(invalid_data, test_db)
    assert habit is None

def test_habit_update(sample_habit_data: dict[str, Any], test_db: TestDatabaseConnector):
    """Test updating habit fields"""
    # Create habit and store ID
    habit = Habit.create(sample_habit_data, test_db)
    assert habit is not None
    habit_id = habit.id
    
    # Update using returned habit object
    assert habit.update({'name': 'Updated Name'})
    
    # Verify update with fresh load
    updated = Habit.get_by_id(habit_id, test_db)
    assert updated.name == 'Updated Name'

def test_habit_deletion(test_db: TestDatabaseConnector, sample_habit_data: dict[str, Any]):
    """Test habit deletion"""
    habit = Habit.create(sample_habit_data, test_db)
    habit_id = habit.id
    assert habit.delete()
    assert Habit.get_by_id(habit_id, test_db) is None

def test_habit_validation(test_db: TestDatabaseConnector):
    """Test habit data validation"""
    invalid_cases = [
        {'name': '', 'category': 'Test'},  # Empty name
        {'name': 'Test', 'repeat': 'Invalid'},  # Invalid repeat
        {'name': 'Test', 'importance': 'Medium'}  # Invalid importance
    ]
    for invalid_data in invalid_cases:
        habit = Habit.create(invalid_data, test_db)
        assert habit is None