from typing import Dict, List, Optional, Tuple
import questionary
from prettytable import PrettyTable
from datetime import datetime
from .core import BaseUI
from habit_management import HabitManagement
from ui_db_handler import UserInputHandler, InputValidator

class HabitManagementUI(BaseUI):
    """Habit management specific UI"""
    def __init__(self):
        super().__init__()
        self.habit_management = HabitManagement()
        self.ui_handler = UserInputHandler()
        self.validator = InputValidator()

    def show_habit_management(self):
        """Show habit management menu and handle interactions"""
        while True:
            self.clear_screen()
            self.show_navigation_hint()
            
            choice = questionary.select(
                "Habit Management Options:",
                choices=[
                    "Create New Habit",
                    "Update Habit",
                    "Delete Habit",
                    "Back to Main Menu"
                ],
                style=self.style
            ).ask()
            
            if choice == "Back to Main Menu":
                break

            if choice == "Update Habit":
                self.update_habit_workflow() 
                
            self.handle_habit_management(choice)
            
            if not questionary.confirm(
                "Return to Habit Management menu?",
                default=True,
                style=self.style
            ).ask():
                break

    def handle_habit_management(self, action: str) -> None:
        """Handle habit management actions"""
        if action == "Create New Habit":
            self.create_new_habit()
        elif action == "Update Habit":
            self.update_habit_workflow()
        elif action == "Delete Habit":
            self.handle_habit_deletion()

    def create_new_habit(self):
        """Get habit data from user with validation"""
        questions = [
            {
                "type": "text",
                "name": "name",
                "message": "Enter habit name:",
                "instruction": "(e.g. Morning Yoga)"
            },
            {
                "type": "text",
                "name": "category",
                "message": "Enter habit category:",
                "instruction": "(e.g. Health/Fitness)"
            },
            {
                "type": "text",
                "name": "description",
                "message": "Enter habit description:",
                "instruction": "(e.g. 15 minutes morning yoga routine)"
            },
            {
                "type": "select",
                "name": "importance",
                "message": "Select importance level:",
                "choices": ["High", "Low"]
            },
            {
                "type": "select",
                "name": "repeat",
                "message": "Select repeat interval:",
                "choices": ["Daily", "Weekly"]
            },
            {
                "type": "text",
                "name": "start",
                "message": "Enter start date:",
                "instruction": "(Format: YYYY-MM-DD)"
            },
            {
                "type": "text",
                "name": "stop",
                "message": "Enter end date:",
                "instruction": "(Format: YYYY-MM-DD)"
            },
            {
                "type": "text",
                "name": "tasks",
                "message": "Enter number of tasks:",
                "instruction": "(Enter a number between 1-10)"
            },
            {
                "type": "text",
                "name": "tasks_description",
                "message": "Enter tasks description:",
                "instruction": "(e.g. Complete one yoga session)"
            }
        ]

        try:
            self.clear_screen()
            self.show_navigation_hint()
            answers = questionary.prompt(questions, style=self.style)
            
            if answers:
                answers['tasks'] = int(answers['tasks'])
                self.show_habit_summary(answers)
                
                if questionary.confirm(
                    "\nCreate this habit?",
                    default=False,
                    style=self.style
                ).ask():
                    if self.ui_handler.process_habit_input(answers):
                        print("Habit created successfully!")
                    else:
                        print("Failed to create habit.")
        except Exception as e:
            print(f"Error creating habit: {e}")

    def show_habit_summary(self, answers: Dict) -> None:
        """Display summary of habit data"""
        print("\nHabit Summary:")
        print("-------------")
        for key, value in answers.items():
            print("{}: {}".format(
                key.replace('_', ' ').title(),
                value
            ))

    def select_field(self, valid_fields: set) -> Optional[str]:
        """Get field selection from user"""
        choices = [field.title() for field in valid_fields]
        choices.append("Cancel")
        
        selected = questionary.select(
            "Select field to update:",
            choices=choices,
            style=self.style
        ).ask()
        
        if selected == "Cancel":
            return None
            
        return selected.lower()

    def update_habit_workflow(self):
        """Control flow for habit updates"""
        habit_data = self.get_habit_for_update()
        if not habit_data:
            return False
            
        update_info = self.collect_update_info(habit_data)
        if not update_info:
            return False
            
        return self.confirm_and_process_update(update_info)

    def get_habit_for_update(self) -> Optional[Dict]:
        """Get habit to update"""
        habit_id_map, habits = self.habit_management.display_habits_with_rows()
        if not habits:
            return None
            
        row_id = self.select_habit_for_update(habits)
        if not row_id:
            return None
            
        return {
            'row_id': row_id,
            'habit_id': habit_id_map[row_id],
            'habits': habits
        }
        
    def collect_update_info(self, habit_data: Dict) -> Optional[Dict]:
        """Collect field and value for update"""
        valid_fields = self.habit_management.get_field_choice()
        field = self.select_field(valid_fields)
        if not field:
            return None
            
        habit = next(h for h in habit_data['habits'] 
                    if h[0] == habit_data['habit_id'])
        value = self.get_field_value(field, habit)
        if not value:
            return None
            
        return {
            'habit_id': habit_data['habit_id'],
            'field': field,
            'value': value,
            'row_id': habit_data['row_id']
        }
        
    def confirm_and_process_update(self, update_info: Dict) -> bool:
        """Confirm and process the update"""
        if not self.confirm_update(
            update_info['row_id'], 
            update_info['field'], 
            update_info['value']
        ):
            return False
            
        return self.ui_handler.process_habit_update(
            update_info['habit_id'],
            update_info['field'],
            update_info['value']
        )

    def delete_habit(self):
        """Delete habit workflow"""
        habits = self.get_habits_data()
        if not habits:
            print("\nNo habits found")
            return
            
        choices = [
            {
                "name": f"Row {idx}: {habit[1]} - {habit[3][:30]}",
                "value": habit[0],
                "checked": False
            }
            for idx, habit in enumerate(habits, 1)
        ]
        
        selected = questionary.checkbox(
            "Select habits to delete:",
            choices=choices,
            style=self.style
        ).ask()
        
        if selected and questionary.confirm(
            f"\nDelete {len(selected)} habit(s)?",
            default=False,
            style=self.style
        ).ask():
            for habit_id in selected:
                if self.ui_handler.delete_habit(habit_id):
                    print(f"Deleted habit {habit_id}")
                else:
                    print(f"Failed to delete habit {habit_id}")

    def handle_habit_deletion(self):
        """Handle habit deletion workflow"""
        habits = self.get_habits_data()
        if not habits:
            print("\nNo habits found")
            return
            
        choices = [
            {
                "name": "Row {}: {} - {}".format(
                    idx,
                    habit[1],
                    habit[3][:30]
                ),
                "value": habit[0],
                "checked": False
            }
            for idx, habit in enumerate(habits, 1)
        ]
        
        selected = questionary.checkbox(
            "Select habits to delete:",
            choices=choices,
            style=self.style
        ).ask()
        
        if selected and questionary.confirm(
            "\nDelete {} habit(s)?".format(len(selected)),
            default=False,
            style=self.style
        ).ask():
            for habit_id in selected:
                if self.ui_handler.delete_habit(habit_id):
                    print("Successfully deleted habit {}".format(habit_id))
                else:
                    print("Failed to delete habit {}".format(habit_id))

    def validate_habit_data(self, data: Dict) -> bool:
        """Validate habit input data"""
        try:
            # Validate dates
            datetime.strptime(data['start'], '%Y-%m-%d')
            datetime.strptime(data['stop'], '%Y-%m-%d')
            
            # Validate tasks number
            if not (1 <= int(data['tasks']) <= 10):
                print("Tasks must be between 1 and 10")
                return False
                
            return True
        except ValueError as e:
            print("Invalid data format: {}".format(e))
            return False

    def get_field_value(self, field: str, habit: tuple) -> Optional[str]:
        """Get new value for field with validation"""
        try:
            if field in ["start", "stop"]:
                value = questionary.text(
                    "Enter new {} (YYYY-MM-DD):".format(field),
                    style=self.style
                ).ask()
                
                if value:
                    try:
                        datetime.strptime(value, '%Y-%m-%d')
                        return value
                    except ValueError:
                        print("Invalid date format. Use YYYY-MM-DD")
                        return None
                        
            elif field == "importance":
                return questionary.select(
                    "Select new importance level:",
                    choices=["High", "Low", "Paused"],
                    style=self.style
                ).ask()
                
            elif field == "repeat":
                return questionary.select(
                    "Select new repeat interval:",
                    choices=["Daily", "Weekly"],
                    style=self.style
                ).ask()
                
            else:
                return questionary.text(
                    "Enter new {}:".format(field),
                    style=self.style
                ).ask()
                
        except Exception as e:
            print("Error getting field value: {}".format(e))
            return None

    def display_current_values(self, habit: tuple, updates: Dict) -> None:
        """Display current habit values"""
        print("\nCurrent Values:")
        print("-------------")
        fields = {
            'Category': habit[2],
            'Description': habit[3],
            'Start Date': habit[5],
            'End Date': habit[6],
            'Importance': habit[7],
            'Repeat': habit[8]
        }
        
        for field, value in fields.items():
            print(f"{field}: {value}")

    def show_updates_summary(self, updates: Dict) -> None:
        """Show summary of updates to be made"""
        print("\nUpdates to apply:")
        for field, value in updates.items():
            print("{}: {}".format(field.title(), value))

    def confirm_update(self, row_id: int, field: str, value: str) -> bool:
        """Get user confirmation for update"""
        return questionary.confirm(
            "\nUpdate row {}'s {} to '{}'?".format(row_id, field, value),
            default=False,
            style=self.style
        ).ask()

    def continue_updating(self) -> bool:
        """Ask if user wants to continue updating"""
        return questionary.confirm(
            "\nUpdate another field?",
            default=True,
            style=self.style
        ).ask()

    def select_habit_for_update(self, habits: List[tuple]) -> Optional[int]:
        """UI method to select habit for update"""
        choices = [
            f"Row {idx}: {habit[1]} - {habit[3][:30]}"
            for idx, habit in enumerate(habits, 1)
        ]
        choices.append("Cancel")
        
        selected = questionary.select(
            "Select habit to update (or Cancel):",
            choices=choices,
            style=self.style
        ).ask()
        
        if selected == "Cancel":
            return None
            
        return int(selected.split(':')[0].replace('Row ', ''))
    
    def show_habit_management(self):
        """Show habit management menu and handle interactions"""
        page = 1
        ITEMS_PER_PAGE = 15
        habits = self.get_habits_data()
        
        while True:
            self.clear_screen()
            self.show_navigation_hint()
            
            if habits:
                self.display_paginated_habits(habits, page, ITEMS_PER_PAGE)
                total_pages = self.get_total_pages(habits, ITEMS_PER_PAGE)
            
            choices = ["Create New Habit", "Update Habit", "Delete Habit"]
            if habits:
                if page > 1:
                    choices.append("Previous Page")
                if page < total_pages:
                    choices.append("Next Page")
            choices.append("Back to Main Menu")
            
            choice = questionary.select(
                "\nHabit Management Options:" if not habits else f"\nPage {page}/{total_pages}",
                choices=choices,
                style=self.style
            ).ask()
            
            if choice == "Back to Main Menu":
                break
                
            elif choice == "Next Page":
                page = min(page + 1, total_pages)
            elif choice == "Previous Page":
                page = max(page - 1, 1)
            else:
                self.handle_habit_management(choice)
                habits = self.get_habits_data()  # Refresh data
                page = 1  # Reset to first page

    def get_habits_data(self) -> Optional[List[tuple]]:
        """Fetch habits data"""
        return self.ui_handler.db_controller.read_data('habit')

    def get_total_pages(self, habits: List[tuple], items_per_page: int) -> int:
        """Calculate total pages"""
        return (len(habits) + items_per_page - 1) // items_per_page

    def display_paginated_habits(self, habits: List[tuple], page: int, items_per_page: int) -> None:
        """Display paginated habits table"""
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        page_habits = habits[start_idx:end_idx]
        
        table = PrettyTable()
        table.field_names = [
            'Row',
            'Name',
            'Category',
            'Description',
            'Importance',
            'Repeat',
            'Start Date',
            'End Date',
            'Tasks'
        ]
        
        for idx, habit in enumerate(page_habits, start=start_idx + 1):
            table.add_row([
                idx,
                habit[1],  # Name
                habit[2],  # Category
                habit[3][:30],  # Description (truncated)
                habit[7],  # Importance
                habit[8],  # Repeat
                habit[5],  # Start Date
                habit[6],  # End Date
                habit[9]   # Tasks
            ])
        
        print("\nHabits Overview:")
        print(table)