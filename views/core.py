import os
from typing import List, Dict, Optional
import questionary
from questionary import Style

class BaseUI:
    """Base User Interface class providing common UI functionality and styling.

    This class serves as a foundation for creating consistent terminal-based user interfaces,
    implementing common UI patterns and styling configurations.

    Attributes:
        style (Style): A questionary Style instance containing color and formatting rules.

    Methods:
        _init_style(): Initializes the UI style configuration with predefined color schemes.
        _clear_screen(): Clears the terminal screen in a cross-platform manner.
        _show_navigation_hint(): Displays navigation instructions for the user.
    """

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
            ('instruction', 'fg:cyan'),
            ('example', 'fg:gray italic')
        ])

    def _clear_screen(self):
        """Clear terminal screen and reset cursor position"""
        try:
            # Check OS and use appropriate command
            if os.name == 'nt':  # Windows
                os.system('cls')
            else:  # Unix/Linux/MacOS
                os.system('clear')
        except Exception as e:
            # Fallback: Print newlines
            print('\n' * 100)
            print("Error clearing screen: {}".format(e))

    def _show_navigation_hint(self):
        """Show navigation instructions"""
        print("\nNavigation: Use ↑↓ arrow keys to move, Enter/Return to select")


