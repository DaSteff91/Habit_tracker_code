from .core import BaseUI
from .analytics_ui import AnalyticsUI
from .task_ui import TaskUI
from .habit_ui import HabitManagementUI
import questionary
import pydoc

class MainUI(BaseUI):
    """Main menu and program flow"""
    def __init__(self, habit_controller=None, task_controller=None, analytics_controller=None):
        super().__init__()
        self.habit_ui = HabitManagementUI(habit_controller)
        self.task_ui = TaskUI(task_controller)
        self.analytics_ui = AnalyticsUI(analytics_controller)

    def main_menu(self):
        """Main menu navigation"""
        while True:
            choice = self.get_menu_choice()
            if choice == "Exit":
                if self._confirm_exit():
                    break
            self.handle_menu_choice(choice)

    def get_menu_choice(self):
        """Get main menu selection"""
        self._clear_screen()
        self._show_navigation_hint() 
        return questionary.select(
            "What would you like to do?",
            choices=[
                "Task Overview",
                "Habit Management", 
                "Analytics",
                "Help",
                "Exit"
            ],
            style=self.style
        ).ask()

    def handle_menu_choice(self, choice):
        """Route menu selections to appropriate UI"""
        if choice == "Analytics":
            self.analytics_ui.show_analytics_menu()
        elif choice == "Task Overview":
            self.task_ui.show_task_overview()
        elif choice == "Habit Management":
            self.habit_ui.show_habit_management()
        elif choice == "Help":
            self._show_help()

    def _show_help(self):
        """Display help information"""
        self._clear_screen()
        try:
            with open('utils/help.txt', 'r') as help_file:
                help_text = help_file.read()
                pydoc.pager("\nHelp Documentation - press q to exit:\n=================\n\n" + help_text)
                
            self._clear_screen()
            
        except Exception as e:
            print("\nError loading help documentation: {}".format(e))

    def _confirm_exit(self):
        """Confirm program exit"""
        confirmed = questionary.confirm(
            "Do you really want to exit?",
            default=False,
            style=self.style
        ).ask()
        
        if confirmed:
            self._clear_screen()
            print("Thank you for using the Habit Tracker!")
        return confirmed

