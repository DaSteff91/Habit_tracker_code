from typing import List, Dict, Tuple, Optional
import questionary
from prettytable import PrettyTable
from .core import BaseUI
from controllers.task import TaskController

class TaskUI(BaseUI):
    """Task management specific UI"""
    def __init__(self, task_controller=None):
        super().__init__()
        self.task_controller = task_controller or TaskController()
        self.items_per_page = 15

    def get_table_headers(self) -> List[str]:
        return [
            'Row',
            'Habit Name',
            'Task Number',
            'Description',
            'Due Date',
            'Status',
            'Completion Rate',
            'Streak'
        ]

    def show_task_overview(self):
        """Main task overview coordinator"""
        while True:          
            self.show_navigation_hint()
            
            task_data = self.get_task_data()
            if not task_data:
                print("\nNo pending tasks found")
                if questionary.confirm(
                    "Return to main menu?",
                    default=True,
                    style=self.style
                ).ask():
                    break
                continue
                
            pending_tasks, task_id_map = task_data
            # Display table once
            self.display_task_table(
                self.get_table_headers(),
                pending_tasks
            )
            
            # Show menu once per loop
            if not self.handle_task_actions(pending_tasks, task_id_map):
                break

    def handle_task_actions(self, pending_tasks: List[Dict], task_id_map: Dict[int, int]) -> bool:
        """Handle task action selection and processing"""
        action = self.show_task_menu()
        if action == "Back to main menu":
            return False

        # Get task selection
        selected_rows = self.get_selected_tasks(pending_tasks)
        if not selected_rows:
            return True  # Stay in menu if no selection
            
        # Process update
        if self.process_task_update(selected_rows, task_id_map, action):
            return self.handle_continue_prompt()
            
        return True  # Stay in menu by default

    def get_task_data(self) -> Optional[Tuple[List[Dict], Dict]]:
        try:
            pending_tasks = self.task_controller.get_pending_tasks()
            if not pending_tasks:
                print("\nNo pending tasks found")
                return None
            
            task_id_map = {i+1: task['id'] for i, task in enumerate(pending_tasks)}
            return pending_tasks, task_id_map
        except Exception as e:
            print("Error fetching tasks: {}".format(e))
            return None

    def show_task_menu(self) -> str:
        """Show task action menu"""
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

    def get_selected_tasks(self, pending_tasks: List[Dict]) -> Optional[List[int]]:
        """Get task selection using checkbox interface"""
        choices = [
            {
                "name": "Row {}: {} - Task {} (Due: {})".format(
                    idx + 1,
                    task['habit_name'],
                    task['task_number'], 
                    task['due_date']
                ),
                "value": idx + 1,
                "checked": False
            }
            for idx, task in enumerate(pending_tasks)
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

    def process_task_update(self, selected_rows: List[int], task_id_map: Dict[int, int], action: str) -> bool:
        """Process task updates"""
        try:
            status = self.task_controller.status_map[action]
            success = True
            updated_count = 0
            
            for row in selected_rows:
                task_id = task_id_map.get(row)
                if task_id:
                    if self.task_controller.update_task_status(task_id, status):
                        updated_count += 1
                    else:
                        success = False
            
            # Single summary message
            if updated_count > 0:
                print("\nSuccessfully updated {} task(s)".format(updated_count))
                
            return success
        except Exception as e:
            print("Error updating tasks: {}".format(e))
            return False

    def display_task_table(self, headers: List[str], tasks: List[Dict]) -> None:
        """Display formatted task table"""
        if not tasks:
            print("\nNo pending tasks found")
            return
            
        table = PrettyTable()
        table.field_names = headers
        
        for i, task in enumerate(tasks, 1):
            table.add_row([
                i,  # Row number
                task['habit_name'],
                task['task_number'],
                task['description'],
                task['due_date'],
                task['status'],
                task['completion_rate'],
                task['streak']
            ])
            
        print("\nPending Tasks:")
        print(table)

    def handle_continue_prompt(self) -> bool:
        return questionary.confirm("Continue managing tasks?").ask()
