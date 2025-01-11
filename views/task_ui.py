from typing import List, Dict, Tuple, Optional
import questionary
from prettytable import PrettyTable
from .core import BaseUI
from controllers.task import TaskController

class TaskUI(BaseUI):
    """Task management specific UI"""

    # Table configuration
    TABLE_HEADERS = [
        "Row",
        "Habit",
        "Task #", 
        "Description",
        "Due Date",
        "Status",
        "Completion Rate",
        "Streak"
    ]
    
    COLUMN_WIDTHS = {
        'Row': 4,
        'Habit': 20,
        'Task #': 6,
        'Description': 50,
        'Due Date': 12,
        'Status': 8,
        'Streak': 8,
        'Completion Rate': 12
    }
    
    # Default values
    DEFAULT_WIDTH = 15
    ITEMS_PER_PAGE = 15

    # Initialization
    def __init__(self, task_controller=None):
        super().__init__()
        self.task_controller = task_controller or TaskController()
        self.items_per_page = self.ITEMS_PER_PAGE

    # Core UI methods
    def show_task_overview(self) -> None:
        """
        Display an interactive overview of pending tasks with pagination functionality.
        This method shows pending tasks in a paginated format, allowing users to navigate
        through multiple pages of tasks. Users can move between pages and return to the
        previous menu.
        Returns:
            None
        Note:
            - The method runs in a loop until the user chooses to exit
            - Tasks are displayed according to the current page number
            - Navigation options depend on the total number of pages and current position
        """

        page = 1
        
        while True:
            # Create task overview table first
            tasks = self.task_controller.get_pending_tasks()
            self._display_current_page(tasks, page)
            total_pages = self._calculate_total_pages(tasks)
            
            # Show menu options
            action = self._get_page_action(tasks, total_pages, page)
            page = self._handle_page_action(action, tasks, page, total_pages)
            if page is None:
                break
 
    def _get_table_headers(self) -> List[str]:
        return [
            "Row",
            "Habit Name",
            "Task Number",
            "Description",
            "Due Date",
            "Status",
            "Completion Rate",
            "Streak"
        ]

    # Display Methods
    def _display_task_table(self, tasks: List[Dict], page: int) -> None:
        """Display paginated task table"""
        if not tasks:
            print("\nNo pending tasks found")
            return
                
        table = self._initialize_table()
        self._configure_columns(table)
        self._add_task_rows(table, tasks, page)
        self._display_table(table)

    def _display_table(self, table: PrettyTable) -> None:
        """
        Display the task overview table in the console.
        This method prints a formatted table showing task-related information to the console output.

        Args:
            table (PrettyTable): A PrettyTable instance containing the task data to be displayed.

        Returns:
            None
        """

        print("\nTask Overview:")
        print(table)

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

    def _add_task_rows(self, table: PrettyTable, tasks: List[Dict], page: int) -> None:
        """Add task rows to table with pagination"""
        start_idx = (page - 1) * self.items_per_page
        end_idx = start_idx + self.items_per_page
        page_tasks = tasks[start_idx:end_idx]
        
        for task in page_tasks:
            table.add_row([
                task["row"],
                task["habit_name"],
                task["task_number"],
                task["description"],
                task["due_date"],
                task["status"],
                task["streak"],
                task["completion_rate"]
            ])

    # Navigation Methods
    def _display_current_page(self, tasks: List[Dict], page: int) -> None:
        """Display current page of tasks"""
        self._clear_screen()
        self._show_navigation_hint()
        self._display_task_table(tasks, page)

    def _calculate_total_pages(self, tasks: List[Dict]) -> int:
        """Calculate total number of pages"""
        return (len(tasks) + self.items_per_page - 1) // self.items_per_page

    def _get_page_action(self, tasks: List[Dict], total_pages: int, page: int) -> str:
        """Get user action for current page"""
        choices = self._build_page_choices(page, total_pages)
        return questionary.select(
            "\nPage {}/{}".format(page, total_pages) if tasks else "\nChoose action:",
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
            self._clear_screen()
            return None
        elif action == "Next Page":
            return min(page + 1, total_pages)
        elif action == "Previous Page":
            return max(page - 1, 1)
        else:
            selected_rows = self.get_selected_tasks(tasks)
            if selected_rows:
                task_id_map = {task["row"]: task["id"] for task in tasks} # Map row index to task ID in the DB
                if self.process_task_update(selected_rows, task_id_map, action):
                    input("\nPress Enter to continue...")
                    self._clear_screen()
                    tasks = self.task_controller.get_pending_tasks()
            return page

    # Task Update Methods

    def get_selected_tasks(self, tasks: List[Dict]) -> Optional[List[int]]:
        """Get task selection using checkbox interface"""
        choices = [
            {
                "name": "Row {}: {} - Task {} (Due: {})".format(
                    task["row"],
                    task["habit_name"],
                    task["task_number"],
                    task["due_date"]
                ),
                "value": task["row"],
                "checked": False
            }
            for task in tasks
        ]
        
        selected = questionary.checkbox(
            "Select tasks to update:",
            choices=choices,
            instruction="(Space to select, Enter to confirm or CRTL + C to quit)",
            style=self.style
        ).ask()
        
        if not selected:
            print("\nNo tasks selected")
        return selected

    def process_task_update(self, selected_rows: List[int], task_id_map: Dict[int, int], action: str) -> bool:
        """
        Process the update of task status for selected tasks.
        This method handles the batch updating of task statuses, including special handling
        for 'ignore' and 'pause habit' statuses which may affect related tasks.
        Args:
            selected_rows (List[int]): List of row indices selected for update
            task_id_map (Dict[int, int]): Mapping of row indices to task IDs
            action (str): The action to perform, corresponding to a status in task_controller.status_map
        Returns:
            bool: True if all selected tasks were updated successfully, False otherwise
        """

        try:
            status = self.task_controller.status_map[action]
            
            if not questionary.confirm(
                "\nUpdate {} task(s) to '{}'?".format(len(selected_rows), status),
                default=False,
                style=self.style
            ).ask():
                return False
                
            success = True
            updated_count = 0
            
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
        """
        Handle the processing of tasks related to selected tasks based on a given status.

        This method checks for related pending tasks for each selected task and, if found,
        prompts the user to decide whether to include these related tasks in the operation.

        Parameters:
            selected_rows (List[int]): List of row indices initially selected by the user
            task_id_map (Dict[int, int]): Dictionary mapping row indices to task IDs
            status (str): The status to be applied to the tasks ('ignore' or 'pause')

        Returns:
            List[int]: Updated list of row indices including any additional related tasks
            the user chose to include

        """

        try:
            new_rows = selected_rows.copy()
            for row in selected_rows:
                task_id = task_id_map.get(row)
                if task_id:
                    related_rows = self.task_controller.get_related_pending_tasks(task_id, task_id_map)
                    if related_rows:
                        action_text = "ignore" if status == "ignore" else "pause"
                        if not questionary.confirm(
                            "\nFound other pending tasks for this habit. {} them as well?".format(action_text),
                            default=False,
                            style=self.style
                        ).ask():
                            continue
                        new_rows.extend([r for r in related_rows if r not in new_rows])
            return new_rows
        except Exception as e:
            print("Error handling related tasks: {}".format(e))
            return selected_rows
