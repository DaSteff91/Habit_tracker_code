from typing import Dict, List, Tuple, Any, Optional
from models.habit import Habit
from utils.validators import HabitValidator
from models.task import Task

class HabitController:
    def __init__(self):
        self.validator = HabitValidator()

    def create_habit(self, habit_data: Dict[str, Any]) -> Optional[int]:
        """Create habit with validation and task creation"""
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
            print(f"Error creating habit: {e}")
            return None

    def create_initial_tasks(self, habit_id: int, habit_data: Dict[str, Any]) -> bool:
        """Create initial set of tasks for new habit"""
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
            print(f"Error creating tasks: {e}")
            return False

    def update_habit(self, habit_id: int, field: str, value: str) -> bool:
        """Update habit with validation"""
        try:
            habit = Habit.get_by_id(habit_id)
            if not habit:
                return False
                
            field = field.lower().replace(' ', '_')
            if not self.validator.validate_update(field, value, habit_id):
                return False
                
            return habit.update({field: value})
        except Exception as e:
            print("Error updating habit: {}".format(e))
            return False

    def delete_habit(self, habit_id: int) -> bool:
        """Delete habit with validation"""
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