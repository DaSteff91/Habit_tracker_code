from .core import BaseUI
from .analytics_ui import AnalyticsUI
from .task_ui import TaskUI
from .habit_ui import HabitManagementUI
import questionary

class MainUI(BaseUI):
    """Main menu and program flow"""
    def __init__(self):
        super().__init__()
        self.analytics_ui = AnalyticsUI()
        self.task_ui = TaskUI()
        self.habit_ui = HabitManagementUI()

    def main_menu(self):
        """Main menu navigation"""
        while True:
            choice = self.get_menu_choice()
            if choice == "Exit":
                if self.confirm_exit():
                    break
            self.handle_menu_choice(choice)

    def handle_menu_choice(self, choice):
        """Route menu selections to appropriate UI"""
        if choice == "Analytics":
            self.analytics_ui.show_analytics_menu()
        elif choice == "Task Overview":
            self.task_ui.show_task_overview()
        elif choice == "Habit Management":
            self.habit_ui.show_habit_management()

    def get_menu_choice(self):
        """Get main menu selection"""
        self.clear_screen()  # Add if not present
        self.show_navigation_hint() 
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

    def confirm_exit(self):
        """Confirm program exit"""
        confirmed = questionary.confirm(
            "Do you really want to exit?",
            default=False,
            style=self.style
        ).ask()
        
        if confirmed:
            self.clear_screen()
            print("Thank you for using the Habit Tracker!")
        return confirmed

    def show_help(self):
        """Display help information"""
        self.clear_screen()
        self.show_navigation_hint()
        print("\nHelp documentation coming soon!")