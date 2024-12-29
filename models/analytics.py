from datetime import datetime
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
    def calculate_success_rate(cls, start_date: str, repeat: str, 
                             streak: int, reset_count: int) -> str:
        """Calculate habit success rate"""
        try:
            days_passed = cls.calculate_passed_days(start_date)
            if days_passed == 0:
                return "N/A"

            possible_occurrences = days_passed
            if repeat == "Weekly":
                possible_occurrences = days_passed // 7

            if possible_occurrences > 0:
                success_rate = ((possible_occurrences - reset_count) / possible_occurrences) * 100
                return "{:.0f}%".format(max(0, min(100, success_rate)))
            return "0%"
        except Exception as e:
            print("Error calculating success rate: {}".format(e))
            return "N/A"

    def get_analytics_data(self) -> List[Dict]:
        """Get formatted analytics data"""
        db = DatabaseController()
        try:
            habits = db.read_data('habit')
            return [{
                'id': habit[0],
                'name': habit[1],
                'category': habit[2],
                'description': habit[3][:30],
                'repeat': habit[8],
                'start': habit[5],  # Keep key as 'start'
                'days_passed': self.calculate_passed_days(habit[5]),
                'success_rate': self.calculate_success_rate(
                    habit[5], habit[8], habit[11], habit[12]
                ),
                'current_streak': habit[11],
                'reset_count': habit[12],
                'status': habit[7]
            } for habit in habits] if habits else []
        except Exception as e:
            print(f"Error getting analytics data: {e}")
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