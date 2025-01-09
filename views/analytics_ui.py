from typing import List, Tuple, Dict, Optional
import questionary
from prettytable import PrettyTable
from .core import BaseUI
from controllers.analytics import AnalyticsController

class AnalyticsUI(BaseUI):
    """Analytics specific UI"""

    # Table configuration
    TABLE_HEADERS = [
        'Name', 'Category', 'Description',
        'Current Streak', 'Longest Streak', 
        'Days Passed', 'Success Rate',
        'Reset Count', 'Repeat', 'Importance'
    ]
    
    COLUMN_WIDTHS = {
        'Name': 20,
        'Category': 15,
        'Description': 50,
        'Current Streak': 12,
        'Longest Streak': 12,
        'Days Passed': 12,
        'Success Rate': 12,
        'Reset Count': 12,
        'Repeat': 8,
        'Importance': 10
    }
    
    DEFAULT_WIDTH = 15
    DEFAULT_ITEMS_PER_PAGE = 10

    def __init__(self, analytics_controller=None):
        super().__init__()
        self.analytics_controller = analytics_controller or AnalyticsController()
        self.current_sort = {'field': None, 'ascending': True}
        self.items_per_page = self.DEFAULT_ITEMS_PER_PAGE

    def _display_paginated_analytics(self, habits: List[Dict], page: int, items_per_page: int) -> None:
        """Display paginated analytics table"""
        if not habits:
            print("\nNo habits found")
            return
                
        table = self._initialize_table()
        self._configure_columns(table)
        self._add_habit_rows(table, habits, page, items_per_page)
        self._display_table(table)

    def _initialize_table(self) -> PrettyTable:
        """Create and configure table"""
        table = PrettyTable()
        table.field_names = self.TABLE_HEADERS
        table.align = "l"
        table.hrules = 1
        return table

    def _configure_columns(self, table: PrettyTable) -> None:
        """Configure column widths"""
        for header in table.field_names:
            table._max_width[header] = self.COLUMN_WIDTHS.get(header, self.DEFAULT_WIDTH)

    def _add_habit_rows(self, table: PrettyTable, habits: List[Dict], page: int, items_per_page: int) -> None:
        """Add habit rows with pagination"""
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        page_habits = habits[start_idx:end_idx]
            
        for habit in page_habits:
            table.add_row([
                habit['name'],
                habit['category'],
                habit['description'],
                habit['current_streak'],
                habit['longest_streak'],
                habit['days_passed'],
                habit['success_rate'],
                habit['reset_count'],
                habit['repeat'],
                habit['importance'] 
            ])

    def _display_table(self, table: PrettyTable) -> None:
        """Display formatted table"""
        print("\nAnalytics Overview:")
        print(table)

    def show_analytics_menu(self):
        """
        This method provides a paginated interface for viewing habit analytics,
        with options to filter, sort, and navigate through multiple pages of habits.
        Returns:
            None
        Features:
            - Paginated display of habits (15 items per page)
            - Filtering habits based on user criteria
            - Sorting habits by different fields
            - Navigation between pages
            - Option to reset view to original state
            - Return to main menu
        Notes:
            - If no habits are found, displays appropriate message and returns to main menu
            - Pagination controls (Previous/Next) appear dynamically based on current page
            - Current page and total pages are displayed for user reference
        """

        page = 1
        ITEMS_PER_PAGE = 15
        habits = self._get_habits_data()
        
        while True:
            if not habits:
                print("\nNo habits found")
                break
                
            self._display_paginated_analytics(habits, page, ITEMS_PER_PAGE)
            total_pages = self._get_total_pages(habits, ITEMS_PER_PAGE)
            
            choices = ["Filter Habits", "Sort Habits", "Reset View"]
            if page > 1:
                choices.append("Previous Page")
            if page < total_pages:
                choices.append("Next Page")
            choices.append("Back to Main Menu")
            
            action = questionary.select(
                "\nPage {}/{}".format(page, total_pages),
                choices=choices,
                style=self.style
            ).ask()
            
            if action == "Back to Main Menu":
                break
            elif action == "Next Page":
                page = min(page + 1, total_pages)
            elif action == "Previous Page":
                page = max(page - 1, 1)
            elif action == "Reset View":
                habits = self._get_habits_data()
                page = 1
                self.current_sort = {'field': None, 'ascending': True}
            elif action == "Sort Habits":
                habits = self.handle_sort_habits(habits)
            elif action == "Filter Habits":
                filtered = self.handle_filter_habits(habits)
                if filtered:
                    habits = filtered
                    page = 1

    def _get_habits_data(self) -> Optional[List[Dict]]:
        """Fetch habits data through controller"""
        return self.analytics_controller.get_analytics_data()
    
    def _get_total_pages(self, habits: List[tuple], items_per_page: int) -> int:
        """Calculate total number of pages"""
        return (len(habits) + items_per_page - 1) // items_per_page
    
    def handle_sort_habits(self, data: List[Dict]) -> List[Dict]:
        """
        This method prompts the user to select a field to sort by and the sort order,
        then returns the sorted data accordingly.
        Args:
            data (List[Dict]): List of dictionaries containing habit data to be sorted
        Returns:
            List[Dict]: The sorted list of habit dictionaries if sort options were selected,
                       or the original data if sorting was cancelled
        Note:
            The sort field is stored in self.current_sort as a dictionary containing:
            - 'field': The selected sort field (lowercase with spaces replaced by underscores)
            - 'ascending': Boolean indicating if sort order is ascending
        """

        sort_by = questionary.select(
            "Sort by:",
            choices=self.get_sortable_fields() + ["Cancel"],
            style=self.style
        ).ask()
        
        if sort_by == "Cancel":
            return data
            
        if sort_by:
            order = questionary.select(
                "Order:",
                choices=["Ascending", "Descending", "Cancel"],
                style=self.style
            ).ask()
            
            if order == "Cancel":
                return data
                
            if order:
                self.current_sort = {
                    'field': sort_by.lower().replace(' ', '_'),
                    'ascending': order == "Ascending"
                }
                return self.analytics_controller.sort_data(
                    data,
                    self.current_sort['field'],
                    self.current_sort['ascending']
                )
            self._clear_screen()
        return data

    def handle_filter_habits(self, data: List[Dict]) -> List[Dict]:
        """
        Handles the filtering of habits based on user selection.
        This method provides an interactive interface for users to filter habit data by selecting
        a field and a corresponding value. Users can also reset filters or cancel the operation.
        Args:
            data (List[Dict]): A list of dictionaries containing habit data to be filtered.
        Returns:
            List[Dict]: Filtered habit data based on user selection. Returns original data if:
                - User cancels the operation
                - No field is selected
                - Filter is reset
        """

        field = questionary.select(
            "Select field to filter by:",
            choices=self.get_filterable_fields() + ["Cancel"],
            style=self.style
        ).ask()
        
        if field == "Cancel":
            return data
            
        if field:
            values = self.get_unique_field_values(data, field)
            values.extend(["Reset Filter", "Cancel"])
            
            value = questionary.select(
                "Select {} value:".format(field.lower()),
                choices=values,
                style=self.style
            ).ask()
            
            if value == "Cancel":
                return data
                
            if value == "Reset Filter":
                self._clear_screen() 
                return self.analytics_controller.get_analytics_data()
                
            return self.analytics_controller.filter_data(
                data,
                field.lower(),
                value
            )
        self._clear_screen()
        return data

    def get_sortable_fields(self) -> List[str]:
        """Return list of sortable fields"""
        return [
            "Name", "Category", "Description", "Repeat",
            "Days Passed", "Success Rate", "Current Streak",
            "Reset Count", "Status"
        ]

    def get_filterable_fields(self) -> List[str]:
        """Return list of filterable fields"""
        return ["Name", "Category", "Description", "Repeat", "Status"]


    def get_unique_field_values(self, habits: List[Dict], field: str) -> List[str]:
        """Get unique values for field"""
        field_mapping = {
            'Name': 'name',
            'Category': 'category', 
            'Description': 'description',
            'Repeat': 'repeat',
            'Status': 'status'
        }
        
        key = field_mapping.get(field)
        if not key:
            return []
        return sorted(set(habit[key] for habit in habits))
    
    def process_analytics_action(self, habits: List[tuple], action: str) -> List[tuple]:
        """Process selected analytics action"""
        if action == "Sort Habits":
            return self.handle_sort_habits(habits)
        elif action == "Filter Habits":
            return self.handle_filter_habits(habits)
        elif action == "Reset View":
            self.current_sort = {'field': None, 'ascending': True}
            return self._get_habits_data()
        return habits