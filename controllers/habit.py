from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime
from models.habit import Habit
from database.operations import DatabaseController
from utils.validators import HabitValidator

class HabitController:
    """Controls habit-related business logic"""  

    def __init__(self, db_controller=None):
        """Initialize controller with optional database controller"""
        self.db_controller = db_controller or DatabaseController()
        self.validator = HabitValidator()

    def create_habit(self, habit_data: Dict[str, Any]) -> Optional[int]:
        """Create new habit with validation"""
        try:
            # 1. Add metadata
            habit_data = self._prepare_habit_data(habit_data)
            
            # 2. Validate data
            if not self._validate_habit_data(habit_data):
                return None
                
            # 3. Create habit
            habit_id = self._create_habit_record(habit_data)
            if not habit_id:
                return None
                
            # 4. Create associated tasks
            if not self._create_habit_tasks(habit_id, habit_data):
                self.db_controller.delete_data('habit', habit_id)
                return None
                
            print(f"Successfully created habit {habit_id}")
            return habit_id
                
        except Exception as e:
            print(f"Error creating habit: {e}")
            return None

    def _prepare_habit_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare habit data with metadata"""
        data['created'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data['streak'] = 0
        return data

    def _validate_habit_data(self, data: Dict[str, Any]) -> bool:
        """Validate habit data"""
        is_valid, message = self.validator.validate_habit_data(data)
        if not is_valid:
            print(f"Invalid habit data: {message}")
        return is_valid

    def _create_habit_record(self, data: Dict[str, Any]) -> Optional[int]:
        """Create habit record in database"""
        habit_id = self.db_controller.create_data('habit', data)
        if habit_id == -1:
            print("Failed to create habit")
            return None
        return habit_id

    def _create_habit_tasks(self, habit_id: int, habit_data: Dict[str, Any]) -> bool:
        """Create associated tasks for habit"""
        task_ids = []
        for task_num in range(1, habit_data['tasks'] + 1):
            task_data = {
                'habit_id': habit_id,
                'task_number': task_num,
                'task_description': habit_data['tasks_description'],
                'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'due_date': habit_data['start'],
                'status': 'pending'
            }
            task_id = self.db_controller.create_data('task', task_data)
            if task_id != -1:
                task_ids.append(task_id)
                print(f"Created task #{task_num} for habit {habit_id}")
            
        if not task_ids:
            print("Failed to create tasks")
            return False
        return True

    def process_habit_update(self, habit_id: int, field: str, value: str) -> bool:
        """Coordinate habit update process"""
        try:
            habit = self._get_habit_data(habit_id)
            if not habit:
                return False
                
            update_data = self._prepare_update_data(habit, field, value)
            if not self._validate_update(update_data, field):
                return False
                
            return self._process_update(habit_id, field, value)
            
        except Exception as e:
            print(f"Error processing update: {e}")
            return False

    def _get_habit_data(self, habit_id: int) -> Optional[tuple]:
        """Retrieve habit data from database"""
        habit = self.db_controller.read_data('habit', {'id': habit_id})[0]
        if not habit:
            print("Habit not found")
            return None
        return habit

    def _prepare_update_data(self, habit: tuple, field: str, value: str) -> Dict[str, Any]:
        """Prepare complete habit data with update"""
        update_data = {
            'name': habit[1],
            'category': habit[2],
            'description': habit[3],
            'start': habit[5],
            'stop': habit[6],
            'importance': habit[7],
            'repeat': habit[8],
            'tasks': habit[9],
            'tasks_description': habit[10]
        }
        update_data[field] = value
        return update_data

    def _validate_update(self, update_data: Dict[str, Any], field: str) -> bool:
        """Validate update data"""
        is_valid, message = self.validator.validate_habit_data(update_data, field)
        if not is_valid:
            print(f"Invalid input: {message}")
        return is_valid

    def _process_update(self, habit_id: int, field: str, value: str) -> bool:
        """Process the actual update"""
        if field == 'importance' and value == 'Paused':
            return self.pause_habit(habit_id)
        return self.update_habit(habit_id, {field: value})

    def create_tasks_from_habit(self, habit_id: int, habit_data: Dict[str, Any]) -> List[int]:
        """Create tasks for a habit"""
        task_ids = []
        try:
            for task_num in range(1, habit_data['tasks'] + 1):
                task_data = {
                    'habit_id': habit_id,
                    'task_number': task_num,
                    'task_description': habit_data['tasks_description'],
                    'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'due_date': habit_data['start'],
                    'status': 'pending'
                }
                task_id = self.db_controller.create_data('task', task_data)
                if task_id != -1:
                    task_ids.append(task_id)
                    print(f"Created task #{task_num} for habit {habit_id}")
            return task_ids
        except Exception as e:
            print(f"Error creating tasks: {e}")
            return []

    def process_habit_update(self, habit_id: int, field: str, value: str) -> bool:
        """Process habit update with validation"""
        try:
            # Get current habit data for validation
            habit = self.db_controller.read_data('habit', {'id': habit_id})[0]
            
            # Prepare full habit data
            update_data = {
                'name': habit[1],
                'category': habit[2],
                'description': habit[3],
                'start': habit[5],
                'stop': habit[6],
                'importance': habit[7],
                'repeat': habit[8],
                'tasks': habit[9],
                'tasks_description': habit[10]
            }
            update_data[field] = value
            
            # Validate update
            is_valid, message = HabitValidator.validate_habit_data(update_data, field)
            if not is_valid:
                print("Invalid input: {}".format(message))
                return False
                
            # Special case for pausing habit
            if field == 'importance' and value == 'Paused':
                return self.pause_habit(habit_id)
                
            # Regular update
            return self.update_habit(habit_id, {field: value})
            
        except Exception as e:
            print("Error processing update: {}".format(e))
            return False


    def increment_streak(self, habit_id: int) -> bool:
        """Increment habit streak"""
        try:
            habit = self.db_controller.read_data('habit', {'id': habit_id})
            if not habit:
                return False
            current_streak = habit[0][11]
            update_data = {'streak': current_streak + 1}
            return self.db_controller.update_data('habit', habit_id, update_data)
        except Exception as e:
            print(f"Error incrementing streak: {e}")
            return False
    
    def increment_reset_counter(self, habit_id: int) -> bool:
        """Increment streak reset counter"""
        try:
            habit = self.db_controller.read_data('habit', {'id': habit_id})
            if not habit:
                return False
            current_reset = habit[0][12]
            update_data = {'streak_reset_count': current_reset + 1}
            return self.db_controller.update_data('habit', habit_id, update_data)
        except Exception as e:
            print(f"Error incrementing reset counter: {e}")
            return False






    def update_habit(self, habit_id: int, update_data: Dict[str, Any]) -> bool:
        """Update habit with validation"""
        try:
            habit = self.db_controller.read_data('habit', {'id': habit_id})
            if not habit:
                print(f"Habit {habit_id} not found")
                return False
            
            current_data = self._prepare_current_data(habit[0])
            field_to_update = list(update_data.keys())[0]
            current_data.update(update_data)
            
            is_valid, message = self.validator.validate_habit_data(current_data, field_to_update)
            if not is_valid:
                print(f"Invalid update data: {message}")
                return False
            
            if update_data.get('importance') == 'Paused':
                return self.pause_habit(habit_id)
            
            result = self.db_controller.update_data('habit', habit_id, update_data)
            if result:
                print(f"Habit {habit_id} updated successfully")
            return result
            
        except Exception as e:
            print(f"Error updating habit: {e}")
            return False

    def _prepare_current_data(self, habit: tuple) -> Dict[str, Any]:
        """Prepare current habit data for validation"""
        return {
            'name': habit[1],
            'category': habit[2],
            'description': habit[3],
            'start': habit[5],
            'stop': habit[6],
            'importance': habit[7],
            'repeat': habit[8],
            'tasks': habit[9],
            'tasks_description': habit[10]
        }

    def delete_habit(self, habit_id: int) -> bool:
        """Delete habit and associated tasks"""
        try:
            habit = self.db_controller.read_data('habit', {'id': habit_id})
            if not habit:
                print(f"Habit {habit_id} not found")
                return False
            result = self.db_controller.delete_data('habit', habit_id)
            if result:
                print(f"Successfully deleted habit {habit_id}")
            return result
        except Exception as e:
            print(f"Error deleting habit: {e}")
            return False

    def get_habits(self) -> List[tuple]:
        """Get all habits from database"""
        return self.ui_handler.db_controller.read_data('habit')

    def get_habit(self, habit_id: int) -> Optional[tuple]:
        """Get specific habit by ID"""
        habits = self.ui_handler.db_controller.read_data('habit', {'id': habit_id})
        return habits[0] if habits else None

    def validate_habit_data(self, data: Dict, updating_field: Optional[str] = None) -> Tuple[bool, str]:
        """Validate habit data"""
        return self.validator.validate_habit_data(data, updating_field)

    def pause_habit(self, habit_id: int) -> bool:
        """Pause habit and reset streak"""
        try:
            update_data = {
                'streak': 0,
                'importance': 'Paused'
            }
            result = self.db_controller.update_data('habit', habit_id, update_data)
            if result:
                self.increment_reset_counter(habit_id)
                print(f"Habit {habit_id} paused and streak reset")
            return result
        except Exception as e:
            print(f"Error pausing habit: {e}")
            return False

    def reset_streak(self, habit_id: int) -> bool:
        """Reset habit streak"""
        try:
            update_data = {'streak': 0}
            result = self.db_controller.update_data('habit', habit_id, update_data)
            if result:
                self.increment_reset_counter(habit_id)
                print("Streak reset for habit {}".format(habit_id))
            return result
        except Exception as e:
            print("Error resetting streak: {}".format(e))
            return False

    def get_valid_fields(self) -> set:
        """Get valid fields for habit updates"""
        return {
            'category',
            'description',
            'start',
            'stop',
            'importance',
            'repeat'
        }

    def is_active(self, habit_id: int) -> bool:
        """Check if habit is active"""
        habit = self.get_habit(habit_id)
        if not habit:
            return False
        return habit[7] != 'Paused'  # index 7 is importance