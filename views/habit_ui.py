from typing import Dict, List, Optional, Tuple
import questionary
from prettytable import PrettyTable
from .core import BaseUI
from controllers.habit import HabitController
from utils.validators import HabitValidator

class HabitManagementUI(BaseUI):
    """Habit management specific UI handling"""

    # Table configuration
    TABLE_HEADERS = [
        'Row', 'Name', 'Category', 'Description',
        'Importance', 'Repeat', 'Start Date',
        'End Date', 'Tasks'
    ]
    
    COLUMN_WIDTHS = {
        'Row': 4,
        'Name': 20,
        'Category': 15,
        'Description': 50,
        'Importance': 10,
        'Repeat': 8,
        'Start Date': 12,
        'End Date': 12,
        'Tasks': 6
    }

    # Menu configuration
    MENU_CHOICES = ["Create New Habit", "Update Habit", "Delete Habit"]
    DEFAULT_WIDTH = 15
    ITEMS_PER_PAGE = 15
    
    # Initialization
    def __init__(self, habit_controller=None):
        """Initialize UI with controllers and configuration"""
        super().__init__()
        self.habit_controller = habit_controller or HabitController()
        self.validator = HabitValidator()
        self.items_per_page = self.ITEMS_PER_PAGE

    # Main Menu Flow
    def show_habit_management(self):
        """Main habit management menu controller"""
        page = 1
        habits = self._get_habits_data()
        
        while True:
            self._clear_screen()
            self._show_navigation_hint()
            
            # Display habits table first
            if habits:
                habit_id_map, _ = self._display_habits_table(habits, page)
                total_pages = self._get_total_pages(habits, self.items_per_page)
                
            # Show menu options
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
                habits = self._get_habits_data()  # Refresh data after action
                page = 1  # Reset to first page

    def handle_habit_management(self, action: str) -> None:
        """Route management actions"""
        if action == "Create New Habit":
            self.create_new_habit()
        elif action == "Update Habit":
            self.update_habit_workflow()
        elif action == "Delete Habit":
            self.delete_habit()

    # Display Methods
    def _display_habits_table(self, habits: List[Dict], page: int = None) -> Tuple[Dict[int, int], List[Dict]]:
        """Displays the habits in a formatted table view.
        This method creates and displays a table containing habit information using the prettytable library.
        It maps internal row numbers to actual habit IDs and handles pagination if enabled.
        Args:
            habits (List[Dict]): List of habit dictionaries containing habit information
            page (int, optional): Page number for pagination. Defaults to None.
        Returns:
            Tuple[Dict[int, int], List[Dict]]: A tuple containing:
                - Dictionary mapping display row numbers to actual habit IDs
                - List of habits displayed in the table
        """

        if not habits:
            print("\nNo habits found")
            return {}, []
                
        table = self._initialize_table()
        self._configure_columns(table)
        habit_id_map = self._add_habit_rows(table, habits, page)
        self._display_table(table)
        
        return habit_id_map, habits

    def _initialize_table(self) -> PrettyTable:
        """Initialize table with headers"""
        table = PrettyTable()
        table.field_names = self.TABLE_HEADERS
        table.align = "l"
        table.hrules = 1
        return table

    def _configure_columns(self, table: PrettyTable) -> None:
            """Configure column widths"""
            for header in table.field_names:
                table._max_width[header] = self.COLUMN_WIDTHS.get(header, self.DEFAULT_WIDTH)

    def _add_habit_rows(self, table: PrettyTable, habits: List[Dict], page: int) -> Dict[int, int]:
        """Add habit rows with pagination"""
        start_idx = (page - 1) * self.items_per_page if page else 0
        end_idx = start_idx + self.items_per_page if page else len(habits)
        page_habits = habits[start_idx:end_idx]
        start_count = start_idx + 1
        
        habit_id_map = {}
        for idx, habit in enumerate(page_habits, start_count):
            habit_id_map[idx] = habit['id']
            table.add_row([
                idx,
                habit['name'],
                habit['category'],
                habit['description'][:30],
                habit['importance'],
                habit['repeat'],
                habit['start'],
                habit['end'],
                habit['tasks']
            ])
        return habit_id_map

    def _display_table(self, table: PrettyTable) -> None:
        """Display formatted table"""
        print("\nHabits Overview:")
        print(table)

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
        """
        Creates a new habit by collecting user input, validating it, showing a summary and confirming creation.
        This method orchestrates the complete workflow of habit creation by:
        1. Collecting user input for the new habit
        2. Validating and processing the input
        3. Showing a summary of the habit to be created
        4. Confirming with the user
        5. Processing the final creation
        Returns:
            None
        """

        try:
            self._clear_screen() 
            answers = self.get_habit_input()
            if not answers:
                return
                
            if not self.validate_and_process_input(answers):
                return
                
            self._show_habit_summary(answers)
            if self.confirm_creation(answers):
                self.process_habit_creation(answers)
                
        except Exception as e:
            print("Error in creation workflow: {}".format(e))

    def get_habit_input(self) -> Optional[Dict]:
        """Get habit input from user"""
        questions = self.get_habit_questions()
        answers = questionary.prompt(questions, style=self.style)
        
        if not answers:
            return None
            
        return answers

    def get_habit_questions(self) -> List[Dict]:
        """
        This method defines the structure and content of the questions that will be
        presented to the user when creating a new habit. Each dictionary in the list
        represents a question with specific attributes.

        Returns:
            List[Dict]: A list of dictionaries where each dictionary contains the following keys:
                - type (str): The type of input field ('text' or 'select')
                - name (str): The identifier for the question
                - message (str): The question prompt shown to the user
                - instruction (str, optional): Additional guidance for the user
                - choices (List[str], optional): Available options for 'select' type questions
        """

        return [
            {
                "type": "text",
                "name": "name",
                "message": "Enter habit name (CTRL+C to cancel):",
                "instruction": "(e.g. Morning Yoga)"
            },
            {
                "type": "text",
                "name": "category",
                "message": "Enter habit category (CTRL+C to cancel):",
                "instruction": "(e.g. Health/Fitness)"
            },
            {
                "type": "text",
                "name": "description",
                "message": "Enter habit description (CTRL+C to cancel):",
                "instruction": "(e.g. 15 minutes morning yoga routine)"
            },
            {
                "type": "select",
                "name": "importance",
                "message": "Select importance level (CTRL+C to cancel):",
                "choices": ["High", "Low"]
            },
            {
                "type": "select",
                "name": "repeat",
                "message": "Select repeat interval (CTRL+C to cancel):",
                "choices": ["Daily", "Weekly"]
            },
            {
                "type": "text",
                "name": "start",
                "message": "Enter start date (CTRL+C to cancel):",
                "instruction": "(Format: YYYY-MM-DD)"
            },
            {
                "type": "text",
                "name": "end",
                "message": "Enter end date (CTRL+C to cancel):",
                "instruction": "(Format: YYYY-MM-DD)"
            },
            {
                "type": "text",
                "name": "tasks",
                "message": "Enter number of tasks (CTRL+C to cancel):",
                "instruction": "(Enter a number between 1-10)"
            },
            {
                "type": "text",
                "name": "tasks_description",
                "message": "Enter tasks description (CTRL+C to cancel):",
                "instruction": "(e.g. Complete one yoga session)"
            }
        ]

    def validate_and_process_input(self, answers: Dict) -> bool:
        """Validates and processes the user input for habit creation.
        This method converts the 'tasks' value to an integer and validates the habit data.

        Args:
            answers (Dict): A dictionary containing the habit information including:
                - tasks: The number of tasks to complete (should be convertible to int)
                - Other habit-related key-value pairs

        Returns:
            bool: True if validation succeeds, False if validation fails or type conversion fails
        """

        try:
            answers['tasks'] = int(answers['tasks'])
            return self.validator.validate_habit_data(answers)
        except ValueError:
            print("\nInvalid task number")
            return False

    def confirm_creation(self, answers: Dict) -> bool:
        """Get confirmation for habit creation"""
        return questionary.confirm(
            "Create this habit?",
            default=False,
            style=self.style
        ).ask()

    def process_habit_creation(self, answers: Dict) -> None:
        """Process habit creation and show feedback"""
        self._clear_screen()

        if self.habit_controller.create_habit(answers):
            print("\nHabit created successfully!")
            input("\nPress Enter to continue...")
            self._clear_screen()
        else:
            print("\nFailed to create habit")
            input("\nPress Enter to continue...")
            self._clear_screen()

    def update_habit_workflow(self):
        """
        Manages the workflow for updating a habit in the habit tracking system.
        This method coordinates the habit update process by:
        1. Prompting for habit selection
        2. Getting update details from user
        3. Processing the actual update
        Returns:
            bool: True if update was successful, False if update failed or was cancelled

        """

        try:
            self._clear_screen()
            habit_id = self.select_habit_for_update()
            
            # Early return if user cancels habit selection
            if not habit_id:
                self._clear_screen()  # Clear screen before returning
                return False
                
            field, value = self.get_update_details()
            if not field or not value:
                self._clear_screen()  # Clear screen before returning
                return False
                
            success = self._process_habit_update(habit_id, field, value)
            if success:
                print("\nHabit updated successfully!")
            else:
                print("\nFailed to update habit")
            input("\nPress Enter to continue...")
            self._clear_screen()
            return success
            
        except Exception as e:
            print("Error in update workflow: {}".format(e))
            return False

    def select_habit_for_update(self) -> Optional[int]:
        """Get habit selection for update"""
        habits = self._get_habits_data()  # This displays the table
        if not habits:
            print("\nNo habits found")
            return None
        
        # Create choices with row numbers
        choices = [
            {
                "name": "Row {}: {} - {}".format(
                    idx, habit['name'], habit['description'][:30]
                ),
                "value": habit['id']
            }
            for idx, habit in enumerate(habits, 1)
        ]
        choices.append({
            "name": "Cancel",
            "value": None
        })
        
        # Show selection menu after table is displayed
        selected = questionary.select(
            "\nSelect habit to update:",
            choices=choices,
            style=self.style
        ).ask()
        
        if selected is None:
            print("\nUpdate cancelled")
            
        return selected

    def get_update_details(self) -> Tuple[Optional[str], Optional[str]]:
        """Gets user input for updating a habit field.
        This method presents a selection menu for the user to choose which field of a habit to update,
        and then prompts for the new value of that field. It handles the input validation through
        questionary's built-in functionality.
        Returns:
            Tuple[Optional[str], Optional[str]]: A tuple containing:
                - The selected field name (without examples)
                - The new value for the selected field
                If user selects "Cancel", returns (None, None)
        """

        field = questionary.select(
            "Select field to update:",
            choices=[
                "Category (e.g. Health/Fitness)",
                "Description (e.g. 15 minutes morning routine)",
                "Start Date (Format: YYYY-MM-DD)",
                "End Date (Format: YYYY-MM-DD)",
                "Importance (High/Low)",
                "Repeat (Daily/Weekly)",
                "Cancel"
            ],
            style=self.style
        ).ask()
    
        if field == "Cancel":
            return None, None
            
        # Extract actual field name without example
        field = field.split(" (")[0]
        
        # Get appropriate instruction based on field
        instruction = self._get_field_instruction(field)
        
        value = questionary.text(
            "Enter new value for {}:".format(field),
            instruction=instruction,
            style=self.style
        ).ask()

        return field, value

    def _get_field_instruction(self, field: str) -> str:
        """Get field-specific instruction"""
        instructions = {
            "Category": "(e.g. Health/Fitness)",
            "Description": "(e.g. 15 minutes morning routine)",
            "Start Date": "(Format: YYYY-MM-DD)",
            "End Date": "(Format: YYYY-MM-DD)",
            "Importance": "(Enter: High or Low)",
            "Repeat": "(Enter: Daily or Weekly)"
        }
        return instructions.get(field, "")

    def _process_habit_update(self, habit_id: int, field: str, value: str) -> bool:
        """Process habit update"""
        try:
            if field == 'Start Date':
                db_field = 'start'
            elif field == 'End Date':
                db_field = 'end'
            else:
                db_field = field
                
            if questionary.confirm(
                "Update {}?".format(field),
                default=False,
                style=self.style
            ).ask():
                return self.habit_controller.update_habit(habit_id, db_field, value)
            return False
        except Exception as e:
            print("Error updating habit: {}".format(e))
            return False
        
    def delete_habit(self):
        """
        Manages the workflow for deleting one or multiple habits.
        This method coordinates the habit deletion process by:
        1. Allowing user to select habits for deletion
        2. Confirming deletion with user
        3. Processing the actual deletion of selected habits
        Returns:
            None
        """

        try:
            self._clear_screen() 
            selected_habits = self._select_habits_for_deletion()
            if not selected_habits:
                return
                
            if self._confirm_deletion(selected_habits):
                self._process_habit_deletion(selected_habits)
        except Exception as e:
            print("Error in deletion workflow: {}".format(e))

    # Helper Methods
    def _get_habits_data(self) -> Optional[List[Dict]]:
        """Fetch habits data through controller"""
        return self.habit_controller.get_habits()

    def _get_total_pages(self, habits: List[Dict], items_per_page: int) -> int:
        """Calculate total pages needed"""
        return (len(habits) + items_per_page - 1) // items_per_page

    def _show_habit_summary(self, data: Dict) -> None:
        """Display habit data summary"""
        print("\nHabit Summary:")
        print("-------------")
        for key, value in data.items():
            print("{}: {}".format(
                key.replace('_', ' ').title(),
                value
            ))

    def _select_habits_for_deletion(self) -> Optional[List[int]]:
        """Get habit selection for deletion"""
        habits = self._get_habits_data()
        if not habits:
            print("\nNo habits found")
            return None
            
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
        choices.append({
            "name": "Cancel",
            "value": "cancel",
            "checked": False
        })
        
        selected = questionary.checkbox(
            "Select habits to delete (or Cancel):",
            choices=choices,
            style=self.style
        ).ask()
        
        if not selected or "cancel" in selected:
            print("\nDeletion cancelled")
            return None
            
        return selected

    def _confirm_deletion(self, selected_habits: List[int]) -> bool:
        """Get deletion confirmation"""
        return questionary.confirm(
            "\nDelete {} habit(s)?".format(len(selected_habits)),
            default=False,
            style=self.style
        ).ask()

    def _process_habit_deletion(self, habit_ids: List[int]) -> None:
        """Execute habit deletion"""
        for habit_id in habit_ids:
            if self.habit_controller.delete_habit(habit_id):
                print("Habit and associated tasks sucessfully deleted")
            else:
                print("Failed to delete habit {}".format(habit_id))