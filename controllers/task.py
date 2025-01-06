from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime
from models.task import Task
from utils.validators import TaskValidator
from controllers.habit import HabitController
from models.habit import Habit
from database.operations import DatabaseController # just pass through in update_task_status

class TaskController:
    """Task controller - coordinates model operations"""
    
    def __init__(self, db_controller: Optional[DatabaseController] = None):
        """Initialize controller"""
        self.validator = TaskValidator()
        self.habit_controller = HabitController()
        self.db_controller = db_controller  # Store db_controller
        self.status_map = {
            "Mark tasks as done": "done",
            "Mark tasks as ignored": "ignore",
            "Pause habit": "pause habit"
        }

    def get_related_pending_tasks(self, task_id: int, task_id_map: Dict[int, int]) -> List[int]:
        """Get a list of related pending task IDs for a given task.

        This method retrieves all pending tasks that are related to the same habit
        and due on the same date as the specified task, excluding the task itself.

        Args:
            task_id (int): ID of the task to find related tasks for
            task_id_map (Dict[int, int]): Mapping of external IDs to internal task IDs

        Returns:
            List[int]: List of external IDs for related pending tasks, or empty list if none found
                       or if an error occurs
        """

        try:
            task = Task.get_by_id(task_id)
            if task:
                related_tasks = Task.get_tasks_for_habit(task.habit_id, task.due_date)
                # Filter for pending AND different task ID
                pending_tasks = [t for t in related_tasks 
                               if t.status == 'pending' and t.id != task_id]
                if pending_tasks:
                    return [k for k,v in task_id_map.items() 
                           if v in [t.id for t in pending_tasks]]
            return []
        except Exception as e:
            print("Error getting related tasks: {}".format(e))
            return []

    def get_pending_tasks(self) -> List[Dict]:
        """Get formatted pending tasks"""
        try:
            tasks = Task.get_pending()
            formatted_tasks = []
            for idx, task in enumerate(tasks, 1):
                task_data = self._format_task_data(task)
                task_data['row'] = idx
                formatted_tasks.append(task_data)
            return formatted_tasks
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
        """
        Updates the status of a task and handles series progression if needed.
        Parameters:
            task_id (int): The ID of the task to update
            new_status (str): The new status to set for the task
        Returns:
            bool: True if the update was successful, False otherwise
        The method will also handle the creation of the next task in a series
        if the new status is either 'done' or 'ignore'.
        """
        
        try:
            task = Task.get_by_id(task_id, self.db_controller)
            if not task:
                print("No data found in task table")
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
        """
        Handles the next series of tasks for a given task's habit.
        This method processes the completion status of tasks in the current series and manages
        the habit's streak accordingly. If all tasks in the series are handled (either completed
        or ignored), it creates the next series of tasks.
        Args:
            task (Task): The task object containing the habit_id and due_date to process.
        Returns:
            bool: True if the next series was successfully handled or if no action was needed,
                  False if an error occurred during processing.
        """

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
            'row': 0,
            'id': task.id,
            'habit_name': task.habit_name,
            'task_number': task.task_number,
            'description': task.task_description[:30],
            'due_date': task.due_date,
            'status': task.status,
            'completion_rate': task.get_completion_rate,
            'streak': task.get_streak
        }