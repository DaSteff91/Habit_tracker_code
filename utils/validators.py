from datetime import datetime
from typing import Dict, Any, Tuple, Optional
from models.habit import Habit
from database.operations import DatabaseController # just pass through in update_task_status

class HabitValidator:
    """Validates habit-related data"""

    @staticmethod
    def validate_update(field: str, value: str, habit_id: int) -> bool: 
        """Validate a single field update for a habit.

        Args:
            field (str): Name of the field to update
            value (str): New value for the field
            habit_id (int): ID of the habit to update

        Returns:
            bool: True if update is valid, False otherwise
        """
        try:
            habit = Habit.get_by_id(habit_id)
            if not habit:
                return False
                
            data = habit.to_dict
            data[field.lower()] = value
            
            return HabitValidator.validate_habit_data(data, updating_field=field.lower())
        except Exception as e:
            return False, "Error validating update: {}".format(e)

    @staticmethod
    def validate_habit_data(data: Dict[str, Any], updating_field: Optional[str] = None) -> Tuple[bool, str]:
        """Validate habit data against business rules.

        Args:
            data (Dict[str, Any]): Habit data to validate containing required fields
            updating_field (Optional[str]): Field being updated, if any

        Returns:
            Tuple[bool, str]: (is_valid, message)
                - is_valid: True if data is valid
                - message: Validation message or error description
        """
        try:
            # Required fields check
            required_fields = [
                'name', 'category', 'description', 'start', 'end',
                'importance', 'repeat', 'tasks', 'tasks_description'
            ]
            for field in required_fields:
                if not data.get(field):
                    return False, f"Missing required field: {field}"
            
            # Tasks validation
            if not isinstance(data['tasks'], int) or data['tasks'] < 1:
                return False, "Tasks must be a positive integer"
            if data['tasks'] > 10:
                return False, "Maximum 10 tasks allowed per habit"
                
            # Date validations
            date_fields = ['start', 'end']
            dates = {}
            for field in date_fields:
                try:
                    dates[field] = datetime.strptime(data[field], '%Y-%m-%d')
                except ValueError:
                    return False, f"Invalid date format for {field}: Use YYYY-MM-DD"
            
            if dates['start'] >= dates['end']:
                return False, "Start date must be before end date"
                
            if updating_field == 'start' and dates['start'].date() < datetime.now().date():
                return False, "Start date cannot be in the past"
            
            # String length validations
            max_lengths = {
                'name': 50,
                'category': 30,
                'description': 200,
                'tasks_description': 50
            }
            for field, max_length in max_lengths.items():
                value = str(data[field]).strip()
                if len(value) > max_length:
                    return False, f"{field} exceeds maximum length of {max_length}"
                if len(value) < 1:
                    return False, f"{field} cannot be empty"
                data[field] = value  # Update with stripped value
            
            # Enum validations
            if data['importance'] not in ['Paused', 'Low', 'High']:
                return False, "Invalid importance level: Use Paused/Low/High"
                
            if data['repeat'] not in ['Daily', 'Weekly']:
                return False, "Invalid repeat value: Use Daily/Weekly"
                
            return True, "Valid habit data"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"

class TaskValidator:
    """Validates task-related data"""
    
    @staticmethod
    def validate_task_data(data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate task input data for a habit tracking system.
        This function checks if the provided task data meets all required criteria including
        presence of required fields, data type validations, and content restrictions.
        Args:
            data (Dict[str, Any]): A dictionary containing task data with the following keys:
                - habit_id: Identifier for the associated habit
                - task_number: Positive integer representing task sequence
                - task_description: String describing the task (1-50 characters)
                - due_date: Date string in 'YYYY-MM-DD' format
                - status: String ('pending', 'done', or 'ignore')
        Returns:
            Tuple[bool, str]: A tuple containing:
                - bool: True if validation passes, False otherwise
                - str: Success message if valid, error message if invalid
        """
        try:
            required_fields = [
                'habit_id', 'task_number', 'task_description',
                'due_date', 'status'
            ]
            for field in required_fields:
                if not data.get(field):
                    return False, f"Missing required field: {field}"
            
            # Task number validation
            if not isinstance(data['task_number'], int) or data['task_number'] < 1:
                return False, "Task number must be a positive integer"
            
            # Date validation
            try:
                datetime.strptime(data['due_date'], '%Y-%m-%d')
            except ValueError:
                return False, "Invalid due date format: Use YYYY-MM-DD"
            
            # Status validation
            if data['status'] not in ['pending', 'done', 'ignore']:
                return False, "Invalid status: Use pending/done/ignore"
            
            # Description length
            desc = str(data['task_description']).strip()
            if len(desc) > 50:
                return False, "Task description exceeds maximum length of 50"
            if len(desc) < 1:
                return False, "Task description cannot be empty"
            
            return True, "Valid task data"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
        
    @staticmethod
    def validate_status(status: str) -> bool:
        """Validate task status"""
        return status in ['pending', 'done', 'ignore'] 
    
