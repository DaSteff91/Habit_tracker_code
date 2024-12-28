from datetime import datetime
from typing import List, Tuple, Dict
from database.operations import DatabaseController

class AnalyticsController:
    """Controller for analytics operations"""
    
    def __init__(self, db_controller=None):
        self.db_controller = db_controller or DatabaseController()

    def sort_habits(self, habits: List[tuple], sort_by: str, ascending: bool = True) -> List[tuple]:
        """Sort habits by specified field"""
        field_indices = {
            'name': 1,
            'category': 2,
            'description': 3,
            'repeat': 8,
            'days_passed': 5,
            'success_rate': None,
            'current_streak': 11,
            'reset_count': 12,
            'status': 7
        }
        
        def sort_key(habit):
            try:
                if sort_by == 'days_passed':
                    return self.calculate_passed_days(habit[5])
                elif sort_by == 'success_rate':
                    rate = self.calculate_success_rate(
                        habit[5],    # start_date
                        habit[8],    # repeat
                        habit[11],   # streak
                        habit[12]    # reset_count
                    )
                    return float(rate.rstrip('%') if rate != 'N/A' else 0)
                elif sort_by in ['current_streak', 'reset_count']:
                    value = habit[field_indices[sort_by]]
                    return float(value if value is not None else -1)
                else:
                    return str(habit[field_indices[sort_by]]).lower()
            except Exception as e:
                print(f"Error in sort_key: {e}")
                return ""
        
        return sorted(habits, key=sort_key, reverse=not ascending)

    def filter_habits(self, habits: List[tuple], filter_by: str, value: str) -> List[tuple]:
        """Filter habits based on criteria"""
        field_indices = {
            'name': 1,
            'category': 2,
            'description': 3,
            'repeat': 8,
            'status': 7
        }
        
        if filter_by not in field_indices:
            return habits
            
        index = field_indices[filter_by]
        return [
            habit for habit in habits 
            if str(value).lower() in str(habit[index]).lower()
        ]

    def calculate_passed_days(self, start_date: str) -> int:
        """Calculate days passed since habit start"""
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            today = datetime.now().date()
            if start > today:
                return 0
            return (today - start).days
        except Exception as e:
            print("Error calculating passed days: {}".format(e))
            return 0

    def calculate_success_rate(self, start_date: str, repeat: str, streak: int, reset_count: int) -> str:
        """Calculate habit success rate"""
        try:
            reset_count = reset_count if reset_count is not None else 0
            streak = streak if streak is not None else 0
            
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            today = datetime.now().date()
            
            if start > today:
                return "N/A"
                
            days_passed = (today - start).days + 1
            
            if repeat == 'Daily':
                possible_occurrences = days_passed
            elif repeat == 'Weekly':
                possible_occurrences = days_passed // 7
                if days_passed % 7 > 0:
                    possible_occurrences += 1
            else:
                return "N/A"
                
            if possible_occurrences > 0:
                success_rate = ((possible_occurrences - reset_count) / possible_occurrences) * 100
                return "{:.0f}%".format(max(0, min(100, success_rate)))
                
            return "0%"
            
        except Exception as e:
            print("Error calculating success rate: {}".format(e))
            return "N/A"

    def get_analytics_data(self) -> List[Dict]:
        """Get formatted analytics data"""
        habits = self.db_controller.read_data('habit')
        if not habits:
            return []
            
        analytics_data = []
        for habit in habits:
            analytics_data.append({
                'name': habit[1],
                'category': habit[2],
                'description': habit[3][:30],
                'repeat': habit[8],
                'days_passed': self.calculate_passed_days(habit[5]),
                'success_rate': self.calculate_success_rate(
                    habit[5], habit[8], habit[11], habit[12]
                ),
                'current_streak': habit[11],
                'reset_count': habit[12],
                'status': habit[7]
            })
            
        return analytics_data