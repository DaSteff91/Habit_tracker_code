from database.operations import DatabaseController
from typing import List, Tuple, Optional

class AnalyticsManagement:
    """Analytics management class"""
    def __init__(self):
        self.db_controller = DatabaseController()
        
    def get_habits_data(self) -> Optional[List[tuple]]:
        """Get habits data for analytics"""
        return self.db_controller.read_data('habit')