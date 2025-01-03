from datetime import datetime, timedelta
from typing import List, Dict, Optional
from database.operations import DatabaseController

class Analytics:
    """Analytics model with data access and calculations"""
    
    def __init__(self, db_controller=None):
        self.db_controller = db_controller or DatabaseController()

    @classmethod
    def calculate_passed_days(cls, start_date: str) -> int:
        """Calculate days passed since start date"""
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            today = datetime.now().date()
            return (today - start).days if start <= today else 0
        except Exception as e:
            print("Error calculating passed days: {}".format(e))
            return 0

    @classmethod
    def calculate_success_rate(cls, habit_id: int) -> str:
        """Calculate success rate based on completed task days"""
        try:
            db = DatabaseController()
            tasks = db.read_data('task', {'habit_id': habit_id})
            
            # Get habit data
            habits = db.read_data('habit', {'id': habit_id})
            habit = habits[0] if habits else None
            
            # Group by period (daily/weekly)
            if habit:
                # Need to pass cls as first argument since it's a classmethod
                grouped = cls._group_tasks_by_period(tasks, habit[8])  # habit[8] is repeat interval
                
                # Rest of the method...
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

    def _get_habit_data(self, habit_id: int, db: DatabaseController) -> Optional[tuple]:
        """Get habit data from database"""
        habits = db.read_data('habit', {'id': habit_id})
        return habits[0] if habits else None

    def _get_task_statistics(self, habit_id: int, repeat: str, db: DatabaseController) -> Dict:
        """Calculate task completion statistics"""
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

    @classmethod  # Add classmethod decorator
    def _group_tasks_by_period(cls, tasks: List[tuple], repeat: str) -> Dict:
        """Group tasks by day or week based on repeat interval"""
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

    def get_analytics_data(self) -> List[Dict]:
        """Get formatted analytics data"""
        db = DatabaseController()
        try:
            habits = db.read_data('habit')
            return [{
                'name': habit[1],
                'category': habit[2], 
                'description': habit[3],
                'repeat': habit[8],
                'days_passed': self.calculate_passed_days(habit[5]),
                'success_rate': self.calculate_success_rate(habit[0]),
                'current_streak': habit[11],
                'longest_streak': habit[13],
                'reset_count': habit[12],
                'importance': habit[7]
            } for habit in habits] if habits else []
        except Exception as e:
            print("Error getting analytics data: {}".format(e))
            return []
        
    def sort_analytics_data(self, data: List[Dict], sort_by: str, ascending: bool = True) -> List[Dict]:
        """Sort with identical logic as original"""
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
        """Filter analytics data"""
        try:
            return [
                item for item in data
                if str(value).lower() in str(item.get(filter_by, '')).lower()
            ]
        except Exception as e:
            print("Error filtering data: {}".format(e))
            return data