from typing import Dict, List, Tuple, Any, Optional
from models.habit import Habit
from utils.validators import HabitValidator

class HabitController:
    def __init__(self):
        self.validator = HabitValidator()

    def create_habit(self, habit_data: Dict[str, Any]) -> Optional[int]:
        """Create habit with validation"""
        try:
            if not self.validator.validate_habit_data(habit_data):
                return None
            habit = Habit.create(habit_data)
            return habit.id if habit else None
        except Exception as e:
            print(f"Error creating habit: {e}")
            return None

    def update_habit(self, habit_id: int, field: str, value: str) -> bool:
        """Update habit with validation"""
        try:
            habit = Habit.get_by_id(habit_id)
            if not habit or not self.validator.validate_update(field, value):
                return False
            return habit.update({field: value})
        except Exception as e:
            print(f"Error updating habit: {e}")
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
            'start_date': habit.start_date,
            'end_date': habit.end_date,
            'tasks': habit.tasks,
            'streak': habit.streak,
            'reset_count': habit.reset_count,
            'status': habit.status
        }