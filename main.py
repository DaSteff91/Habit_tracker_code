from views import MainUI
from database.operations import DatabaseController
from ui_db_handler import UserInputHandler

def main():
    """Main entry point of the application"""
    ui = MainUI()
    ui.main_menu()

if __name__ == "__main__":
    main()