from typing import Dict, List, Tuple, Any, Optional
from models.habit import Habit
from utils.validators import HabitValidator
from models.task import Task

class HabitController:
    def __init__(self):
        self.validator = HabitValidator()

    def create_habit(self, habit_data: Dict[str, Any]) -> Optional[int]:
        """Creates a new habit and its associated initial tasks.
        This method handles the creation of a new habit and its associated tasks in one transaction.
        If any part of the creation process fails, the entire operation is rolled back.

        Args:
            habit_data (Dict[str, Any]): A dictionary containing the habit information with the following keys:
                - name (str): The name of the habit
                - description (str): A description of the habit
                - frequency (str): How often the habit should be performed
                - start (datetime): When the habit should start
                - other habit-specific parameters as needed
        Returns:
            Optional[int]: The ID of the newly created habit if successful, None if creation fails
                or validation errors occur.
        Raises:
            Exception: If there is an unexpected error during habit creation. The exception 
        """
        
        try:
            if not self.validator.validate_habit_data(habit_data):
                return None
                
            # Create habit    
            habit = Habit.create(habit_data)
            if not habit:
                return None
                
            # Create associated tasks
            success = self.create_initial_tasks(habit.id, habit_data)
            if not success:
                # Rollback habit creation
                habit.delete()
                return None
                
            return habit.id
        except Exception as e:
            print("Error creating habit: {}".format(e))
            return None

    def create_initial_tasks(self, habit_id: int, habit_data: Dict[str, Any]) -> bool:
        """
        Creates initial tasks for a given habit based on habit data.

        This method generates a series of Task objects based on the provided habit data.
        Each task is associated with the given habit_id and numbered sequentially.

        Args:
            habit_id (int): The unique identifier of the habit to create tasks for.
            habit_data (Dict[str, Any]): Dictionary containing habit information including:
                - tasks (int): Number of tasks to create
        Returns:
            bool: True if all tasks were created successfully, False if any task creation failed
                  or if an exception occurred during the process.
        """

        try:
            for task_num in range(1, habit_data['tasks'] + 1):
                task = Task.create_from_habit(
                    habit_id=habit_id,
                    task_number=task_num,
                    habit_data=habit_data
                )
                if not task:
                    return False
            return True
        except Exception as e:
            print("Error creating tasks: {}".format(e))
            return False

    def update_habit(self, habit_id: int, field: str, value: str) -> bool:
        """Updates a specific field of a habit with a given value.
        This method updates a single field of a habit identified by its ID. It validates the field
        and value before performing the update.
        Args:
            habit_id (int): The unique identifier of the habit to update.
            field (str): The name of the field to update (case-insensitive, spaces converted to underscores).
            value (str): The new value to set for the specified field.
        Returns:
            bool: True if the update was successful, False if the habit doesn't exist,
                  validation fails, or an error occurs during the update.
        """

        try:
            habit = Habit.get_by_id(habit_id)
            if not habit:
                return False
                
            is_valid, message = self.validator.validate_update(field, value, habit_id)
            if not is_valid:
                print("\nValidation error: {}".format(message))
                return False
                
            return habit.update({field: value})
        except Exception as e:
            print("Error updating habit: {}".format(e))
            return False

    def delete_habit(self, habit_id: int) -> bool:
        """
        Delete a habit from the database.
        Args:
            habit_id (int): The unique identifier of the habit to be deleted.
        Returns:
            bool: True if the habit was successfully deleted, False if the habit wasn't found
                  or if an error occurred during deletion.
        """

        try:
            habit = Habit.get_by_id(habit_id)
            if not habit:
                return False
            return habit.delete()
        except Exception as e:
            print(f"Error deleting habit: {e}")
            return False
        
    def get_habits(self) -> List[Dict]:
        """Get all habits through model"""
        try:
            habits = Habit.get_all()
            if not habits:
                return []
            return [self._format_habit_data(habit) for habit in habits]
        except Exception as e:
            print(f"Error getting habits: {e}")
            return []
            
    def _format_habit_data(self, habit: Habit) -> Dict[str, Any]:
        """Format habit data for UI"""
        return {
            'id': habit.id,
            'name': habit.name,
            'category': habit.category,
            'description': habit.description[:30],
            'importance': habit.importance,
            'repeat': habit.repeat,
            'start': habit.start,
            'end': habit.end,
            'tasks': habit.tasks,
            'streak': habit.streak,
            'reset_count': habit.reset_count,
            'status': habit.status
        }