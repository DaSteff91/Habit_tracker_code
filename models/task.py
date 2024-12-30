from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime, timedelta
from database.operations import DatabaseController

class Task:
    """Task data model with business logic"""
    def __init__(self, 
                 habit_id: int,
                 task_number: int,
                 task_description: str,
                 due_date: str,
                 task_id: int = None,
                 status: str = 'pending',
                 created: str = None,
                 db_controller: Optional[DatabaseController] = None):
        # Core properties
        self.id = task_id
        self.habit_id = habit_id
        self.task_number = task_number
        self.task_description = task_description
        self.due_date = due_date
        self.status = status
        self.created = created or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Additional properties
        self.habit_name = None
        self.streak = 0
        self.completion_rate = 0.0
        
        # Database access
        self.db_controller = db_controller or DatabaseController()

    # Database operations
    def save(self) -> Optional[int]:
        """Save task to database"""
        try:
            task_id = self.db_controller.create_data('task', self.to_dict())
            return task_id if task_id != -1 else None
        except Exception as e:
            print("Error saving task: {}".format(e))
            return None

    def update_status(self, new_status: str) -> bool:
        """Update task status with validation"""
        if not self._is_valid_status(new_status):
            return False
        return self.db_controller.update_data('task', self.id, {'status': new_status})
    
    @property
    def get_streak(self) -> int:
        """Get current streak from associated habit"""
        try:
            habit = self.db_controller.read_data(
                'habit', 
                {'id': self.habit_id}
            )[0]
            return habit[11]  # streak field
        except Exception as e:
            print("Error getting streak: {}".format(e))
            return 0

    @property
    def get_completion_rate(self) -> str:
        """Calculate completion rate for task's habit"""
        try:
            total_tasks = self.db_controller.read_data(
                'task',
                {'habit_id': self.habit_id, 'due_date': self.due_date}
            )
            if not total_tasks:
                return "0%"
                
            completed = len([t for t in total_tasks if t[6] == 'done'])
            rate = (completed / len(total_tasks)) * 100
            return "{}%".format(int(rate))
        except Exception as e:
            print("Error calculating completion rate: {}".format(e))
            return "N/A"

    # Business logic
    @staticmethod
    def _calculate_completion_rate(habit_id: int) -> float:
        """Calculate completion rate for a habit's tasks"""
        db = DatabaseController()
        try:
            all_tasks = db.read_data('task', {'habit_id': habit_id})
            if not all_tasks:
                return 0.0
            completed = len([t for t in all_tasks if t[6] == 'done'])
            return round((completed / len(all_tasks) * 100), 1)
        except Exception:
            return 0.0
        
    @staticmethod
    def _calculate_next_due_date(self, repeat: str) -> str:
        """Calculate next due date based on repeat interval"""
        current = datetime.strptime(self.due_date, '%Y-%m-%d')
        if repeat == 'Daily':
            next_date = current + timedelta(days=1)
        elif repeat == 'Weekly':
            next_date = current + timedelta(weeks=1)
        else:
            next_date = current
        return next_date.strftime('%Y-%m-%d')

    # Class methods for task creation
    @classmethod
    def get_tasks_for_habit(cls, habit_id: int) -> List['Task']:
        """Get all tasks for a habit"""
        db = DatabaseController()
        try:
            tasks = db.read_data('task', {'habit_id': habit_id})
            return [cls.from_db_tuple(task) for task in tasks]
        except Exception as e:
            print(f"Error getting tasks: {e}")
            return []

    @classmethod
    def delete_for_habit(cls, habit_id: int) -> bool:
        """Delete all tasks for a habit"""
        db = DatabaseController()
        try:
            return db.delete_data('task', {'habit_id': habit_id})
        except Exception as e:
            print(f"Error deleting tasks: {e}")
            return False

    @classmethod
    def create_next_series(cls, habit_id: int, due_date: str, tasks: List[Dict[str, Any]]) -> bool:
        """Create next series of tasks based on completed ones"""
        db = DatabaseController()
        try:
            # Get habit data for repeat interval
            habit = db.read_data('habit', {'id': habit_id})[0]
            repeat = habit[8]  # repeat interval
            stop_date = datetime.strptime(habit[6], '%Y-%m-%d')  # end date

            # Calculate next due date
            current = datetime.strptime(due_date, '%Y-%m-%d')
            next_due = cls._calculate_next_due_date(current, repeat)

            # Check if we've reached the end date
            if next_due.date() > stop_date.date():
                print("Habit completed - end date reached")
                return False

            # Create new tasks
            for task_num in range(1, len(tasks) + 1):
                task = cls(
                    habit_id=habit_id,
                    task_number=task_num,
                    task_description=habit[10],  # tasks_description
                    due_date=next_due.strftime('%Y-%m-%d')
                )
                task.save()

            return True
        except Exception as e:
            print("Error creating next task series: {}".format(e))
            return False
 
    @classmethod
    def get_by_id(cls, task_id: int) -> Optional['Task']:
        """Get task by ID"""
        db_controller = DatabaseController()
        try:
            task_data = db_controller.read_data('task', {'id': task_id})
            if not task_data:
                return None
            return cls.from_db_tuple(task_data[0])
        except Exception as e:
            print("Error getting task: {}".format(e))
            return None
 
    @classmethod
    def create_from_habit(cls, habit_id: int, task_number: int, 
                         habit_data: Dict[str, Any],
                         db_controller: Optional[DatabaseController] = None) -> 'Task':
        """Create task from habit data"""
        return cls(
            habit_id=habit_id,
            task_number=task_number,
            task_description=habit_data['tasks_description'],
            due_date=habit_data['start'],
            db_controller=db_controller
        )

    @classmethod
    def create_pending_tasks(cls, tasks_data: List[tuple], 
                           habits_data: List[tuple],
                           db_controller: DatabaseController) -> List['Task']:
        """Create task instances from raw data"""
        pending_tasks = []
        for task in tasks_data:
            task_obj = cls.from_db_tuple(task, db_controller)
            habit = next((h for h in habits_data if h[0] == task[1]), None)
            if habit and habit[7] != 'Paused':
                task_obj.set_habit_data(habit[1], habit[11])
                task_obj.completion_rate = task_obj.calculate_completion_rate()
                pending_tasks.append(task_obj)
        return pending_tasks
    
    @classmethod
    def get_pending(cls) -> List['Task']:
        """Get all pending tasks"""
        db = DatabaseController()
        try:
            tasks = db.read_data('task', {'status': 'pending'})
            habits = db.read_data('habit')
            
            pending_tasks = []
            for task in tasks:
                task_obj = cls.from_db_tuple(task)
                habit = next((h for h in habits if h[0] == task[1]), None)
                if habit and habit[7] != 'Paused':
                    task_obj.habit_name = habit[1]  # Set habit name
                    task_obj.streak = habit[11]     # Set streak
                    pending_tasks.append(task_obj)
                    
            return pending_tasks
        except Exception as e:
            print("Error getting pending tasks: {}".format(e))
            return []

    @classmethod
    def from_db_tuple(cls, db_tuple: tuple) -> 'Task':
        """Create task from database tuple"""
        return cls(
            task_id=db_tuple[0],
            habit_id=db_tuple[1],
            task_number=db_tuple[2],
            task_description=db_tuple[3],
            created=db_tuple[4],
            due_date=db_tuple[5],
            status=db_tuple[6]
        )
    
    @classmethod
    def create_series(cls, habit_id: int, habit_data: Dict[str, Any]) -> List[int]:
        """Create a series of tasks for a habit"""
        db = DatabaseController()
        task_ids = []
        
        try:
            for task_num in range(1, habit_data['tasks'] + 1):
                task = cls(
                    habit_id=habit_id,
                    task_number=task_num,
                    task_description=habit_data['tasks_description'],
                    due_date=habit_data['start']
                )
                task_id = task.save()
                if task_id:
                    task_ids.append(task_id)
            return task_ids
        except Exception as e:
            print("Error creating task series: {}".format(e))
            return []
    
    @classmethod
    def check_completion_status(cls, tasks: List['Task']) -> tuple[bool, bool]:
        """Check if all tasks are completed/handled"""
        all_done = all(task.status == 'done' for task in tasks)
        all_handled = all(task.status in ['done', 'ignore'] for task in tasks)
        return all_done, all_handled

    # Helper methods
    def set_habit_data(self, habit_name: str, streak: int) -> None:
        """Set habit-related data"""
        self.habit_name = habit_name
        self.streak = streak

    def to_dict(self) -> Dict[str, Any]:
        """Convert to database format"""
        return {
            'habit_id': self.habit_id,
            'task_number': self.task_number,
            'task_description': self.task_description,
            'created': self.created,
            'due_date': self.due_date,
            'status': self.status
        }

    # Validation methods
    def is_pending(self) -> bool:
        """Check current state"""
        return self.status == 'pending'

    def is_completed(self) -> bool:
        """Check current state"""
        return self.status == 'done'
    
    # String representations
    def __str__(self) -> str:
        """String representation"""
        return "Task {} (Due: {}) - {}".format(
            self.task_number, self.due_date, self.status)

    def __repr__(self) -> str:
        """Detailed representation"""
        return "Task(habit_id={}, number={}, due={}, status={})".format(
            self.habit_id, self.task_number, self.due_date, self.status)