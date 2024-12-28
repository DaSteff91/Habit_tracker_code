from prettytable import PrettyTable
from database.operations import DatabaseController
from ui_db_handler import UserInputHandler
from datetime import datetime
from typing import List, Tuple, Dict, Optional

class TaskOverview:
    def __init__(self):
        self.db_controller = DatabaseController()
        self.ui_handler = UserInputHandler()
        self.habit_headers = self.db_controller.get_table_headers('habit')
        self.task_headers = self.db_controller.get_table_headers('task')
    
    def get_table_headers(self) -> List[str]:
        """Return headers for display table"""
        return [
            'Row',
            self.habit_headers[1],     # habit name
            self.task_headers[2],      # task_number
            self.task_headers[3],      # task_description
            self.task_headers[5],      # due_date
            self.task_headers[6],      # status
            'completion_rate',         # success rate
            'streak'                   # streak
        ]
    
    def calculate_completion_rates(self, tasks: List[Tuple]) -> Dict[Tuple[int, str], Dict[str, int]]:
        """Calculate completion rates for habits grouped by due date"""
        habit_tasks = {}
        for task in tasks:
            habit_id = task[1]
            due_date = task[5]
            task_key = (habit_id, due_date)
            
            if task_key not in habit_tasks:
                habit_tasks[task_key] = {'total': 0, 'done': 0}
            habit_tasks[task_key]['total'] += 1
            if task[6] == 'done':
                habit_tasks[task_key]['done'] += 1
        return habit_tasks

    def get_pending_tasks(self) -> Tuple[List[List], Dict[int, int]]:
        """Get pending tasks and their mapping"""
        today = datetime.now().strftime('%Y-%m-%d')
        habits = self.db_controller.read_data('habit')
        tasks = self.db_controller.read_data('task')
        
        habit_names = {habit[0]: habit[1] for habit in habits}
        habit_importance = {habit[0]: habit[7] for habit in habits}
        habit_streaks = {habit[0]: habit[11] for habit in habits}
        habit_tasks = self.calculate_completion_rates(tasks)
        
        pending_tasks = []
        task_id_map = {}
        row_number = 1
        
        for task in tasks:
            habit_id = task[1]
            due_date = task[5]
            task_key = (habit_id, due_date)
            
            if (habit_importance.get(habit_id) == 'Paused' or
                task[6] != 'pending' or
                task[5] > today):
                continue
                
            if task_key in habit_tasks:
                total = habit_tasks[task_key]['total']
                done = habit_tasks[task_key]['done']
                completion_rate = "{}%".format(int((done/total)*100)) if total > 1 else ""
                
                task_id_map[row_number] = task[0]
                pending_tasks.append([
                    row_number,
                    habit_names[habit_id],
                    task[2],
                    task[3],
                    task[5],
                    task[6],
                    completion_rate,
                    habit_streaks.get(habit_id, 0)
                ])
                row_number += 1
                
        return pending_tasks, task_id_map

    def find_related_tasks(self, task_id: int, task_id_map: Dict[int, int]) -> List[int]:
        """Find tasks with same habit_id and due_date"""
        tasks = self.db_controller.read_data('task')
        original_task = next(task for task in tasks if task[0] == task_id)
        habit_id = original_task[1]
        due_date = original_task[5]
        
        related_rows = []
        for row_num, db_task_id in task_id_map.items():
            task = next(task for task in tasks if task[0] == db_task_id)
            if (task[1] == habit_id and 
                task[5] == due_date and 
                task[0] != task_id):
                related_rows.append(row_num)
        return related_rows

    def process_task_updates(self, row_ids: List[int], task_id_map: Dict[int, int], status: str) -> Tuple[List[int], List[int]]:
        """Process task updates and handle streaks"""
        updated = []
        failed = []
        tasks_by_habit = {}
        
        for row_id in row_ids:
            task_id = task_id_map[row_id]
            if self.ui_handler.update_task_status(task_id, status):
                updated.append(row_id)
                task_data = self.db_controller.read_data('task', {'id': task_id})[0]
                habit_id = task_data[1]
                due_date = task_data[5]
                
                if habit_id not in tasks_by_habit:
                    tasks_by_habit[habit_id] = set()
                tasks_by_habit[habit_id].add(due_date)
            else:
                failed.append(row_id)

        if status == 'done':
            self._handle_streak_updates(tasks_by_habit)
            
        self._create_next_tasks(tasks_by_habit)
        return updated, failed

    def _handle_streak_updates(self, tasks_by_habit: Dict[int, set]) -> None:
        """Update streaks for completed tasks"""
        tasks = self.db_controller.read_data('task')
        for habit_id, due_dates in tasks_by_habit.items():
            for due_date in due_dates:
                all_date_tasks = [t for t in tasks if t[1] == habit_id and t[5] == due_date]
                if all(t[6] == 'done' for t in all_date_tasks):
                    self.ui_handler.increment_streak(habit_id)
                    break

    def _create_next_tasks(self, tasks_by_habit: Dict[int, set]) -> None:
        """Create next tasks when all current tasks are handled"""
        for habit_id, due_dates in tasks_by_habit.items():
            for due_date in due_dates:
                habit_tasks = self.ui_handler.get_tasks_for_habit(habit_id, due_date)
                if habit_tasks:
                    all_done, all_handled = self.ui_handler.check_task_completion_status(habit_tasks)
                    if all_handled:
                        self.ui_handler.create_next_tasks(habit_id, due_date, habit_tasks)