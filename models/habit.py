from typing import Dict, Any
from datetime import datetime

class Habit:
    """Habit data model"""
    def __init__(self, 
                 name: str,
                 category: str,
                 description: str,
                 start_date: str,
                 end_date: str,
                 importance: str,
                 repeat: str,
                 tasks: int,
                 tasks_description: str):
        self.name = name
        self.category = category
        self.description = description
        self.start_date = start_date
        self.end_date = end_date
        self.importance = importance
        self.repeat = repeat
        self.tasks = tasks
        self.tasks_description = tasks_description
        self.streak = 0
        self.reset_count = 0
        self.created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    @property
    def status(self) -> str:
        """Get current habit status"""
        if self.importance == 'Paused':
            return 'Paused'
        today = datetime.now().date()
        end = datetime.strptime(self.end_date, '%Y-%m-%d').date()
        if end < today:
            return 'Completed'
        return 'Active'

    def is_active(self) -> bool:
        """Check if habit is currently active"""
        return self.status == 'Active'

    def is_valid_date_format(self, date_str: str) -> bool:
        """Validate date string format"""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def __str__(self) -> str:
        """String representation of habit"""
        return f"{self.name} ({self.category}) - {self.status}"

    def __repr__(self) -> str:
        """Detailed string representation"""
        return f"Habit(name='{self.name}', category='{self.category}', status='{self.status}')"

    def to_dict(self) -> Dict[str, Any]:
        """Convert habit to dictionary for database operations"""
        return {
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'start': self.start_date,
            'stop': self.end_date,
            'importance': self.importance,
            'repeat': self.repeat,
            'tasks': self.tasks,
            'tasks_description': self.tasks_description,
            'streak': self.streak,
            'streak_reset_count': self.reset_count,
            'created': self.created
        }

    @classmethod
    def from_db_tuple(cls, db_tuple: tuple) -> 'Habit':
        """Create Habit instance from database tuple"""
        habit = cls(
            name=db_tuple[1],
            category=db_tuple[2],
            description=db_tuple[3],
            start_date=db_tuple[5],
            end_date=db_tuple[6],
            importance=db_tuple[7],
            repeat=db_tuple[8],
            tasks=db_tuple[9],
            tasks_description=db_tuple[10]
        )
        habit.streak = db_tuple[11]
        habit.reset_count = db_tuple[12]
        habit.created = db_tuple[4]
        return habit