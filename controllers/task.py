from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime
from models.task import Task
from utils.validators import TaskValidator
from controllers.habit import HabitController

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
                
    def update_task_status(self, task_id: int, new_status: str) -> bool:
        """Coordinate task status update"""
        try:
            if not self.validator.validate_status(new_status):
                return False

            task = Task.get_by_id(task_id)
            if not task:
                return False

            if not task.update_status(new_status):
                return False

            # Handle next task series creation if needed
            if new_status in ['done', 'ignore']:
                return self._handle_next_series(task)
            return True
        except Exception as e:
            print("Error updating task status: {}".format(e))
            return False

    def _handle_next_series(self, task: Task) -> bool:
        """Handle creation of next task series"""
        habit_tasks = Task.get_tasks_for_habit(task.habit_id, task.due_date)
        all_done, all_handled = Task.check_completion_status(habit_tasks)
        
        if all_handled:
            return Task.create_next_series(
                task.habit_id,
                task.due_date,
                habit_tasks
            )
        return True
    
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