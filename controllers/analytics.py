from typing import List, Dict
from models.analytics import Analytics

class AnalyticsController:
    """Controller for analytics operations"""
    
    def __init__(self, analytics_model=None):
        self.analytics = analytics_model or Analytics()

    def get_analytics_data(self) -> List[Dict]:
        """Get formatted analytics data through model"""
        return self.analytics.get_analytics_data()

    def sort_data(self, data: List[Dict], sort_by: str, 
                 ascending: bool = True) -> List[Dict]:
        """Sort analytics data through model"""
        return self.analytics.sort_analytics_data(data, sort_by, ascending)

    def filter_data(self, data: List[Dict], filter_by: str, 
                   value: str) -> List[Dict]:
        """Filter analytics data through model"""
        return self.analytics.filter_analytics_data(data, filter_by, value)

    def calculate_passed_days(self, start_date: str) -> int:
        """Calculate days passed through model"""
        return Analytics.calculate_passed_days(start_date)

    def calculate_success_rate(self, start_date: str, repeat: str,
                             streak: int, reset_count: int) -> str:
        """Calculate success rate through model"""
        return Analytics.calculate_success_rate(start_date, repeat, 
                                             streak, reset_count)