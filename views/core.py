import os
from typing import List, Dict, Optional
import questionary
from questionary import Style

class BaseUI:
    """Base UI class with shared functionality"""
    def __init__(self):
        self._init_style()

    def _init_style(self):
        """Initialize UI style configuration"""
        self.style = Style([
            ('qmark', 'fg:yellow bold'),
            ('question', 'bold'),
            ('answer', 'fg:green bold'),
            ('pointer', 'fg:yellow bold'),
            ('selected', 'fg:green'),
            ('instruction', 'fg:blue'),
            ('example', 'fg:gray italic')
        ])

    def clear_screen(self):
        """Clear terminal screen and reset cursor position"""
        try:
            # Clear screen and reset cursor for Linux/Mac
            os.system('clear && tput cup 0 0')
        except Exception as e:
            # Fallback if clear fails
            print('\n' * 100)
            print("Error clearing screen: {}".format(e))

    def show_navigation_hint(self):
        """Show navigation instructions"""
        print("\nNavigation: Use ↑↓ arrow keys to move, Enter/Return to select")

    def confirm_action(self, message: str, default: bool = False) -> bool:
        """Generic confirmation dialog"""
        return questionary.confirm(
            message,
            default=default,
            style=self.style
        ).ask()

    def select_option(self, message: str, choices: List[str]) -> Optional[str]:
        """Generic selection dialog"""
        return questionary.select(
            message,
            choices=choices,
            style=self.style
        ).ask()