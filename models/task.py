from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime, timedelta
from database.operations import DatabaseController
from utils.date_utils import get_next_date

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

    # Properties and status

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
            if not total_tasks or len(total_tasks) <= 1:  # Check for single task
                return ""  # Empty string for single tasks
                
            completed = len([t for t in total_tasks if t[6] == 'done'])
            rate = (completed / len(total_tasks)) * 100
            return "{}%".format(int(rate))
        except Exception as e:
            print("Error calculating completion rate: {}".format(e))
            return "N/A"

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
        """Update task status"""
        try:
            return self.db_controller.update_data(
                'task',
                self.id,
                {'status': new_status}
            )
        except Exception as e:
            print("Error updating status: {}".format(e))
            return False
    
    @classmethod
    def get_by_id(cls, task_id: int, db_controller: Optional[DatabaseController] = None) -> Optional['Task']:
        """
        Retrieve a task by its ID from the database.

        Args:
            task_id (int): The ID of the task to retrieve.
            db_controller (Optional[DatabaseController]): Database controller instance. 
                If None, a new controller will be created.

        Returns:
            Optional[Task]: The task object if found, None otherwise.

        """

        db = db_controller or DatabaseController()
        try:
            task_data = db.read_data('task', {'id': task_id})
            if not task_data:
                return None
            return cls.from_db_tuple(task_data[0])
        except Exception as e:
            print("Error getting task: {}".format(e))
            return None
    
    @classmethod
    def from_db_tuple(cls, db_tuple: tuple) -> 'Task':
        """
        Creates a Task object from a database tuple.

        Args:
            cls: The class reference
            db_tuple (tuple): A tuple containing task data from database with the following structure:
                (task_id, habit_id, task_number, task_description, created, due_date, status)

        Returns:
            Task: A new Task instance populated with the database values

        """

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
    def get_pending(cls, db_controller: Optional[DatabaseController] = None) -> List['Task']:
        """
        Retrieves all pending tasks that are due today or earlier from the database.
        This method queries the database for tasks with 'pending' status and filters them based on
        their due date. It also fetches associated habit information for each task.
        Args:
            db_controller (DatabaseController, optional): Database controller instance.
                If not provided, a new instance will be created.
        Returns:
            List[Task]: A list of Task objects that are pending and due today or earlier.
                Returns an empty list if an error occurs during the database operation.
        Notes:
            - Tasks are considered pending only if their associated habit is not in 'Paused' state
            - Each returned Task object includes the associated habit name and current streak
            - Due date comparison is done using 'YYYY-MM-DD' format
        """

        db = db_controller or DatabaseController()
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            tasks = db.read_data('task', {'status': 'pending'})
            habits = db.read_data('habit')
            
            pending_tasks = []
            for task in tasks:
                task_obj = cls.from_db_tuple(task)
                # Add date check: due today or earlier
                if task_obj.due_date <= today:
                    habit = next((h for h in habits if h[0] == task[1]), None)
                    if habit and habit[7] != 'Paused':
                        task_obj.habit_name = habit[1]
                        task_obj.streak = habit[11]
                        pending_tasks.append(task_obj)
                        
            return pending_tasks
        except Exception as e:
            print("Error getting pending tasks: {}".format(e))
            return []

    # Business logic
 
    @classmethod
    def create_from_habit(cls, habit_id: int, task_number: int, habit_data: Dict[str, Any], db_controller: Optional[DatabaseController] = None) -> Optional['Task']:
        """
        Creates a new Task instance from a habit's data when creating a new one.

        Args:
            habit_id (int): The ID of the habit this task belongs to
            task_number (int): The sequence number of this task within the habit
            habit_data (Dict[str, Any]): Dictionary containing habit data with keys:
                - 'tasks_description': Description of the task
                - 'start': Due date for the task
            db_controller (Optional[DatabaseController]): Database controller instance for database operations. 
                                                        Defaults to None.

        Returns:
            Optional[Task]: New Task instance if creation successful, None if creation fails

        """

        try:
            task = cls(
                habit_id=habit_id,
                task_number=task_number,
                task_description=habit_data['tasks_description'],
                due_date=habit_data['start'],
                db_controller = db_controller # Passes through the parameter. Inserted for testing purposes
            )
            task_id = task.save()
            if task_id:
                task.id = task_id
                return task
            return None
        except Exception as e:
            print("Error creating task from habit: {}".format(e))
            return None

    @classmethod
    def create_next_series(cls, habit_id: int, due_date: str, tasks: List['Task']) -> bool:
        """
        Creates the next series of tasks for a given habit based on its periodicity.
        Args:
            habit_id (int): The ID of the habit to create next series for.
            due_date (str): The current due date in 'YYYY-MM-DD' format.
            tasks (List['Task']): List of existing tasks for the habit.
        Returns:
            bool: True if next series was created successfully, False otherwise.
        This method:
        - Retrieves habit data using the habit ID
        - Checks if next due date exceeds habit end date
        - Creates new task series if all checks pass
        """

        try:
            habit = cls._get_habit_data(habit_id)
            if not habit:
                return False
                
            next_due = get_next_date(due_date, habit[8])  # Returns str
            if not next_due:
                return False
                
            # Convert string to datetime for comparison
            next_due_dt = datetime.strptime(next_due, '%Y-%m-%d')
            
            if cls._is_past_end_date(next_due_dt, habit[6]):  # habit[6] is end date
                print("Habit {} completed - end date reached".format(habit_id))
                return False
                
            return cls._create_task_series(habit_id, next_due_dt, habit)
                
        except Exception as e:
            print("Error creating next task series: {}".format(e))
            return False

    @classmethod
    def _create_task_series(cls, habit_id: int, next_due: datetime, habit: tuple) -> bool:
        """
        Creates a series of tasks for a habit with specified parameters.

        This method generates multiple task instances based on the habit's task count,
        storing them in the database with sequential task numbers.

        Args:
            habit_id (int): The ID of the habit to create tasks for
            next_due (datetime): The due date for the tasks
            habit (tuple): A tuple containing habit information where:
                - habit[9]: Number of tasks to create (tasks_count)
                - habit[10]: Description for all tasks (tasks_description)

        Returns:
            bool: True if all tasks were created successfully, False otherwise

        """

        try:
            for task_num in range(1, habit[9] + 1):  # habit[9] is tasks_count
                task = cls(
                    habit_id=habit_id,
                    task_number=task_num,
                    task_description=habit[10],  # tasks_description
                    due_date=next_due.strftime('%Y-%m-%d')
                )
                if not task.save():
                    return False
            return True
        except Exception as e:
            print("Error creating tasks: {}".format(e))
            return False

    @staticmethod
    def get_tasks_for_habit(habit_id: int, due_date: str, db_controller: Optional[DatabaseController] = None) -> List['Task']:
        """
        Retrieves tasks associated with a specific habit and due date from the database.

        Args:
            habit_id (int): The ID of the habit to retrieve tasks for.
            due_date (str): The due date for the tasks in string format.
            db_controller (Optional[DatabaseController]): Database controller instance. 
                If not provided, a new instance will be created.

        Returns:
            List[Task]: A list of Task objects matching the habit_id and due_date.
                Returns an empty list if an error occurs during database operation.

        """

        try:
            db = db_controller or DatabaseController()
            tasks = db.read_data(
                'task',
                {
                    'habit_id': habit_id,
                    'due_date': due_date
                }
            )
            return [Task.from_db_tuple(task) for task in tasks]
        except Exception as e:
            print("Error getting tasks: {}".format(e))
            return []

    @classmethod
    def create_series(cls, habit_id: int, habit_data: Dict[str, Any]) -> List[int]:
        """
        Creates a series of tasks for a given habit.
        Args:
            habit_id (int): The ID of the habit to create tasks for.
            habit_data (Dict[str, Any]): Dictionary containing task creation data with keys:
                - 'tasks': Number of tasks to create
                - 'tasks_description': Description for each task
                - 'start': Start date for the tasks
        Returns:
            List[int]: List of created task IDs. Returns empty list if creation fails.

        """

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

    # Class methods for task creation

    @classmethod
    def delete_for_habit(cls, habit_id: int, db_controller: Optional[DatabaseController] = None) -> bool:
        """
        Deletes all tasks associated with a specific habit from the database.

        Args:
            habit_id (int): The ID of the habit whose tasks should be deleted.
            db_controller (Optional[DatabaseController]): Database controller instance. If None, a new one will be created.

        Returns:
            bool: True if deletion was successful, False otherwise.

        """

        db = db_controller or DatabaseController()
        try:
            return db.delete_data('task', {'habit_id': habit_id})
        except Exception as e:
            print(f"Error deleting tasks: {e}")
            return False

    @classmethod
    def check_completion_status(cls, tasks: List['Task']) -> tuple[bool, bool]:
        """Check if all tasks are completed/handled"""
        all_done = all(task.status == 'done' for task in tasks)
        all_handled = all(task.status in ['done', 'ignore'] for task in tasks)
        return all_done, all_handled

    # Helper methods
 
    @classmethod
    def _get_habit_data(cls, habit_id: int, db_controller: Optional[DatabaseController] = None) -> Optional[tuple]:
        """Get habit data from database"""
        db = db_controller or DatabaseController()
        habits = db.read_data('habit', {'id': habit_id})
        return habits[0] if habits else None
        
    @classmethod
    def _is_past_end_date(cls, next_due: datetime, end: str) -> bool:
        """Check if next due date is past habit end date
        
        Args:
            next_due (datetime): Next due date to check
            end (str): End date string in YYYY-MM-DD format
            
        Returns:
            bool: True if next_due is past end date, False otherwise
        """
        try:
            if not end:
                return False
                
            end_date = datetime.strptime(end, '%Y-%m-%d').date()
            return next_due.date() > end_date
        except ValueError as e:
            print("Error checking end date: {}".format(e))
            return False

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
    
    # String representations
    def __str__(self) -> str:
        """String representation"""
        return "Task {} (Due: {}) - {}".format(
            self.task_number, self.due_date, self.status)

    def __repr__(self) -> str:
        """Detailed representation"""
        return "Task(habit_id={}, number={}, due={}, status={})".format(
            self.habit_id, self.task_number, self.due_date, self.status)