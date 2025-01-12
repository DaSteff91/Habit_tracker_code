from models.task import Task
from models.habit import Habit
from controllers.task import TaskController
from tests.db import DatabaseConnectorTesting
from typing import Any
import pytest

class TestTask:
    """Test suite for Task model"""

    def test_db_setup(self, test_db):
        """Verify test database setup"""
        # Arrange
        assert isinstance(test_db, DatabaseConnectorTesting)
        assert test_db.db_name == "test.db"
        
        # Act
        tables = test_db.get_tables()
        
        # Assert
        assert 'task' in tables
        assert 'habit' in tables
   
    def test_initial_task_creation(self, test_db: DatabaseConnectorTesting, sample_habit_data: dict[str, Any]):
        """Test tasks are created with habit"""
        # Arrange
        habit = Habit.create(sample_habit_data, test_db)
        
        # Act - Pass test_db
        task = Task.create_from_habit(
            habit_id=habit.id,
            task_number=1,
            habit_data=sample_habit_data,
            db_controller=test_db
        )
        
        # Verify
        tasks = Task.get_tasks_for_habit(
            habit_id=habit.id,
            due_date=habit.start,
            db_controller=test_db
        )
        
        # Assert
        assert task is not None
        assert len(tasks) == 1


    def test_task_status_update(self, test_db: DatabaseConnectorTesting, sample_habit_data: dict[str, Any]):
        """Test updating task status"""
        # Arrange
        habit = Habit.create(sample_habit_data, test_db)
        task = Task.create_from_habit(
            habit_id=habit.id,
            task_number=1,
            habit_data=sample_habit_data,
            db_controller=test_db
        )
        
        # Act - Direct DB update
        success = test_db.update_data('task', task.id, {'status': 'done'})
        
        # Assert using test-specific method
        assert success
        updated_task = test_db.get_task_by_id(task.id)
        assert updated_task is not None
        assert updated_task['status'] == 'done'