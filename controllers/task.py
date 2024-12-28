from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional
from database.operations import DatabaseController

class TaskController:
    """Task business logic"""
    
    def __init__(self, db_controller=None):
        """Initialize TaskController"""
        self.db_controller = db_controller or DatabaseController()

    def create_tasks_from_habit(self, habit_id: int, habit_data: Dict[str, Any]) -> List[int]:
        """Coordinate task creation from habit data"""
        try:
            task_template = self._prepare_base_task_data(habit_id, habit_data)
            return self._create_task_series(task_template, habit_data['tasks'])
        except Exception as e:
            print(f"Error creating tasks: {e}")
            return []

    def _prepare_base_task_data(self, habit_id: int, habit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare base task data template"""
        return {
            'habit_id': habit_id,
            'task_number': 0,  # Will be updated for each task
            'task_description': habit_data['tasks_description'],
            'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'due_date': habit_data['start'],
            'status': 'pending'
        }

    def _create_task_series(self, task_template: Dict[str, Any], num_tasks: int) -> List[int]:
        """Create series of tasks from template"""
        task_ids = []
        for task_num in range(1, num_tasks + 1):
            task_data = task_template.copy()
            task_data['task_number'] = task_num
            
            task_id = self.db_controller.create_data('task', task_data)
            if task_id != -1:
                task_ids.append(task_id)
                print(f"Created task #{task_num} for habit {task_data['habit_id']}")
            else:
                print(f"Failed to create task #{task_num} for habit {task_data['habit_id']}")
                
        return task_ids

    def update_task_status(self, task_id: int, new_status: str) -> bool:
        """Coordinate task status update"""
        if not self._validate_status(new_status):
            return False
            
        task_data = self._get_task_data(task_id)
        if not task_data:
            return False
            
        return self._update_status(task_id, new_status)

    def _validate_status(self, status: str) -> bool:
        """Validate task status value"""
        valid_status = ['done', 'ignore', 'pause habit']
        if status not in valid_status:
            print(f"Invalid status. Use: {'/'.join(valid_status)}")
            return False
        return True

    def _get_task_data(self, task_id: int) -> Optional[Dict]:
        """Retrieve task data"""
        task_data = self.db_controller.read_data('task', {'id': task_id})
        if not task_data:
            print(f"Task {task_id} not found")
            return None
        return task_data[0]

    def _update_status(self, task_id: int, new_status: str) -> bool:
        """Update task status in database"""
        try:
            task_update = {'status': new_status}
            if self.db_controller.update_data('task', task_id, task_update):
                print(f"Task {task_id} status updated to: {new_status}")
                return True
            print("Failed to update task status")
            return False
        except Exception as e:
            print(f"Error updating task status: {e}")
            return False
        
    def get_tasks_for_habit(self, habit_id: int, due_date: str) -> List[Dict[str, Any]]:
        """Get tasks for a specific habit and due date"""
        return self.db_controller.read_data('task', {
            'habit_id': habit_id,
            'due_date': due_date
        })

    def check_task_completion_status(self, tasks: List[Dict[str, Any]]) -> Tuple[bool, bool]:
        """Check if all tasks are completed or ignored"""
        all_tasks_updated = all(task[6] == 'done' for task in tasks)
        all_tasks_completed = all(task[6] in ['done', 'ignore'] for task in tasks)
        return all_tasks_updated, all_tasks_completed

    def create_next_tasks(self, habit_id: int, due_date: str, tasks: List[Dict[str, Any]]) -> bool:
        """Coordinate creation of next task set"""
        try:
            habit_data = self._get_habit_data(habit_id)
            if not habit_data:
                return False

            next_due = self._calculate_next_due_date(
                habit_data['repeat'],
                due_date,
                habit_data['stop_date']
            )
            if not next_due:
                print(f"Habit {habit_id} completed - end date reached")
                return False

            task_data = self._prepare_task_data(habit_id, habit_data['description'], next_due)
            return self._create_task_set(task_data, len(tasks))

        except Exception as e:
            print(f"Error creating next tasks: {e}")
            return False

    def _get_habit_data(self, habit_id: int) -> Optional[Dict[str, Any]]:
        """Get required habit data"""
        habit = self.db_controller.read_data('habit', {'id': habit_id})[0]
        if not habit:
            return None
        return {
            'repeat': habit[8],
            'stop_date': habit[6],
            'description': habit[10]
        }

    def _calculate_next_due_date(self, repeat: str, current_due: str, stop_date: str) -> Optional[str]:
        """Calculate next due date if within stop date"""
        current = datetime.strptime(current_due, '%Y-%m-%d')
        stop = datetime.strptime(stop_date, '%Y-%m-%d')
        
        next_due = self.calculate_next_due_date(repeat, current)
        if next_due.date() > stop.date():
            return None
        return next_due.strftime('%Y-%m-%d')

    def _prepare_task_data(self, habit_id: int, description: str, due_date: str) -> Dict[str, Any]:
        """Prepare base task data"""
        return {
            'habit_id': habit_id,
            'task_description': description,
            'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'due_date': due_date,
            'status': 'pending'
        }

    def _create_task_set(self, task_data: Dict[str, Any], num_tasks: int) -> bool:
        """Create set of tasks with task numbers"""
        success = True
        for task_num in range(1, num_tasks + 1):
            task_data['task_number'] = task_num
            if self.db_controller.create_data('task', task_data) == -1:
                success = False
        
        if success:
            print(f"Created new tasks for habit {task_data['habit_id']} due {task_data['due_date']}")
        return success

    def calculate_next_due_date(self, repeat: str, current_due: datetime) -> datetime:
        """Calculate the next due date based on repeat interval"""
        if repeat == 'Daily':
            return current_due + timedelta(days=1)
        elif repeat == 'Weekly':
            return current_due + timedelta(weeks=1)
        return current_due
        