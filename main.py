import os
import sys
import subprocess
from views.menu_ui import MainUI
from controllers.habit import HabitController
from controllers.task import TaskController
from controllers.analytics import AnalyticsController
from database.connector import DatabaseConnector
from database.operations import DatabaseController

def launch_new_terminal():
    """Attempt to launch application in new terminal window"""
    if os.environ.get('HABIT_TRACKER_RUNNING'):  # Check if already in new terminal
        return False
            
    try:
        script_path = os.path.abspath(__file__)
        if os.name == 'posix':  #  Works on Linux/Unix
            os.environ['HABIT_TRACKER_RUNNING'] = '1'  # Set environment flag
            terminal_commands = [
                ['gnome-terminal', '--', 'bash', '-c', f'HABIT_TRACKER_RUNNING=1 python3 {script_path}; exec bash'],
                ['xterm', '-hold', '-e', f'HABIT_TRACKER_RUNNING=1 python3 {script_path}'],
                ['konsole', '--hold', '--', 'python3', script_path]
            ]
            
            for cmd in terminal_commands:
                try:
                    subprocess.run(['which', cmd[0]], check=True, capture_output=True)
                    subprocess.Popen(cmd)
                    sys.exit(0)
                except subprocess.CalledProcessError:
                    continue
        return False
    except Exception as e:
        print(f"Could not launch new terminal: {e}")
        return False
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
    if len(sys.argv) == 1:  # Only try on first run
        if launch_new_terminal():
            return
    app = HabitTracker()
    app.run()

if __name__ == "__main__":
    main()