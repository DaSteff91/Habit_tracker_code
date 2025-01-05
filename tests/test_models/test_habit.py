from models.habit import Habit
from tests.utils.db import DatabaseConnectorTesting
from typing import Any

class TestHabit:
    """Test suite for Habit model"""
    
    # CRUD Operations
    def test_habit_creation(self, test_db: DatabaseConnectorTesting, sample_habit_data: dict[str, Any]):
        """Test creating a new habit with valid data"""
        habit = Habit.create(sample_habit_data, test_db)
        assert habit is not None
        assert habit.name == sample_habit_data['name']
        assert habit.category == sample_habit_data['category']
        assert habit.streak == 0
        assert habit.reset_count == 0

    def test_habit_read(self, test_db: DatabaseConnectorTesting, sample_habit_data: dict[str, Any]):
        """Test reading habit data"""
        habit = Habit.create(sample_habit_data, test_db)
        read_habit = Habit.get_by_id(habit.id, test_db)
        assert read_habit is not None
        assert read_habit.name == sample_habit_data['name']

    def test_habit_update(self, test_db: DatabaseConnectorTesting, sample_habit_data: dict[str, Any]):
        """Test updating habit fields"""
        habit = Habit.create(sample_habit_data, test_db)
        assert habit.update({'name': 'Updated Name'})
        updated = Habit.get_by_id(habit.id, test_db)
        assert updated.name == 'Updated Name'

    def test_habit_deletion(self, test_db: DatabaseConnectorTesting, sample_habit_data: dict[str, Any]):
        """Test habit deletion"""
        habit = Habit.create(sample_habit_data, test_db)
        habit_id = habit.id
        assert habit.delete()
        assert Habit.get_by_id(habit_id, test_db) is None

    # Streak Management
    def test_habit_streak_increment(self, test_db: DatabaseConnectorTesting, sample_habit_data: dict[str, Any]):
        """Test streak increment functionality"""
        habit = Habit.create(sample_habit_data, test_db)
        initial_streak = habit.streak
        assert habit.increment_streak()
        assert habit.streak == initial_streak + 1

    def test_habit_streak_reset(self, test_db: DatabaseConnectorTesting, sample_habit_data: dict[str, Any]):
        """Test streak reset functionality"""
        habit = Habit.create(sample_habit_data, test_db)
        habit.increment_streak()
        assert habit.reset_streak()
        assert habit.streak == 0
        assert habit.reset_count == 1

    # Validation Tests
    def test_invalid_habit_creation(self, test_db: DatabaseConnectorTesting):
        """Test creating habit with invalid data fails"""
        invalid_data = {'name': '', 'category': ''}
        habit = Habit.create(invalid_data, test_db)
        assert habit is None