from typing import List, Dict
import questionary
from prettytable import PrettyTable
from task_overview import TaskOverview
from .core import BaseUI
from controllers.task import TaskController

class TaskUI(BaseUI):
    """Task management specific UI"""

    def __init__(self):
        super().__init__()
        self.task_controller = TaskController()
        self.items_per_page = 15

    def show_task_overview(self):
        """Handle task overview and interactions"""
        while True:
            self.clear_screen()
            self.show_navigation_hint()
            
            task_data = self.get_task_data()
            if not task_data:
                break
                
            pending_tasks, task_id_map = task_data
            self.display_task_table(self.task_overview.get_table_headers(), pending_tasks)
            
            action = self.show_task_menu()
            if action == "Back to main menu":
                break
                
            selected_rows = self.get_selected_tasks(pending_tasks)
            if not selected_rows:
                continue
                
            if self.process_task_update(selected_rows, task_id_map, action):
                if not self.handle_continue_prompt():
                    break
    def get_task_data(self):
        """Get task data with error handling"""
        try:
            pending_tasks = self.task_controller.get_pending_tasks()  # Use controller instead of direct DB access
            if not pending_tasks:
                print("\nNo pending tasks found")
                return None
            return pending_tasks
        except Exception as e:
            print(f"Error fetching tasks: {e}")
            return None

    def show_task_menu(self):
        """Display task action menu"""
        return questionary.select(
            "Choose action:",
            choices=[
                "Mark tasks as done",
                "Mark tasks as ignored",
                "Pause habit",
                "Back to main menu"
            ],
            style=self.style
        ).ask()

    def get_selected_tasks(self, pending_tasks):
        """Get user selected tasks"""
        choices = [
            {
                "name": "Row {}: {} - Task {} (Due: {})".format(
                    task[0],      # Row number
                    task[1],      # Habit name
                    task[2],      # Task number
                    task[4]       # Due date
                ),
                "value": task[0],
                "checked": False
            }
            for task in pending_tasks
        ]
        
        selected = questionary.checkbox(
            "Select tasks to update:",
            choices=choices,
            instruction="(Space to select, Enter to confirm)",
            style=self.style
        ).ask()
        
        if not selected:
            print("\nNo tasks selected")
        return selected

    def process_task_update(self, selected_rows, task_id_map, action):
        """Process task update with confirmation"""
        status_map = {
            "Mark tasks as done": "done",
            "Mark tasks as ignored": "ignore",
            "Pause habit": "pause habit"
        }
        
        status = status_map.get(action)
        update_msg = "\nUpdate {0} task(s) to '{1}'?".format(
            len(selected_rows), status
        )
        
        if questionary.confirm(update_msg, default=False, style=self.style).ask():
            updated, failed = self.task_overview.process_task_updates(
                selected_rows, task_id_map, status
            )
            
            if updated:
                print("\nSuccessfully updated {0} task(s)".format(len(updated)))
            if failed:
                print("\nFailed to update {0} task(s)".format(len(failed)))
            return True
        return False

    def handle_continue_prompt(self):
        """Handle continue confirmation"""
        return questionary.confirm(
            "Continue with task overview?",
            default=True,
            style=self.style
        ).ask()
    
    def display_task_table(self, headers: List[str], tasks: List[List]) -> None:
        """Display formatted task table"""
        table = PrettyTable()
        table.field_names = headers
        for task in tasks:
            table.add_row(task)
        print("\nPending Tasks:")
        print(table)

    