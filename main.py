from views.menu_ui import MainUI
from controllers.habit import HabitController
from controllers.task import TaskController
from controllers.analytics import AnalyticsController
from database.connector import DatabaseConnector
from database.operations import DatabaseController

def main():
    """Main entry point of the application"""
    # Initialize database system
    DatabaseConnector()
    DatabaseController()
    
    # Initialize controllers (no db dependencies)
    habit_controller = HabitController()
    task_controller = TaskController()
    analytics_controller = AnalyticsController()
    
    # Initialize and run UI
    ui = MainUI(habit_controller, task_controller, analytics_controller)
    ui.main_menu()

if __name__ == "__main__":
    main()

