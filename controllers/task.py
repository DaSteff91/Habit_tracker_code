from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime
from models.task import Task
from utils.validators import TaskValidator
from controllers.habit import HabitController
from models.habit import Habit

class TaskController:
    """Task controller - coordinates model operations"""
    
    def __init__(self):
        """Initialize controller"""
        self.validator = TaskValidator()
        self.habit_controller = HabitController()
        self.status_map = {
            "Mark tasks as done": "done",
            "Mark tasks as ignored": "ignore",
            "Pause habit": "pause habit"
        }

    def get_pending_tasks(self) -> List[Dict]:
        """Get formatted pending tasks"""
        try:
            tasks = Task.get_pending()  # Tasks already filtered for pending
            return [self._format_task_data(task) for task in tasks]
        except Exception as e:
            print("Error getting pending tasks: {}".format(e))
            return []
    
    def get_related_tasks(self, task_id: int) -> List[int]:
        """Get tasks with same habit/date"""
        try:
            task = Task.get_by_id(task_id)
            if task:
                return Task.get_tasks_for_habit(task.habit_id, task.due_date)
            return []
        except Exception as e:
            print("Error getting related tasks: {}".format(e))
            return []
                
    def update_task_status(self, task_id: int, new_status: str) -> bool:
        """Coordinate task status update"""
        try:
            if not self.validator.validate_status(new_status):
                return False

            task = Task.get_by_id(task_id)
            if not task:
                return False

            success = task.update_status(new_status)

            if success:
                if new_status in ['done', 'ignore']:
                    return self._handle_next_series(task)
                return True
                
            return False

        except Exception as e:
            print("Error updating task status: {}".format(e))
            return False
    
    def _handle_next_series(self, task: Task) -> bool:
        """Handle creation of next task series"""
        try:
            habit_tasks = Task.get_tasks_for_habit(task.habit_id, task.due_date)
            all_done, all_handled = Task.check_completion_status(habit_tasks)
            
            # Handle streak updates
            if all_done:
                habit = Habit.get_by_id(task.habit_id)
                if habit:
                    habit.increment_streak()
            elif all_handled:  # Not all done but all handled
                habit = Habit.get_by_id(task.habit_id)
                if habit:
                    habit.reset_streak()
                    
            # Create next series if ALL tasks are handled (done OR ignored)
            if all_handled:
                return Task.create_next_series(task.habit_id, task.due_date, habit_tasks)
            return True
                
        except Exception as e:
            print("Error handling next series: {}".format(e))
            return False
        
    def _format_task_data(self, task: Task) -> Dict[str, Any]:
        """Format task data for UI"""
        return {
            'id': task.id,
            'habit_name': task.habit_name,
            'task_number': task.task_number,
            'description': task.task_description[:30],
            'due_date': task.due_date,
            'status': task.status,
            'completion_rate': task.get_completion_rate,
            'streak': task.get_streak
        }