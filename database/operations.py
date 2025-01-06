from database.connector import DatabaseConnector as Database
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional

class DatabaseController:
    """Controls all database operations for habits and tasks"""
    
    def __init__(self, db_name: str = 'main.db'):
        """Initialize controller with database name"""
        self.db_name = db_name

    def create_data(self, table: str, data: Dict[str, Any]) -> int:
        """Create a new record in the specified table.
        This method coordinates the main data creation process, including table validation,
        duplicate checking, and record insertion.
        Args:
            table (str): The name of the table where data will be inserted
            data (Dict[str, Any]): Dictionary containing the data to insert, where keys are column names
                                  and values are the data to insert
        Returns:
            int: The ID of the newly created record if successful, -1 if operation fails
                 Failure can occur due to:
                 - Invalid table name
                 - Invalid data format
                 - Duplicate entry exists
                 - Database connection/operation error
        """
        try:
            with Database(self.db_name) as db:
                db.create_tables()
                
                # Validate table and data
                if not self._validate_table(table):
                    return -1
                    
                # Get and validate conditions
                conditions = self._get_duplicate_conditions(table, data)
                if not conditions:
                    return -1
                    
                # Check for duplicates
                if self._check_duplicates(db, table, conditions):
                    return -1
                    
                # Create record
                return db.create_data(table, data)
                
        except Exception as e:
            print("Error creating data: {}".format(e))
            return -1

    def _validate_table(self, table: str) -> bool:
        """
        Validates if the provided table name is valid within the database schema.
        Args:
            table (str): Name of the table to validate.
        Returns:
            bool: True if table name is valid ('habit' or 'task'), False otherwise.
        """
        
        if table not in ['habit', 'task']:
            print("Invalid table: {}".format(table))
            return False
        return True

    def _get_duplicate_conditions(self, table: str, data: Dict[str, Any]) -> Optional[Dict]:
        """
        Determines the conditions for checking duplicate entries in the database based on the table and data provided.

        Args:
            table (str): The name of the database table ('habit' or 'task').
            data (Dict[str, Any]): Dictionary containing the data fields to check for duplicates.

        Returns:
            Optional[Dict]: A dictionary containing the fields and values to check for duplicates.
                           For 'habit' table, returns name and description.
                           For 'task' table, returns task_description, habit_id, task_number and due_date.
                           Returns None if required fields are missing or table is not recognized.
        """

        try:
            if table == 'habit':
                return {
                    'name': data['name'],
                    'description': data['description']
                }
            elif table == 'task':
                return {
                    'task_description': data['task_description'],
                    'habit_id': data['habit_id'],
                    'task_number': data['task_number'],
                    'due_date': data['due_date']
                }
        except KeyError as ke:
            print("Missing required {} field: {}".format(table, ke))
        return None

    def _check_duplicates(self, db: Database, table: str, conditions: Dict) -> bool:
        """
        Check if a record with given conditions already exists in the specified table.

        Args:
            db (Database): Database instance to check against
            table (str): Name of the table to check in
            conditions (Dict): Dictionary containing column-value pairs to check for duplicates

        Returns:
            bool: True if duplicate exists, False otherwise

        """

        existing = db.read_data(table, conditions)
        if existing:
            print("Error: {} already exists!".format(table.capitalize()))
            return True
        return False
        
    def delete_data(self, table: str, record_id: int) -> bool:
        """Delete record and associated task data from the specified table.

        This method deletes a record from the specified table based on the record ID.
        If the table is 'habit', it also deletes all associated task records before
        deleting the habit record.

        Args:
            table (str): The name of the table to delete from ('habit' or 'task')
            record_id (int): The ID of the record to delete

        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            with Database(self.db_name) as db:
                if table == 'habit':
                    db.delete_data('task', {'habit_id': record_id})
                result = db.delete_data(table, {'id': record_id})
                return result
        except Exception as e:
            print("Error deleting data: {}".format(e))
            return False

    def update_data(self, table: str, record_id: int, new_data: Dict[str, Any]) -> bool:
        """
        Update an existing record in the specified table with new data.
        Args:
            table (str): The name of the table where the record exists.
            record_id (int): The ID of the record to be updated.
            new_data (Dict[str, Any]): A dictionary containing the new data to update the record with.
        Returns:
            bool: True if the update was successful, False otherwise.
        """
        try:
            with Database(self.db_name) as db:
                if not db.read_data(table, {'id': record_id}):
                    print("Error: {} with ID {} not found".format(table.capitalize(), record_id))
                    return False
                    
                result = db.update_data(table, new_data, {'id': record_id})
                return result
        except Exception as e:
            print("Error updating data: {}".format(e))
            return False

    def read_data(self, table: str, conditions: Optional[Dict[str, Any]] = None) -> List[Tuple]:
        """
        Read data from database table with optional conditions
        
        Args:
            table: Name of table to read from ('habit' or 'task')
            conditions: Optional filtering conditions
            
        Returns:
            List of tuples containing the matched records, empty list if no data found
        """
        try:
            with Database(self.db_name) as db:
                data = db.read_data(table, conditions)
                
                if not data:
                    print("No data found in {} table".format(table))
                    return []
                return data
                    
        except Exception as e:
            print("Error reading {}: {}".format(table, e))
            return []

    def get_table_headers(self, table: str) -> List[str]:
        """
        Get column names for specified table
        
        Args:
            table: Name of the table ('habit' or 'task')
            
        Returns:
            List of column names
        """
        try:
            with Database(self.db_name) as db:
                if table not in ['habit', 'task']:
                    return []
                return db.get_table_header(table)
        except Exception as e:
            print("Error getting table headers: {}".format(e))
            return []
