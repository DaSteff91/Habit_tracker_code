import sys
import os
from questionary import Style, Validator, ValidationError
import questionary
from task_overview import TaskOverview
from analytics_management import HabitAnalytics
from habit_management import HabitManagement
from ui_db_handler import UserInputHandler, InputValidator
from database.operations import DatabaseController
from typing import List, Tuple, Dict, Optional
from datetime import datetime
from prettytable import PrettyTable

class HabitUI:
    """Main UI class for habit tracker application"""
    
    def __init__(self):
        self._init_components()
        self._init_style()
        self.current_sort = {
            'field': None,
            'ascending': True
        }

    def _init_components(self):
        """Initialize all UI components"""
        self.validator = InputValidator()
        self.ui_handler = UserInputHandler()
        self.db_controller = DatabaseController()
        self.analytics = HabitAnalytics()
        self.habit_management = HabitManagement()
        
    def _init_style(self):
        """Initialize UI style configuration"""
        self.style = Style([
            ('qmark', 'fg:yellow bold'),
            ('question', 'bold'),
            ('answer', 'fg:green bold'),
            ('pointer', 'fg:yellow bold'),
            ('selected', 'fg:green'),
            ('instruction', 'fg:blue'),
            ('example', 'fg:gray italic')
        ])

    def clear_screen(self):
        """Clear terminal screen and reset cursor position"""
        try:
            # Clear screen and reset cursor for Linux/Mac
            os.system('clear && tput cup 0 0')
        except Exception as e:
            # Fallback if clear fails
            print('\n' * 100)
            print("Error clearing screen: {}".format(e))

    def show_navigation_hint(self):
        """Show navigation instructions"""
        print("\nNavigation: Use ↑↓ arrow keys to move, Enter/Return to select")

    # Display Methods
    def display_task_table(self, headers: List[str], tasks: List[List]) -> None:
        """Display formatted task table"""
        table = PrettyTable()
        table.field_names = headers
        for task in tasks:
            table.add_row(task)
        print("\nPending Tasks:")
        print(table)

    def display_habit_table(self, table: PrettyTable) -> None:
        """Display habit table with header"""
        print("\nHabits Overview:")
        print(table)

    def display_habit_details(self, habit_id: int) -> None:
        """Display detailed habit information"""
        habit = self.db_controller.read_data('habit', {'id': habit_id})[0]
        detail_table = self._create_detail_table(habit)
        print("\nHabit Details:")
        print(detail_table)

    # Menu Methods
    def main_menu(self):
        """Main menu navigation"""
        while True:
            self.clear_screen()
            self.show_navigation_hint()
            
            choice = questionary.select(
                "What would you like to do?",
                choices=[
                    "Task Overview",
                    "Habit Management",
                    "Analytics",
                    "Help",
                    "Exit"
                ],
                style=self.style
            ).ask()

            if choice == "Exit":
                if questionary.confirm(
                    "Do you really want to exit?",
                    default=False,
                    style=self.style
                ).ask():
                    self.clear_screen()
                    print("Thank you for using the Habit Tracker!")
                    sys.exit(0)
                continue

            self.handle_menu_choice(choice)

    def handle_menu_choice(self, choice: str) -> None:
        """Handle main menu selections"""
        self.clear_screen()
        self.show_navigation_hint()
        
        if choice == "Task Overview":
            self.show_task_overview()
        elif choice == "Habit Management":
            self.show_habit_management()
        elif choice == "Analytics":
            self.show_analytics_menu()
        elif choice == "Help":
            self.show_help()

    def show_analytics_menu(self):
        """Main analytics menu controller"""
        page = 1
        ITEMS_PER_PAGE = 15
        habits = self.get_habits_data()
        
        while True:
            if not habits:
                print("\nNo habits found")
                break
                
            # Display current page
            self.display_paginated_analytics(habits, page, ITEMS_PER_PAGE)
            
            # Show options with page info
            total_pages = self.get_total_pages(habits, ITEMS_PER_PAGE)
            
            choices = ["Filter Habits", "Sort Habits", "Reset View"]
            if page > 1:
                choices.append("Previous Page")
            if page < total_pages:
                choices.append("Next Page")
            choices.append("Back to Main Menu")
            
            action = questionary.select(
                f"\nPage {page} of {total_pages}",
                choices=choices,
                style=self.style
            ).ask()
            
            if action == "Back to Main Menu":
                break
            elif action == "Next Page":
                page = min(page + 1, total_pages)
            elif action == "Previous Page":
                page = max(page - 1, 1)
            elif action == "Reset View":
                habits = self.get_habits_data()
                page = 1
                self.current_sort = {'field': None, 'ascending': True}
            elif action == "Sort Habits":
                habits = self.handle_sort_habits(habits)
            elif action == "Filter Habits":
                filtered = self.handle_filter_habits(habits)
                if filtered:
                    habits = filtered
                    page = 1

    def initialize_analytics_view(self) -> Optional[List[tuple]]:
        """Initialize analytics view with data"""
        self.clear_screen()
        self.show_navigation_hint()
        return self.get_habits_data()

    def display_current_analytics_page(self, habits: List[tuple], page: int, items_per_page: int) -> None:
        """Display current page of analytics"""
        self.clear_screen()
        self.show_navigation_hint()
        self.display_paginated_analytics(habits, page, items_per_page)

    def get_analytics_action(self) -> str:
        """Get user action choice for analytics"""
        return questionary.select(
            "Choose action:",
            choices=[
                "Filter Habits",
                "Sort Habits",
                "Back to Main Menu"
            ],
            style=self.style
        ).ask()

    def get_paginated_habits(self, habits: List[tuple], page: int, items_per_page: int) -> List[tuple]:
        """Get subset of habits for current page"""
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        return habits[start_idx:end_idx]

    def get_total_pages(self, habits: List[tuple], items_per_page: int) -> int:
        """Calculate total number of pages"""
        return (len(habits) + items_per_page - 1) // items_per_page

    def get_menu_choices(self, current_page: int, total_pages: int) -> List[str]:
        """Generate menu choices based on current page"""
        choices = ["Filter Habits", "Sort Habits"]
        if current_page > 1:
            choices.append("Previous Page")
        if current_page < total_pages:
            choices.append("Next Page")
        choices.append("Back to Main Menu")
        return choices

    def show_page_info(self, current_page: int, total_pages: int) -> None:
        """Display current page information"""
        print(f"\nPage {current_page} of {total_pages}")

    def fetch_and_display_analytics(self, page: int, items_per_page: int) -> Optional[List[tuple]]:
        """Fetch data and display analytics table"""
        self.clear_screen()
        self.show_navigation_hint()
        
        habits = self.get_habits_data()
        if habits:
            self.display_paginated_analytics(habits, page, items_per_page)
        return habits

    def show_analytics_options(self) -> str:
        """Display analytics menu options"""
        return questionary.select(
            "Choose action:",
            choices=[
                "Filter Habits",
                "Sort Habits",
                "Back to Main Menu"
            ],
            style=self.style,
            qmark=""
        ).ask()

    def handle_analytics_actions(self, habits: List[tuple], page: int, items_per_page: int) -> bool:
        """Handle user actions in analytics menu"""
        action = self.show_analytics_options()
        
        if action == "Back to Main Menu":
            return False
            
        updated_habits = self.process_analytics_action(habits, action)
        if not updated_habits:
            return False
            
        return self.handle_pagination(updated_habits, page, items_per_page)

    def process_analytics_action(self, habits: List[tuple], action: str, page: int) -> Tuple[List[tuple], int]:
        """Process selected analytics action"""
        if action == "Sort Habits":
            field = questionary.select(
                "Sort by:",
                choices=self.get_filterable_fields(),
                style=self.style
            ).ask()
            
            if field:
                order = questionary.select(
                    "Order:",
                    choices=["Ascending", "Descending"],
                    style=self.style
                ).ask()
                
                self.current_sort = {
                    'field': field.lower(),
                    'ascending': order == "Ascending"
                }
                
                sorted_habits = self.analytics.sort_habits(
                    habits,
                    self.current_sort['field'],
                    self.current_sort['ascending']
                )
                
                total_pages = self.get_total_pages(sorted_habits, 15)
                if page > total_pages:
                    page = total_pages
                    
                return sorted_habits, page
                
        elif action == "Filter Habits":
            filtered_habits = self.handle_filter_habits(habits)
            if filtered_habits and filtered_habits != habits:
                if self.current_sort['field']:  # Apply current sort to filtered results
                    filtered_habits = self.analytics.sort_habits(
                        filtered_habits,
                        self.current_sort['field'],
                        self.current_sort['ascending']
                    )
                return filtered_habits, 1
                
        return habits, page

    def get_habits_data(self) -> Optional[List[tuple]]:
        """Fetch habits data from database"""
        habits = self.db_controller.read_data('habit')
        if not habits:
            print("\nNo habits found")
            return None
        return habits

    def handle_analytics_action(self, habits: List[tuple]) -> Optional[List[tuple]]:
        """Handle analytics menu actions"""
        print("\nAnalytics Options:")
        action = questionary.select(
            "Choose action:",
            choices=[
                "Filter Habits",
                "Sort Habits",
                "Back to Main Menu"
            ],
            style=self.style,
            qmark=""
        ).ask()
        
        if action == "Back to Main Menu":
            return None
        elif action == "Sort Habits":
            return self.handle_sort_habits(habits)
        elif action == "Filter Habits":
            return self.handle_filter_habits(habits)
        return habits

    def handle_pagination(self, habits: List[tuple], page: int, items_per_page: int) -> Tuple[List[tuple], int]:
        """Handle pagination navigation while maintaining sort"""
        total_pages = self.get_total_pages(habits, items_per_page)
        
        if total_pages <= 1:
            return habits, page
            
        nav_choices = self.get_navigation_choices(page, total_pages)
        nav_action = questionary.select(
            f"\nPage {page}/{total_pages}",
            choices=nav_choices,
            style=self.style
        ).ask()
        
        if nav_action == "Next Page" and page < total_pages:
            return habits, page + 1
        elif nav_action == "Previous Page" and page > 1:
            return habits, page - 1
            
        return habits, page

    def get_navigation_choices(self, page: int, total_pages: int) -> List[str]:
        """Get available navigation choices"""
        choices = []
        if page > 1:
            choices.append("Previous Page")
        if page < total_pages:
            choices.append("Next Page")
        choices.extend(["Return to Analytics Menu", "Back to Main Menu"])
        return choices

    def process_navigation_action(self, action: str, page: int, total_pages: int) -> bool:
        """Process navigation action and return continue flag"""
        if action == "Next Page" and page < total_pages:
            page += 1
            return True
        elif action == "Previous Page" and page > 1:
            page -= 1
            return True
        elif action == "Back to Main Menu":
            return False
        return True

    def display_paginated_analytics(self, habits: List[tuple], page: int, items_per_page: int) -> None:
        """Display paginated analytics table with statistics"""
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        page_habits = habits[start_idx:end_idx]
        
        table = PrettyTable()
        table.field_names = [
            'Name',
            'Category',
            'Description',
            'Repeat',
            'Days Passed',
            'Success Rate',
            'Current Streak',
            'Reset Count',
            'Status'
        ]
        
        for habit in page_habits:
            days_passed = self.analytics.calculate_passed_days(habit[5])
            success_rate = self.analytics.calculate_success_rate(
                habit[5], habit[8], habit[11], habit[12]
            )
            
            table.add_row([
                habit[1],
                habit[2],
                habit[3][:30],
                habit[8],
                days_passed,
                success_rate,
                habit[11],
                habit[12],
                habit[7]
            ])
        
        print(f"\nHabits Analytics Overview (Page {page} - 15 entires per page):")
        print(table)

    def handle_analytics_options(self, habits: List[tuple]) -> Optional[List[tuple]]:
        """Handle analytics menu options"""
        action = questionary.select(
            "Analytics Options:",
            choices=[
                "Show All Habits",
                "Sort Habits",
                "Filter Habits",
                "Back to Main Menu"
            ],
            style=self.style
        ).ask()
        
        if action == "Back to Main Menu":
            return None
        elif action == "Sort Habits":
            return self.handle_sort_habits(habits)
        elif action == "Filter Habits":
            return self.handle_filter_habits(habits)
        return habits

    def get_sortable_fields(self) -> List[str]:
        """Return list of fields that can be sorted"""
        return [
            "Name",
            "Category",
            "Description",
            "Repeat",
            "Days Passed",
            "Success Rate",
            "Current Streak",
            "Reset Count",
            "Status"
        ]
    
    def handle_sort_habits(self, habits: List[tuple]) -> List[tuple]:
        """Handle habit sorting workflow"""
        sort_by = questionary.select(
            "Sort by:",
            choices=self.get_sortable_fields(),
            style=self.style
        ).ask()
        
        if sort_by:
            order = questionary.select(
                "Order:",
                choices=["Ascending", "Descending"],
                style=self.style
            ).ask()
            
            if order:
                return self.analytics.sort_habits(
                    habits,
                    sort_by.lower().replace(' ', '_'),
                    order == "Ascending"
                )
        
        return habits

    def get_filterable_fields(self) -> List[str]:
        """Return list of fields that can be filtered"""
        return [
            "Name",
            "Category", 
            "Description",
            "Repeat",
            "Status"
        ]

    def get_unique_field_values(self, habits: List[tuple], field: str) -> List[str]:
        #rename this function
        """Get unique values for selected field"""
        field_indices = {
            'Name': 1,
            'Category': 2,
            'Description': 3,
            'Repeat': 8,
            'Status': 7
        }
        
        index = field_indices[field] # rename the parameter
        return sorted(set(habit[index] for habit in habits))

    def show_filter_options(self, habits: List[tuple]) -> Tuple[str, str]:
        """Show filter field and value selection"""
        # Select field # rename field and choiches to a more descriptive name
        field = questionary.select(
            "Select field to filter by:",
            choices=self.get_filterable_fields(),
            style=self.style
        ).ask()
        
        if not field:
            return None, None
            
        # Get unique values for selected field
        values = self.get_unique_field_values(habits, field)
        values.append("Reset Filter")  # Add reset option
        
        # Select value
        value = questionary.select(
            f"Select {field.lower()} value:",
            choices=values,
            style=self.style
        ).ask()
        
        return field, value

    def handle_filter_habits(self, habits: List[tuple]) -> List[tuple]:
        """Handle habit filtering workflow"""
        field, value = self.show_filter_options(habits)
        
        if not field or not value:
            return habits
            
        if value == "Reset Filter":
            return self.get_habits_data()
        
        # Apply filter
        filtered_habits = self.analytics.filter_habits(habits, field.lower(), value)
        
        if not filtered_habits:
            print("\nNo habits match the filter criteria")
            return habits
            
        return filtered_habits

    def display_analytics_table(self, habits: List[tuple]) -> None:
        """Display analytics table with statistics"""
        table = PrettyTable()
        table.field_names = [
            'Name',
            'Category',
            'Description',
            'Repeat',
            'Days Passed',
            'Success Rate',
            'Current Streak',
            'Reset Count',
            'Status'
        ]
        
        for habit in habits:
            days_passed = self.analytics.calculate_passed_days(habit[5])
            success_rate = self.analytics.calculate_success_rate(
                habit[5], habit[8], habit[11], habit[12]
            )
            
            table.add_row([
                habit[1],
                habit[2],
                habit[3][:30],
                habit[8],
                days_passed,
                success_rate,
                habit[11],
                habit[12],
                habit[7]
            ])
        
        print("\nHabits Analytics Overview:")
        print(table)
        
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
                
            self.handle_habit_management(choice)
            
            if not questionary.confirm(
                "Return to Habit Management menu?",
                default=True,
                style=self.style
            ).ask():
                break

    def confirm_update(self, row_id: int, field: str, value: str) -> bool:
        """Get user confirmation for update"""
        return input("\nConfirm updating row {}'s {} to '{}'? (y/n): ".format(
            row_id, field, value)).lower() == 'y'

    # Action Methods
    
    def show_task_overview(self):
        """Handle task overview and interactions"""
        task_overview = TaskOverview()
        
        while True:
            self.clear_screen()
            self.show_navigation_hint()
            
            # Get current tasks
            pending_tasks, task_id_map = task_overview.get_pending_tasks()
            
            if not pending_tasks:
                print("\nNo pending tasks found")
                if questionary.confirm("Return to main menu?", default=True, style=self.style).ask():
                    break
                continue
            
            # Display current tasks
            self.display_task_table(task_overview.get_table_headers(), pending_tasks)
            
            # Task action menu
            action = questionary.select(
                "Choose action:",
                choices=[
                    "Mark tasks as done",
                    "Mark tasks as ignored",
                    "Pause habit",
                    "Back to main menu"
                ],
                style=self.style
            ).ask()
            
            if action == "Back to main menu":
                break
                
            # Select tasks
            choices = [
                {
                    "name": f"Row {task[0]}: {task[1]} - Task {task[2]} (Due: {task[4]})",
                    "value": task[0],
                    "checked": False
                }
                for task in pending_tasks
            ]
            
            selected_rows = questionary.checkbox(
                "Select tasks to update:",
                choices=choices,
                instruction="(Space to select, Enter to confirm)",
                style=self.style
            ).ask()

            if not selected_rows:
                print("\nNo tasks selected")
                continue
            
            # Map status
            status_map = {
                "Mark tasks as done": "done",
                "Mark tasks as ignored": "ignore",
                "Pause habit": "pause habit"
            }
            
            status = status_map.get(action)
            
            # Single confirmation
            if questionary.confirm(
                f"\nUpdate {len(selected_rows)} task(s) to '{status}'?",
                default=False,
                style=self.style
            ).ask():
                updated, failed = task_overview.process_task_updates(selected_rows, task_id_map, status)
                
                if updated:
                    print(f"\nSuccessfully updated {len(updated)} task(s)")
                if failed:
                    print(f"\nFailed to update {len(failed)} task(s)")
            
            if not questionary.confirm(
                "Continue with task overview?",
                default=True,
                style=self.style
            ).ask():
                break

    def handle_analytics(self, habits: List[tuple], action: str) -> None:
        """Handle analytics actions"""
        if action == "Show All Habits":
            self.display_analytics(habits)
        elif action == "Sort Habits":
            self.handle_analytics_sort(habits)
        elif action == "Filter Habits":
            self.handle_analytics_filter(habits)

    def handle_habit_management(self, action: str) -> None:
        """Handle habit management actions"""
        if action == "Show Current Habits":
            self.habit_management.display_habits_with_rows()
        elif action == "Create New Habit":
            self.create_new_habit()
        elif action == "Update Habit":
            self.update_habit_workflow()
        elif action == "Delete Habit":
            self.delete_habit()

    def show_current_values(self, habit: tuple, updates: dict):
        """Display current habit values and pending updates"""
        print("\nCurrent Values:")
        print("---------------")
        fields = {
            'Category': habit[2],
            'Description': habit[3],
            'Start Date': habit[5],
            'End Date': habit[6],
            'Importance': habit[7],
            'Repeat': habit[8]
        }
        
        for field, value in fields.items():
            new_value = updates.get(field.lower())
            if new_value:
                print(f"{field}: {value} -> {new_value} (pending)")
            else:
                print(f"{field}: {value}")

    def get_field_value(self, field: str, habit: tuple) -> Optional[str]:
        """Get new value for a field with appropriate validation"""
        if field in ["Importance", "Repeat"]:
            choices = {
                "Importance": ["High", "Low", "Paused"],
                "Repeat": ["Daily", "Weekly"]
            }
            return questionary.select(
                f"Select new {field.lower()}:",
                choices=choices[field],
                style=self.style
            ).ask()
        else:
            value = questionary.text(
                f"Enter new {field.lower()}:",
                style=self.style
            ).ask()
            
            if value:
                # Validate date format for date fields
                if field in ["Start Date", "End Date"]:
                    try:
                        datetime.strptime(value, '%Y-%m-%d')
                    except ValueError:
                        print("Invalid date format. Use YYYY-MM-DD")
                        return None
            return value

    def show_updates_summary(self, updates: dict):
        """Show summary of all pending updates"""
        print("\nPending Updates:")
        print("---------------")
        for field, value in updates.items():
            print(f"{field.title()}: {value}")

    def update_habit_workflow(self):
        """Handle the habit update workflow"""
        try:
            # Get current habits
            habit_id_map, habits = self.habit_management.display_habits_with_rows()
            
            if not habits:
                print("\nNo habits found")
                return

            # Single-select for habit
            row = questionary.select(
                "Select habit to update:",
                choices=[
                    f"Row {row}: {habit[1]} - {habit[3][:30]}"
                    for row, habit in zip(habit_id_map.keys(), habits)
                ],
                style=self.style
            ).ask()
            
            if not row:
                return
                
            # Extract row number
            row_num = int(row.split(':')[0].replace('Row ', ''))
            habit_id = habit_id_map[row_num]
            habit = next(h for h in habits if h[0] == habit_id)
            
            # Multi-select fields to update
            field_choices = [
                {
                    "name": field,
                    "value": field.lower(),
                    "checked": False
                }
                for field in [
                    "Category",
                    "Description", 
                    "Start Date",
                    "End Date",
                    "Importance",
                    "Repeat"
                ]
            ]
            
            selected_fields = questionary.checkbox(
                "Select fields to update:",
                choices=field_choices,
                style=self.style
            ).ask()
            
            if not selected_fields:
                print("\nNo fields selected")
                return
                
            # Get new values for selected fields
            updates = {}
            for field in selected_fields:
                new_value = self.get_field_value(field.title(), habit)
                if new_value is not None:
                    updates[field] = new_value
            
            if updates:
                self.show_updates_summary(updates)
                if questionary.confirm(
                    "Save these changes?",
                    default=False,
                    style=self.style
                ).ask():
                    if self.ui_handler.update_habit(habit_id, updates):
                        print("\nHabit updated successfully!")
                    else:
                        print("\nFailed to update habit")
            else:
                print("No valid updates provided")

        except Exception as e:
            print(f"Error updating habit: {e}")

    def display_current_habits(self):
        """Display current habits using HabitManagement"""
        self.clear_screen()
        self.show_navigation_hint()
        
        table, habit_id_map = self.habit_management.display_habits_with_rows()
        
        if not table:
            print("\nNo habits found")
            return
            
        print("\nHabits Overview:")
        print(table)
        
        if questionary.confirm(
            "\nView more details?",
            default=False,
            style=self.style
        ).ask():
            self.show_habit_details(habit_id_map)

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

    def show_habit_summary(self, answers: dict):
        """Display summary of habit data"""
        print("\nHabit Summary:")
        print("-------------")
        for key, value in answers.items():
            print(f"{key.replace('_', ' ').title()}: {value}")

    def delete_habit(self):
        """Delete habits with multi-select capability"""
        try:
            habits = self.db_controller.read_data('habit')
            if not habits:
                print("No habits found")
                return

            choices = [
                {
                    "name": f"{habit[1]} - {habit[3][:30]}{'...' if len(habit[3]) > 30 else ''}", 
                    "value": habit[0],
                    "checked": False
                } 
                for habit in habits
            ]

            self.clear_screen()
            self.show_navigation_hint()
            print("\nSelect habits to delete (space to select, enter to confirm):")
            
            selected_habits = questionary.checkbox(
                "Select habits:",
                choices=choices,
                style=self.style
            ).ask()

            if not selected_habits:
                return

            if questionary.confirm(
                f"\nDelete {len(selected_habits)} habit(s)?",
                default=False,
                style=self.style
            ).ask():
                for habit_id in selected_habits:
                    if self.ui_handler.delete_habit(habit_id):
                        print(f"Deleted habit {habit_id}")
                    else:
                        print(f"Failed to delete habit {habit_id}")

        except Exception as e:
            print(f"Error deleting habits: {e}")

    def show_help(self):
        """Display help information"""
        print("\nHelp documentation coming soon!")
        
def main():
    """Main entry point"""
    ui = HabitUI()
    ui.main_menu()

if __name__ == "__main__":
    main()