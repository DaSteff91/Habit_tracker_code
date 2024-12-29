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
        self.status_map = {
            "Mark tasks as done": "done",
            "Mark tasks as ignored": "ignore",
            "Pause habit": "pause habit"
        }

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

    def show_task_overview(self) -> None:
        while True:
            self.clear_screen()
            self.show_navigation_hint()
            
            task_data = self.get_task_data()
            if not task_data:
                break
                
            pending_tasks, task_id_map = task_data
            self.display_task_table(self.get_table_headers(), pending_tasks)
            
            action = self.show_task_menu()
            if action == "Back to main menu":
                break
                
            selected_rows = self.get_selected_tasks(pending_tasks)
            if not selected_rows:
                continue
                
            if self.process_task_update(selected_rows, task_id_map, action):
                if not self.handle_continue_prompt():
                    break

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
        choices = list(self.status_map.keys()) + ["Back to main menu"]
        return questionary.select(
            "Choose action:",
            choices=choices
        ).ask()

    def get_selected_tasks(self, pending_tasks: List[Dict]) -> Optional[List[int]]:
        try:
            input_text = questionary.text(
                "Enter row numbers (comma-separated) or 'all':"
            ).ask()
            
            if not input_text:
                return None
                
            if input_text.lower() == 'all':
                return list(range(1, len(pending_tasks) + 1))
                
            return [int(x.strip()) for x in input_text.split(',')]
        except ValueError:
            print("Invalid input. Please enter numbers separated by commas.")
            return None

    def process_task_update(self, selected_rows: List[int], 
                          task_id_map: Dict[int, int], 
                          action: str) -> bool:
        try:
            status = self.status_map[action]
            for row in selected_rows:
                task_id = task_id_map.get(row)
                if task_id:
                    self.task_controller.update_task_status(task_id, status)
            return True
        except Exception as e:
            print("Error updating tasks: {}".format(e))
            return False

    def display_task_table(self, headers: List[str], tasks: List[Dict]) -> None:
        table = PrettyTable()
        table.field_names = headers
        
        for i, task in enumerate(tasks, 1):
            table.add_row([
                i,
                task['habit_name'],
                task['task_number'],
                task['description'][:30],
                task['due_date'],
                task['status'],
                "{}%".format(task['completion_rate']),
                task['streak']
            ])
            
        print(table)

    def handle_continue_prompt(self) -> bool:
        return questionary.confirm("Continue managing tasks?").ask()

    def show_navigation_hint(self) -> None:
        print("\nTask Management")
        print("==============")
        print("Select tasks by row number (comma-separated) or 'all'")
        print("Enter 'q' to return to main menu\n")