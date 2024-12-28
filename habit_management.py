from prettytable import PrettyTable
from database.operations import DatabaseController
from ui_db_handler import UserInputHandler, InputValidator
from datetime import datetime
from typing import List, Tuple, Dict, Optional

# Remove any imports from user_interface.py

class HabitManagement:
    def __init__(self):
        self.db_controller = DatabaseController()
        self.ui_handler = UserInputHandler()
        self.habit_headers = self.db_controller.get_table_headers('habit')
        self.validator = InputValidator()
        

    def get_table_headers(self) -> List[str]:
        """Return headers for habit management table"""
        return [
            'Name',
            'Category',
            'Description',
            'Importance',
            'Repeat',
            'Start Date',
            'End Date',
            'Tasks'
        ]

    def display_habits_with_rows(self) -> Dict[int, int]:
        """Display habits with row numbers"""
        habits = self.db_controller.read_data('habit')
        habit_id_map = {}
        row_number = 1
        
        if not habits:
            print("No habits found")
            return {}, []
        
        table = PrettyTable()
        table.field_names = ['Row'] + self.get_table_headers()
        
        for habit in habits:
            habit_id_map[row_number] = habit[0]
            table.add_row([
                row_number,
                habit[1],          # Name
                habit[2],          # Category
                habit[3],          # Description
                habit[7],          # Importance
                habit[8],          # Repeat
                habit[5],          # Start Date
                habit[6],          # End Date
                habit[9]           # Tasks
            ])
            row_number += 1
        
        print("\nHabits Overview:")
        print(table)
        return habit_id_map, habits

    def get_field_choice(self) -> Optional[str]:
        """Get valid field name for update"""
        valid_fields = {
            'category',
            'description',
            'start',
            'stop',
            'importance',
            'repeat'
        }
        return valid_fields

    def update_habit(self, row_id: int, habit_id_map: Dict[int, int]) -> bool:
        """Business logic for habit updates"""
        try:
            # Get habit ID from map
            habit_id = habit_id_map.get(row_id)
            if not habit_id:
                print("Invalid row ID")
                return False
                
            # Get habit data
            habit = self.db_controller.read_data('habit', {'id': habit_id})
            if not habit:
                print("Habit not found")
                return False
                
            # Get field choice
            valid_fields = self.get_field_choice()
            if not valid_fields:
                return False
                
            # Get update info
            update_info = self.get_update_info(habit_id)
            if not update_info:
                return False
                
            field, value = update_info
                
            # Validate and process update
            if self.validate_update(habit_id, field, value):
                return self.process_habit_update(habit_id, field, value)
                
            return False
            
        except Exception as e:
            print("Error updating habit: {}".format(e))
            return False

    def get_update_info(self, habit_id: int) -> Optional[Tuple[str, str]]:
        """Get field and value for update"""
        field = self.get_field_choice()
        if not field:
            return None
            
        value = self.get_field_value(field, habit_id)
        if not value:
            return None
            
        if self.validate_update(habit_id, field, value):
            return (field, value)
        return None

    def validate_update(self, habit_id: int, field: str, value: str) -> bool:
        """Validate update data"""
        habit_data = self.db_controller.read_data('habit', {'id': habit_id})[0]
        update_data = {
            'name': habit_data[1],
            'category': habit_data[2],
            'description': habit_data[3],
            'start': habit_data[5],
            'stop': habit_data[6],
            'importance': habit_data[7],
            'repeat': habit_data[8],
            'tasks': habit_data[9],
            'tasks_description': habit_data[10]
        }
        update_data[field] = value
        
        is_valid, message = self.validator.validate_habit_data(update_data, field)
        if not is_valid:
            print("Invalid input: {}".format(message))
        return is_valid

    def process_habit_update(self, habit_id: int, field: str, value: str) -> bool:
        """Process habit update in database"""
        if field == 'importance' and value == 'Paused':
            return self.ui_handler.pause_habit(habit_id)
        return self.ui_handler.update_habit(habit_id, {field: value})


    def run(self) -> None:
        """Main execution loop"""
        while True:
            habit_id_map = self.display_habits_with_rows()
            if not habit_id_map:
                break
                
            if not self.update_habit(habit_id_map):
                break

def main():
    management = HabitManagement()
    management.run()

if __name__ == "__main__":
    main()