from datetime import datetime, timedelta
from typing import List, Dict, Optional
from database.operations import DatabaseController

class Analytics:
    """Analytics model with data access and calculations"""
    
    def __init__(self, db_controller=None):
        self.db_controller = db_controller or DatabaseController()

    # Core Analytics Methods

    @classmethod
    def calculate_passed_days(cls, start: str, end: str) -> int:
        """
        Calculate the number of days between two dates, considering today as the maximum end date.
        Args:
            start (str): Start date in 'YYYY-MM-DD' format.
            end (str): End date in 'YYYY-MM-DD' format. If None, uses current date.
        Returns:
            int: Number of days between start and end date (or today, whichever is earlier).
                 Returns 0 if start date is after end date or in case of any errors.
        """

        try:
            start = datetime.strptime(start, '%Y-%m-%d').date()
            end = datetime.strptime(end, '%Y-%m-%d').date() if end else datetime.now().date()
            today = datetime.now().date()
            
            # Use earlier date between today and end date
            reference_date = min(today, end)
            
            return (reference_date - start).days if start <= reference_date else 0
        except Exception as e:
            print("Error calculating passed days: {}".format(e))
            return 0

    @classmethod
    def calculate_success_rate(cls, habit_id: int, db_controller: Optional[DatabaseController] = None) -> str:
        """
        Calculate the success rate for a specific habit.
        This method calculates what percentage of periods (daily/weekly) were successfully completed
        for a given habit. A period is considered successful if all tasks in that period are marked as 'done'.
        Args:
            habit_id (int): The ID of the habit to calculate success rate for
            db_controller (Optional[DatabaseController]): Database controller instance. If None, creates new instance
        Returns:
            str: Success rate as a percentage string (e.g. "75%"), or "N/A" if calculation fails or no data exists
        Note:
            - Success rate is rounded to nearest whole number
            - Rate is capped between 0% and 100%
            - Returns "N/A" if there are no periods to calculate from or in case of errors
        """

        try:
            db = db_controller or DatabaseController()
            tasks = db.read_data('task', {'habit_id': habit_id})
            
            # Get habit data
            habits = db.read_data('habit', {'id': habit_id})
            habit = habits[0] if habits else None
            
            # Group by period (daily/weekly)
            if habit:
                # Need to pass cls as first argument since it's a classmethod
                grouped = cls._group_tasks_by_period(tasks, habit[8])  # habit[8] is repeat interval
                
                successful_periods = sum(1 for tasks in grouped.values() 
                                    if all(t[6] == 'done' for t in tasks))
                total_periods = len(grouped)
                
                if total_periods == 0:
                    return "N/A"
                    
                success_rate = (successful_periods / total_periods) * 100
                return "{:.0f}%".format(max(0, min(100, success_rate)))
                
        except Exception as e:
            print("Error calculating success rate: {}".format(e))
            return "N/A"

    # Data Processing

    def get_analytics_data(self, db_controller: Optional[DatabaseController] = None) -> List[Dict]:
        """
        Retrieves analytics data for all habits from the database.
        This method fetches habit records and calculates various analytics metrics including
        days passed since creation, success rates, streaks and more.
        Args:
            db_controller (Optional[DatabaseController]): Database controller instance. 
                If None, a new instance will be created.
        Returns:
            List[Dict]: List of dictionaries containing analytics data for each habit with keys
        """
        
        db = db_controller or DatabaseController()
        try:
            habits = db.read_data('habit')
            return [{
                'name': habit[1],
                'category': habit[2], 
                'description': habit[3],
                'repeat': habit[8],
                'days_passed': self.calculate_passed_days(habit[5], habit[6]),
                'success_rate': self.calculate_success_rate(habit[0]),
                'current_streak': habit[11],
                'longest_streak': habit[13],
                'reset_count': habit[12],
                'importance': habit[7]
            } for habit in habits] if habits else []
        except Exception as e:
            print("Error getting analytics data: {}".format(e))
            return []

    def _get_task_statistics(self, habit_id: int, repeat: str, db_controller: Optional[DatabaseController] = None) -> Dict:
        """
        Calculate statistics for tasks associated with a specific habit.
        This method analyzes task completion rates by grouping tasks into periods (days or weeks)
        and determining how many periods were completely successful (all tasks done).
        Parameters:
            habit_id (int): The unique identifier of the habit to analyze
            repeat (str): The periodicity of the habit ('daily' or 'weekly')
            db_controller (Optional[DatabaseController]): Database controller instance. 
                If None, a new instance will be created.
        Returns:
            Dict: A dictionary containing:
                - 'successful_days': Number of periods where all tasks were completed
                - 'total_days': Total number of periods with tasks
        """

        db = db_controller or DatabaseController()
        tasks = db.read_data('task', {'habit_id': habit_id})
        if not tasks:
            return {'successful_days': 0, 'total_days': 0}
        
        # Group tasks by due_date or week
        grouped_tasks = self._group_tasks_by_period(tasks, repeat)
        
        # Count successful periods (all tasks done) vs total periods
        successful = sum(1 for tasks in grouped_tasks.values() 
                        if all(t[6] == 'done' for t in tasks))
        
        return {
            'successful_days': successful,
            'total_days': len(grouped_tasks)
        }

    # Filtering and Sorting

    def sort_analytics_data(self, data: List[Dict], sort_by: str, ascending: bool = True) -> List[Dict]:
        """
        Sort the analytics data based on a specified field.
        This method sorts a list of dictionaries containing habit analytics data based on the specified
        field and order. It handles different data types (strings, numbers, percentages) appropriately
        during sorting.
        Args:
            data (List[Dict]): A list of dictionaries containing habit analytics data.
            sort_by (str): The field to sort by. Valid values are:
                - 'name'
                - 'category'
                - 'description'
                - 'repeat'
                - 'days_passed'
                - 'success_rate'
                - 'current_streak'
                - 'reset_count'
                - 'status'
            ascending (bool, optional): Sort order. True for ascending, False for descending. 
                Defaults to True.
        Returns:
            List[Dict]: The sorted list of dictionaries.
        Note:
            - Success rate values are converted from percentage strings to floats for sorting
            - Numerical fields (current_streak, reset_count, days_passed) are converted to floats
            - Missing or None values are handled appropriately for each field type
        """

        field_mapping = {
            'name': 'name',
            'category': 'category',
            'description': 'description',
            'repeat': 'repeat',
            'days_passed': 'days_passed',
            'success_rate': 'success_rate',
            'current_streak': 'current_streak',
            'reset_count': 'reset_count',
            'status': 'status'
        }
        
        def sort_key(item):
            field = field_mapping.get(sort_by)
            if not field:
                return ''
            
            value = item.get(field)
            
            if sort_by == 'success_rate':
                return float(value.rstrip('%')) if value != 'N/A' else 0
            elif sort_by in ['current_streak', 'reset_count', 'days_passed']:
                return float(value if value is not None else -1)
            return str(value).lower()
            
        return sorted(data, key=sort_key, reverse=not ascending)

    def filter_analytics_data(self, data: List[Dict], filter_by: str, value: str) -> List[Dict]:
        """
        Filter analytics data based on a specified field and value.
        This method filters a list of dictionaries based on a case-insensitive partial match
        of the specified value against a specified field.
        Args:
            data (List[Dict]): List of dictionaries containing analytics data to filter
            filter_by (str): The dictionary key to filter on
            value (str): The value to filter for (case-insensitive partial match)
        Returns:
            List[Dict]: Filtered list of dictionaries where the specified field contains
            the filter value (case-insensitive). Returns original data if an error occurs.
        """
        
        try:
            return [
                item for item in data
                if str(value).lower() in str(item.get(filter_by, '')).lower()
            ]
        except Exception as e:
            print("Error filtering data: {}".format(e))
            return data

    # Helper Methods

    @classmethod
    def _group_tasks_by_period(cls, tasks: List[tuple], repeat: str) -> Dict:
        """Group tasks by period according to repeat parameter.
        Args:
            tasks (List[tuple]): List of task tuples containing task data where the due_date is at index 5
            repeat (str): String indicating grouping period ('Weekly' or other)
        Returns:
            Dict: Dictionary with dates as keys and lists of task tuples as values.
                For 'Weekly' repeat, keys are Monday dates of each week.
                For other repeats, keys are the original due dates.
        """
        
        grouped = {}
        for task in tasks:
            due_date = task[5]  # due_date field
            
            if repeat == 'Weekly':
                # Get week start date
                date = datetime.strptime(due_date, '%Y-%m-%d')
                key = (date - timedelta(days=date.weekday())).strftime('%Y-%m-%d')
            else:
                key = due_date
                
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(task)
            
        return grouped
   
    def _get_habit_data(self, habit_id: int, db_controller: Optional[DatabaseController] = None) -> Optional[tuple]:
        """Get habit data from database"""
        db = db_controller or DatabaseController()
        habits = db.read_data('habit', {'id': habit_id})
        return habits[0] if habits else None

