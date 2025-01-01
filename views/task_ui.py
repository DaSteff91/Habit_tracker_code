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

    def show_task_overview(self) -> None:
        """Main task overview controller"""
        page = 1  # Initialize page counter
        tasks = self.task_controller.get_pending_tasks()
        
        while True:
            self._display_current_page(tasks, page)
            total_pages = self._calculate_total_pages(tasks)
            action = self._get_page_action(tasks, total_pages, page)
            
            # Update page variable based on action
            page = self._handle_page_action(action, tasks, page, total_pages)
            if page is None:  # Use None as exit signal
                break

    def _display_current_page(self, tasks: List[Dict], page: int) -> None:
        """Display current page of tasks"""
        self.display_task_table(self.get_table_headers(), tasks, page)

    def _calculate_total_pages(self, tasks: List[Dict]) -> int:
        """Calculate total number of pages"""
        return (len(tasks) + self.items_per_page - 1) // self.items_per_page

    def _get_page_action(self, tasks: List[Dict], total_pages: int, page: int) -> str:
        """Get user action for current page"""
        choices = self._build_page_choices(page, total_pages)  # Pass both arguments
        return questionary.select(
            f"\nPage {page}/{total_pages}" if tasks else "\nChoose action:",
            choices=choices,
            style=self.style
        ).ask()

    def _build_page_choices(self, page: int, total_pages: int) -> List[str]:
        """Build choices list including pagination"""
        choices = ["Mark tasks as done", "Mark tasks as ignored", "Pause habit"]
        if page > 1:
            choices.append("Previous Page")
        if page < total_pages:
            choices.append("Next Page")
        choices.append("Back to Main Menu")
        return choices
    
    def _handle_page_action(self, action: str, tasks: List[Dict], page: int, total_pages: int) -> Optional[int]:
        """Handle page action selection and return new page number"""
        if action == "Back to Main Menu":
            return None
        elif action == "Next Page":
            return min(page + 1, total_pages)
        elif action == "Previous Page":
            return max(page - 1, 1)
        else:
            selected_rows = self.get_selected_tasks(tasks)  # Direct call
            if selected_rows:
                task_id_map = {task['row']: task['id'] for task in tasks}
                if self.process_task_update(selected_rows, task_id_map, action):
                    tasks = self.task_controller.get_pending_tasks()
            return page

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
            
            # Add confirmation prompt
            if not questionary.confirm(
                "\nUpdate {} task(s) to '{}'?".format(len(selected_rows), status),
                default=False,
                style=self.style
            ).ask():
                return False
                
            success = True
            updated_count = 0
            
            # Handle both ignore and pause
            if status in ["ignore", "pause habit"]:
                selected_rows = self._handle_related_tasks(selected_rows, task_id_map, status)
                
            for row in selected_rows:
                task_id = task_id_map.get(row)
                if task_id and self.task_controller.update_task_status(task_id, status):
                    updated_count += 1
                else:
                    success = False
            
            if updated_count > 0:
                print("\nSuccessfully updated {} task(s)!".format(updated_count))
                
            return success
        except Exception as e:
            print("Error updating tasks: {}".format(e))
            return False
        
    def _handle_related_tasks(self, selected_rows: List[int], task_id_map: Dict[int, int], status: str) -> List[int]:
        """Handle related tasks for both ignore and pause"""
        try:
            new_rows = selected_rows.copy()
            for row in selected_rows:
                task_id = task_id_map.get(row)
                if task_id:
                    related_rows = self.task_controller.get_related_pending_tasks(task_id, task_id_map)
                    if related_rows:
                        action_text = "ignore" if status == "ignore" else "pause"
                        if questionary.confirm(
                            "\nFound other pending tasks for this habit. {} them as well?".format(action_text),
                            default=False,
                            style=self.style
                        ).ask():
                            new_rows.extend([r for r in related_rows if r not in new_rows])
            return new_rows
        except Exception as e:
            print("Error handling related tasks: {}".format(e))
            return selected_rows

    def display_task_table(self, headers: List[str], tasks: List[Dict], page: int) -> None:
        """Display paginated task table"""
        if not tasks:
            print("\nNo pending tasks found")
            return
            
        start_idx = (page - 1) * self.items_per_page
        end_idx = start_idx + self.items_per_page
        page_tasks = tasks[start_idx:end_idx]
        
        table = PrettyTable()
        table.field_names = headers
        
        for task in page_tasks:
            table.add_row([
                task['row'],
                task['habit_name'],
                task['task_number'],
                task['description'],
                task['due_date'],
                task['status'],
                task['completion_rate'],
                task['streak']
            ])
            
        print("\nTask Overview:")
        print(table)

    def handle_continue_prompt(self) -> bool:
        return questionary.confirm("Continue managing tasks?").ask()
