from datetime import datetime
from typing import Dict, Any, Optional

class Task:
    """Task data model"""
    def __init__(self,
                 habit_id: int,
                 task_number: int,
                 task_description: str,
                 due_date: str,
                 status: str = 'pending'):
        """Initialize Task instance"""
        self.habit_id = habit_id
        self.task_number = task_number
        self.task_description = task_description
        self.due_date = due_date
        self.status = status
        self.created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for database operations"""
        return {
            'habit_id': self.habit_id,
            'task_number': self.task_number,
            'task_description': self.task_description,
            'due_date': self.due_date,
            'status': self.status,
            'created': self.created
        }

    @classmethod
    def from_db_tuple(cls, db_tuple: tuple) -> 'Task':
        """Create Task instance from database tuple"""
        task = cls(
            habit_id=db_tuple[1],
            task_number=db_tuple[2],
            task_description=db_tuple[3],
            due_date=db_tuple[5],
            status=db_tuple[6]
        )
        task.created = db_tuple[4]
        return task

    def is_pending(self) -> bool:
        """Check if task is pending"""
        return self.status == 'pending'

    def is_completed(self) -> bool:
        """Check if task is completed"""
        return self.status == 'done'

    def is_valid_date(self) -> bool:
        """Validate due date format"""
        try:
            datetime.strptime(self.due_date, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def __str__(self) -> str:
        """String representation of task"""
        return f"Task {self.task_number} (Due: {self.due_date}) - {self.status}"

    def __repr__(self) -> str:
        """Detailed string representation"""
        return (f"Task(habit_id={self.habit_id}, "
                f"number={self.task_number}, "
                f"due={self.due_date}, "
                f"status={self.status})")