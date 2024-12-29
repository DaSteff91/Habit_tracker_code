from typing import Dict, List, Optional, Tuple
import questionary
from prettytable import PrettyTable
from datetime import datetime
from .core import BaseUI
from controllers.habit import HabitController
from utils.validators import HabitValidator

class HabitManagementUI(BaseUI):
    """Habit management specific UI handling"""
    
    def __init__(self, habit_controller=None):
        """Initialize UI with controllers and configuration"""
        super().__init__()
        self.habit_controller = habit_controller or HabitController()
        self.validator = HabitValidator()
        self.items_per_page = 15

    # Core UI Methods
    def show_habit_management(self):
        """Main habit management menu controller"""
        page = 1
        habits = self.get_habits_data()
        
        while True:
            self.clear_screen()
            self.show_navigation_hint()
            
            if habits:
                self.display_habits_table(habits, page)
                total_pages = self.get_total_pages(habits, self.items_per_page)
            
            choices = ["Create New Habit", "Update Habit", "Delete Habit"]
            if habits:
                if page > 1:
                    choices.append("Previous Page")
                if page < total_pages:
                    choices.append("Next Page")
            choices.append("Back to Main Menu")
            
            choice = questionary.select(
                "\nHabit Management Options:" if not habits else "Page {}/{}".format(page, total_pages),
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
                habits = self.get_habits_data()
                page = 1

    def handle_habit_management(self, action: str) -> None:
        """Route management actions"""
        if action == "Create New Habit":
            self.create_new_habit()
        elif action == "Update Habit":
            self.update_habit_workflow()
        elif action == "Delete Habit":
            self.delete_habit()

    # Display Methods
    def display_habits_table(self, habits: List[Dict], page: int = None) -> Tuple[Dict[int, int], List[Dict]]:
        """Display habits table with optional pagination"""
        try:
            if not habits:
                print("\nNo habits found")
                return {}, []

            start_idx = (page - 1) * self.items_per_page if page else 0
            end_idx = start_idx + self.items_per_page if page else len(habits)
            display_habits = habits[start_idx:end_idx]
            start_count = start_idx + 1

            habit_id_map = {}
            table = PrettyTable()
            table.field_names = ['Row'] + self.get_table_headers()
            
            for idx, habit in enumerate(display_habits, start_count):
                habit_id_map[idx] = habit['id']
                table.add_row([
                    idx,
                    habit['name'],
                    habit['category'],
                    habit['description'][:30],
                    habit['importance'],
                    habit['repeat'],
                    habit['start_date'],
                    habit['end_date'],
                    habit['tasks']
                ])
            
            print("\nHabits Overview:")
            print(table)
            return habit_id_map, habits

        except Exception as e:
            print("Error displaying habits: {}".format(e))
            return {}, []

    def get_table_headers(self) -> List[str]:
        """Get table headers"""
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

    # CRUD Operations
    def create_new_habit(self):
        """Handle habit creation workflow"""
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
                if not self.validator.validate_habit_data(answers):
                    return
                    
                self.show_habit_summary(answers)
                if self.confirm_action("Create this habit?"):
                    if self.habit_controller.create_habit(answers):
                        print("Habit created successfully!")
                    else:
                        print("Failed to create habit.")
        except Exception as e:
            print("Error creating habit: {}".format(e))

    def update_habit_workflow(self):
        """Handle habit update workflow"""
        habit_data = self.get_habit_for_update()
        if not habit_data:
            return False
            
        update_info = self.collect_update_info(habit_data)
        if not update_info:
            return False
            
        return self.confirm_and_process_update(update_info)

    def delete_habit(self):
        """Handle habit deletion workflow"""
        habits = self.get_habits_data()
        if not habits:
            print("\nNo habits found")
            return
            
        selected = self.select_habits_for_deletion(habits)
        if selected and self.confirm_deletion(selected):
            self.process_habit_deletion(selected)

    # Helper Methods
    def get_habits_data(self) -> Optional[List[Dict]]:
        """Fetch habits data through controller"""
        return self.habit_controller.get_habits()

    def get_total_pages(self, habits: List[Dict], items_per_page: int) -> int:
        """Calculate total pages needed"""
        return (len(habits) + items_per_page - 1) // items_per_page

    def show_habit_summary(self, data: Dict) -> None:
        """Display habit data summary"""
        print("\nHabit Summary:")
        print("-------------")
        for key, value in data.items():
            print("{}: {}".format(
                key.replace('_', ' ').title(),
                value
            ))

    def select_habits_for_deletion(self, habits: List[Dict]) -> List[int]:
        """Get user selection for deletion"""
        choices = [
            {
                "name": "Row {}: {} - {}".format(
                    idx, habit['name'], habit['description'][:30]
                ),
                "value": habit['id'],
                "checked": False
            }
            for idx, habit in enumerate(habits, 1)
        ]
        
        return questionary.checkbox(
            "Select habits to delete:",
            choices=choices,
            style=self.style
        ).ask()

    def confirm_deletion(self, selected_habits: List[int]) -> bool:
        """Get deletion confirmation"""
        return questionary.confirm(
            "\nDelete {} habit(s)?".format(len(selected_habits)),
            default=False,
            style=self.style
        ).ask()

    def process_habit_deletion(self, habit_ids: List[int]) -> None:
        """Process habit deletions"""
        for habit_id in habit_ids:
            if self.habit_controller.delete_habit(habit_id):
                print("Successfully deleted habit {}".format(habit_id))
            else:
                print("Failed to delete habit {}".format(habit_id))