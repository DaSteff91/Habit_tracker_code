from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from database.operations import DatabaseController

class Habit:
    """Habit data model with database operations and business logic"""
    def __init__(self, 
                 name: str,
                 category: str,
                 description: str,
                 start: str,
                 end: str,
                 importance: str,
                 repeat: str,
                 tasks: int,
                 tasks_description: str,
                 habit_id: int = None,
                 db_controller: Optional[DatabaseController] = None):
        # Core properties
        self.id = habit_id
        self.name = name
        self.category = category
        self.description = description
        self.start = start
        self.end = end
        self.importance = importance
        self.repeat = repeat
        self.tasks = tasks
        self.tasks_description = tasks_description
        self.streak = 0
        self.reset_count = 0
        self.created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.db_controller = db_controller or DatabaseController()

    # Class methods for creation/retrieval

    @staticmethod
    def _prepare_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare habit data for database"""
        prepared = data.copy()
        prepared.update({
            'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'streak': 0,
            'streak_reset_count': 0
        })
        return prepared

    @classmethod
    def create(cls, data: Dict[str, Any], db_controller: Optional[DatabaseController] = None) -> Optional['Habit']:
        """Create new habit"""
        try:
            # Store original data for object creation
            init_data = data.copy()
            
            # Prepare data for database
            db_data = cls._prepare_data(data)
            db = db_controller or DatabaseController()
            
            # Create in database
            habit_id = db.create_data('habit', db_data)
            if habit_id == -1:
                return None
                
            # Create object with original data
            return cls.get_by_id(habit_id, db_controller=db, **init_data)
        except Exception as e:
            print("Error creating habit: {}".format(e))
            return None

    @classmethod
    def get_by_id(cls, habit_id: int, db_controller: Optional[DatabaseController] = None, **kwargs) -> Optional['Habit']:
        """Get habit by ID"""
        db = db_controller or DatabaseController()
        try:
            if kwargs:
                return cls(
                    habit_id=habit_id,
                    db_controller=db,
                    **kwargs
                )
            
            # Normal DB lookup
            habits = db.read_data('habit', {'id': habit_id})
            return cls.from_db_tuple(habits[0]) if habits else None
        except Exception as e:
            print("Error getting habit: {}".format(e))
            return None

    @classmethod
    def get_all(cls, db_controller: Optional[DatabaseController] = None) -> List['Habit']:
        """Get all habits"""
        db = db_controller or DatabaseController()
        try:
            habits = db.read_data('habit')
            return [cls.from_db_tuple(habit) for habit in habits]
        except Exception as e:
            print("Error getting habits: {}".format(e))
            return []

    @classmethod
    def from_db_tuple(cls, db_tuple: tuple) -> 'Habit':
        """Create habit from database tuple"""
        habit = cls(
            habit_id=db_tuple[0],
            name=db_tuple[1],
            category=db_tuple[2],
            description=db_tuple[3],
            start=db_tuple[5],
            end=db_tuple[6],
            importance=db_tuple[7],
            repeat=db_tuple[8],
            tasks=db_tuple[9],
            tasks_description=db_tuple[10]
        )
        # Set additional properties
        habit.streak = db_tuple[11]
        habit.reset_count = db_tuple[12]
        habit.created = db_tuple[4]
        return habit

    # Properties and status
    @property
    def status(self) -> str:
        """Get current status"""
        if self.importance == 'Paused':
            return 'Paused'
        today = datetime.now().date()
        end = datetime.strptime(self.end, '%Y-%m-%d').date()
        if end < today:
            return 'Completed'
        return 'Active'

    def is_active(self) -> bool:
        """Check if currently active"""
        return self.status == 'Active'

    # Database operations
    def save(self) -> bool:
        """Save to database"""
        try:
            data = self.to_dict()
            if not hasattr(self, 'id'):
                self.id = self.db_controller.create_data('habit', data)
                return self.id != -1
            return self.db_controller.update_data('habit', self.id, data)
        except Exception as e:
            print(f"Error saving habit: {e}")
            return False

    def update(self, data: Dict[str, Any]) -> bool:
        """Update specific fields"""
        try:
            if not hasattr(self, 'id'):
                return False
            if self.db_controller.update_data('habit', self.id, data):
                for key, value in data.items():
                    setattr(self, key, value)
                return True
            return False
        except Exception as e:
            print(f"Error updating habit: {e}")
            return False

    def delete(self) -> bool:
        """Delete from database"""
        try:
            if not hasattr(self, 'id'):
                return False
            return self.db_controller.delete_data('habit', self.id)
        except Exception as e:
            print(f"Error deleting habit: {e}")
            return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to database format"""
        return {
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'start': self.start,
            'end': self.end,
            'importance': self.importance,
            'repeat': self.repeat,
            'tasks': self.tasks,
            'tasks_description': self.tasks_description,
            'streak': self.streak,
            'streak_reset_count': self.reset_count,
            'created': self.created
        }

    # Business logic
    def increment_streak(self) -> bool:
        """Increment streak"""
        try:
            self.streak += 1
            success = self.update({'streak': self.streak})
            if success:
                return self.update_longest_streak()
            return False
        except Exception as e:
            print("Error updating streak: {}".format(e))
            return False

    def update_longest_streak(self) -> bool:
        """Update longest streak if current is higher"""
        try:
            if not hasattr(self, 'longest_streak'):
                self.longest_streak = 0
            if self.streak > self.longest_streak:
                self.longest_streak = self.streak
                return self.update({'longest_streak': self.longest_streak})
            return True
        except Exception as e:
            print("Error updating longest streak: {}".format(e))
            return False
        
    def reset_streak(self) -> bool:
        """Reset habit streak and increment reset counter"""
        try:
            if self.update({'streak': 0}):
                return self.increment_reset_counter()
            return False
        except Exception as e:
            print("Error resetting streak: {}".format(e))
            return False

    def increment_reset_counter(self) -> bool:
        """Increment reset counter"""
        try:
            self.reset_count += 1
            return self.update({'streak_reset_count': self.reset_count})
        except Exception as e:
            print(f"Error incrementing reset: {e}")
            return False

    def get_days_passed(self) -> int:
        """Calculate days since start"""
        start = datetime.strptime(self.start, '%Y-%m-%d').date()
        today = datetime.now().date()
        return (today - start).days

    def get_success_rate(self) -> float:
        """Calculate success rate"""
        if self.streak == 0:
            return 0.0
        total_attempts = self.streak + self.reset_count
        return (self.streak / total_attempts) * 100 if total_attempts > 0 else 0.0

    # String representations
    def __str__(self) -> str:
        """String representation"""
        return f"{self.name} ({self.category}) - {self.status}"

    def __repr__(self) -> str:
        """Detailed representation"""
        return f"Habit(name='{self.name}', category='{self.category}', status='{self.status}')"