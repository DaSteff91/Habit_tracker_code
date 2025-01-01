from os import sys
from views.menu_ui import MainUI
from controllers.habit import HabitController
from controllers.task import TaskController
from controllers.analytics import AnalyticsController
from database.connector import DatabaseConnector
from database.operations import DatabaseController

class HabitTracker:
    """Main application class"""
    def __init__(self, db_name: str = "main.db"):
        """Initialize application components"""
        try:
            # Database initialization with verification
            self.db_connector = DatabaseConnector(db_name)
            if not self.db_connector.connection:
                raise Exception("Failed to establish database connection")

            # Create tables only if connection successful
            self.db_connector.create_tables()
            self.db_controller = DatabaseController(db_name)
            
            # Initialize controllers
            self.habit_controller = HabitController()
            self.task_controller = TaskController()
            self.analytics_controller = AnalyticsController()
            
            # Initialize UI
            self.ui = MainUI(
                self.habit_controller,
                self.task_controller,
                self.analytics_controller
            )
        except Exception as e:
            print("Error initializing application: {}".format(e))
            sys.exit(1)

    def run(self):
        """Run the application"""
        try:
            self.ui.main_menu()
        except Exception as e:
            print("Runtime error: {}".format(e))
            sys.exit(1)

def main():
    """Application entry point"""
    app = HabitTracker()
    app.run()

if __name__ == "__main__":
    main()