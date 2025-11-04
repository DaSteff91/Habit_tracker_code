import os
import sys
import subprocess
from views.menu_ui import MainUI
from controllers.habit import HabitController
from controllers.task import TaskController
from controllers.analytics import AnalyticsController
from database.connector import DatabaseConnector
from database.operations import DatabaseController
import shlex

NEW_TERMINAL_FLAG = "--new-terminal"


def launch_new_terminal():
    """
    Launch a new terminal window and run the current script in it.
    This function attempts to launch a new terminal window and run the current script,
    ensuring that multiple instances are not started simultaneously by using an environment variable.
    On Linux/Unix systems, it tries different terminal emulators (gnome-terminal, xterm, konsole)
    in sequence until one succeeds. On Windows, it uses the default command prompt (cmd).
    Returns:
        bool: True if the new terminal was successfully launched, False otherwise.
            Returns False if:
            - The script is already running (HABIT_TRACKER_RUNNING is set)
            - No suitable terminal emulator is found (Linux/Unix)
            - The subprocess creation fails
            - Any other unexpected error occurs
    """
    if os.environ.get("HABIT_TRACKER_RUNNING"):
        return False

    try:
        script_path = os.path.abspath(__file__)
        if os.name == "posix":
            return launch_unix_terminal(script_path)
        elif os.name == "nt":
            return launch_windows_terminal(script_path)
        return False
    except Exception:
        return False


def launch_unix_terminal(script_path: str) -> bool:
    """
    Launch the app in a new terminal on Linux/*nix.
    Uses the exact flag combo that worked in your manual test for Konsole,
    and sensible equivalents for other terminals.
    """
    env = os.environ.copy()
    env["HABIT_TRACKER_RUNNING"] = "1"  # prevent relaunch loops

    py = shlex.quote(sys.executable)  # current Python
    sp = shlex.quote(script_path)  # this script
    cmd_str = f"HABIT_TRACKER_RUNNING=1 {py} {sp}"

    # Try Konsole first (your default on Manjaro), then others
    candidates = [
        ["konsole", "-e", "bash", "-lc", cmd_str],  # Konsole
        ["gnome-terminal", "--", "bash", "-lc", cmd_str],  # GNOME Terminal
        ["kitty", "bash", "-lc", cmd_str],  # kitty
        ["alacritty", "-e", "bash", "-lc", cmd_str],  # Alacritty
        ["xterm", "-e", cmd_str],  # xterm
    ]

    cwd = os.path.dirname(os.path.abspath(script_path)) or None

    for cmd in candidates:
        try:
            subprocess.Popen(
                cmd,
                env=env,
                cwd=cwd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            return True
        except FileNotFoundError:
            continue
        except Exception:
            continue

    return False


def launch_windows_terminal(script_path: str) -> bool:
    """Launch terminal on Windows systems"""
    try:
        subprocess.Popen(
            [
                "start",
                "cmd",
                "/c",
                "set HABIT_TRACKER_RUNNING=1 && python {} && exit".format(script_path),
            ],
            shell=True,
        )
        return True
    except Exception:
        return False


def cleanup_on_exit():
    """
    Cleans up environment variables when the application exits.

    This function removes the 'HABIT_TRACKER_RUNNING' environment variable
    if it exists. The removal is performed within a try-except block to
    handle cases where the variable might not exist.

    Returns:
        None
    """

    try:
        if os.environ.get("HABIT_TRACKER_RUNNING"):
            del os.environ["HABIT_TRACKER_RUNNING"]
    except Exception:
        pass


class HabitTracker:
    """HabitTracker class manages the habit tracking application.
    This class serves as the main application controller, initializing and managing all components
    including database connections, controllers, and user interface.
    Attributes:
        db_connector (DatabaseConnector): Manages database connections and table creation
        db_controller (DatabaseController): Handles database operations
        habit_controller (HabitController): Manages habit-related operations
        task_controller (TaskController): Manages task-related operations
        analytics_controller (AnalyticsController): Handles analytics and reporting
        ui (MainUI): Manages the user interface
    Args:
        db_name (str): Name of the database file, defaults to "main.db"
    """

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
                self.habit_controller, self.task_controller, self.analytics_controller
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

    def __str__(self):
        return "Habit Tracker Application"

    def __repr__(self):
        return "HabitTracker(db_name='{}')".format(self.db_connector.db_name)


def main():
    """Application entry point"""
    try:
        if NEW_TERMINAL_FLAG in sys.argv:
            if launch_new_terminal():
                return

        sys.argv = [arg for arg in sys.argv if arg != NEW_TERMINAL_FLAG]

        app = HabitTracker()
        app.run()
    finally:
        cleanup_on_exit()


if __name__ == "__main__":
    main()
