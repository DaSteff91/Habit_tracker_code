import sqlite3
from typing import List, Tuple

class DatabaseConnector:
    def __init__(self, db_name: str = "main.db"):
        """Initialize database connection"""
        self.db_name = db_name
        self.connection = None
        self.cursor = None
        self.connect()  

    def connect(self) -> None:
        """Establish database connection"""
        try:
            self.connection = sqlite3.connect(
                self.db_name,
                timeout=10,
                isolation_level=None)
            self.cursor = self.connection.cursor()
        except sqlite3.Error as e:
            print("Connection error: {}".format(e))

    def create_tables(self) -> bool:
        """Create necessary database tables.

        This method initializes the database by creating required tables for habits and tasks.
        It calls private methods to create individual tables and commits the changes.

        Returns:
            bool: True if tables were created successfully, False if an error occurred during creation.

        Raises:
            sqlite3.Error: If there is an error while creating the tables or committing changes.
        """
        try:
            self._create_habit_table()
            self._create_task_table()
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print("Error creating tables: {}".format(e))
            return False

    def _create_habit_table(self) -> None:
        """Create habit table with schema"""
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS habit (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            created TEXT NOT NULL,
            start TEXT NOT NULL,
            end TEXT,
            importance TEXT NOT NULL,
            repeat TEXT NOT NULL,
            tasks INT NOT NULL,
            tasks_description TEXT NOT NULL,
            streak INT NOT NULL DEFAULT 0,
            streak_reset_count INT NOT NULL DEFAULT 0,
            longest_streak INT NOT NULL DEFAULT 0 
        )""")

    def _create_task_table(self) -> None:
        """Create task table with schema and foreign key"""
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS task (
            id INTEGER PRIMARY KEY,
            habit_id INTEGER NOT NULL,
            task_number INTEGER NOT NULL,
            task_description TEXT NOT NULL,
            created TEXT NOT NULL,
            due_date TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (habit_id) REFERENCES habit (id)
        )""")

    def create_data(self, table: str, data: dict) -> int:
        """
        Inserts data into the specified table in the database.

        Args:
            table (str): The name of the table where data will be inserted.
            data (dict): A dictionary containing the column names as keys and the corresponding values to be inserted.

        Returns:
            int: The ID of the last row inserted if successful, -1 if an error occurs.
        """
        try:
            columns = ', '.join(data.keys())    # Creates a comma-separated string of keys
            placeholders = ', '.join(['?' for _ in data]) # Creates a comma-separated string of question marks to prevent SQL injection
            query = "INSERT INTO {} ({}) VALUES ({})".format(table, columns, placeholders)
            self.cursor.execute(query, list(data.values())) # list() creates a list of the values from the dictionary. The execute functions takes both, the created SQL statement ant the respective value from the data
            self.connection.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print("Error creating record: {}".format(e))
            return -1

    def read_data(self, table: str, conditions: dict = None) -> List[Tuple]:
        """
        Reads data from the specified table in the database with optional conditions.

        Args:
            table (str): The name of the table to read data from.
            conditions (dict, optional): A dictionary of conditions to filter the query. 
                                         The keys are column names and the values are the 
                                         values to match. Defaults to None.

        Returns:
            List[Tuple]: A list of tuples containing the rows that match the query.
                         Returns an empty list if an error occurs.
        """
        try:
            query = "SELECT * FROM {}".format(table)
            if conditions:  # To create a WHERE clause with one or more conditions
                where_clause = ' AND '.join(["{} = ?".format(k) for k in conditions.keys()])
                query += " WHERE {}".format(where_clause)
                self.cursor.execute(query, list(conditions.values()))
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print("Error reading records: {}".format(e))
            return []

    def update_data(self, table: str, data: dict, conditions: dict) -> bool:
        """
        Update records in the specified table that match the given conditions.

        Args:
            table (str): The name of the table to update.
            data (dict): A dictionary of column-value pairs to update.
            conditions (dict): A dictionary of column-value pairs to match for the update.

        Returns:
            bool: True if the update was successful, False otherwise.
            
        """
        try:
            set_clause = ', '.join(["{} = ?".format(k) for k in data.keys()])
            where_clause = ' AND '.join(["{} = ?".format(k) for k in conditions.keys()])
            query = "UPDATE {} SET {} WHERE {}".format(table, set_clause, where_clause)
            values = list(data.values()) + list(conditions.values())
            self.cursor.execute(query, values)
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print("Error updating records: {}".format(e))
            return False

    def delete_data(self, table: str, conditions: dict) -> bool:
        """
        Delete records from a specified table that match the given conditions.

        Args:
            table (str): The name of the table from which to delete records.
            conditions (dict): A dictionary of conditions to match for deletion, 
                               where keys are column names and values are the 
                               corresponding values to match.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        try:
            where_clause = ' AND '.join(["{} = ?".format(k) for k in conditions.keys()])
            query = "DELETE FROM {} WHERE {}".format(table, where_clause)
            self.cursor.execute(query, list(conditions.values()))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print("Error deleting records: {}".format(e))
            return False

    def get_table_header(self, table_name: str) -> List[str]:
        """
        Get table column names
        
        Args:
            table_name: Name of the table ('habit' or 'task')
            
        Returns:
            List of column names
        """
        try:
            self.cursor.execute(f"PRAGMA table_info({table_name})")
            return [column[1] for column in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print("Error getting table info: {}".format(e))
            return []

    def commit(self) -> None:
        """
        Commits the current transaction to the database.
        This method saves all changes made to the database since the last commit.
        """
        self.connection.commit()

    def close(self) -> None:
        """
        Close the database connection if it is open.

        This method checks if the database connection (`self.conn`) is open,
        and if so, it closes the connection to free up resources.
        """
        if self.connection:
            self.connection.close()

    def __enter__(self):
        """
        - Context manager method
        - Allows using database with with statement
        - Returns database instance
        - Example: with Database('db.sqlite') as db:  
        """
        self.connect()
        return self
    

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        - Context manager cleanup method
        - Called when exiting with block
        - Automatically closes database connection
        - Handles exceptions that occurred in with block
        """
        if self.connection:  
            self.connection.close()

