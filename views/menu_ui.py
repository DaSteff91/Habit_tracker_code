from .core import BaseUI
from .analytics_ui import AnalyticsUI
from .task_ui import TaskUI
from .habit_ui import HabitManagementUI
import questionary

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
                if self.confirm_exit():
                    break
            self.handle_menu_choice(choice)

    def get_menu_choice(self):
        """Get main menu selection"""
        self.clear_screen()
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

    def handle_menu_choice(self, choice):
        """Route menu selections to appropriate UI"""
        if choice == "Analytics":
            self.analytics_ui.show_analytics_menu()
        elif choice == "Task Overview":
            self.task_ui.show_task_overview()
        elif choice == "Habit Management":
            self.habit_ui.show_habit_management()
        elif choice == "Help":
            self.show_help()

    def show_help(self):
        """Display help information"""
        self.clear_screen()
        self.show_navigation_hint()
        
        try:
            with open('utils/help.txt', 'r') as help_file:
                help_text = help_file.read()
                print("\nHelp Documentation:")
                print("=================")
                print(help_text)
        except Exception as e:
            print("\nError loading help documentation: {}".format(e))
        
        input("\nPress Enter to return to main menu...")
        self.clear_screen()

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

