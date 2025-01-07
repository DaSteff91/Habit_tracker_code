from typing import List, Dict
from models.analytics import Analytics

class AnalyticsController:
    """Controller for analytics operations"""
    
    def __init__(self, analytics_model=None):
        self.analytics = analytics_model or Analytics()

    def get_analytics_data(self) -> List[Dict]:
        """Get formatted analytics data through model"""
        return self.analytics.get_analytics_data()

    def sort_data(self, data: List[Dict], sort_by: str, ascending: bool = True) -> List[Dict]:
        """Sort the analytics data based on specified criteria.
        
        Args:
            data (List[Dict]): List of dictionaries containing analytics data to be sorted
            sort_by (str): The key to sort the data by
            ascending (bool, optional): Sort order. True for ascending, False for descending. Defaults to True.

        Returns:
            List[Dict]: Sorted list of dictionaries containing analytics data
        """
        return self.analytics.sort_analytics_data(data, sort_by, ascending)

    def filter_data(self, data: List[Dict], filter_by: str, value: str) -> List[Dict]:
        """
        Filter analytics data based on specified criteria.

        Args:
            data (List[Dict]): List of dictionaries containing analytics data to filter
            filter_by (str): The field/key to filter the data on
            value (str): The value to filter for in the specified field

        Returns:
            List[Dict]: Filtered list of dictionaries matching the filter criteria
        """
        return self.analytics.filter_analytics_data(data, filter_by, value)

    def calculate_passed_days(self, start: str) -> int:
        """Calculate days passed through model"""
        return Analytics.calculate_passed_days(start)

    def calculate_success_rate(self, start: str, repeat: str, streak: int, reset_count: int) -> str:
        """
        Calculate success rate for a habit based on its parameters.

        Args:
            start (str): The starting date of the habit in format YYYY-MM-DD
            repeat (str): The repetition frequency of the habit (e.g., daily, weekly)
            streak (int): The current streak count of the habit
            reset_count (int): Number of times the habit has been reset

        Returns:
            str: Success rate as a percentage string (e.g., "85.5%")
        """
        return Analytics.calculate_success_rate(start, repeat, streak, reset_count)