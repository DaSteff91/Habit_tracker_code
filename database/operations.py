from database.connector import DatabaseConnector as Database
from datetime import datetime
import sqlite3
from typing import Dict, Any, List, Tuple, Optional

class DatabaseController:
    """Controls all database operations for habits and tasks"""
    
    def __init__(self, db_name: str = 'main.db'):
        """Initialize controller with database name"""
        self.db_name = db_name

    def create_data(self, table: str, data: Dict[str, Any]) -> int:
        """Insert data into database with table-specific duplicate checks"""
        try:
            with Database(self.db_name) as db:
                db.create_tables()
                
                # Table-specific duplicate checks
                if table == 'habit':
                    try:
                        conditions = {
                            'name': data['name'],
                            'description': data['description']
                        }
                    except KeyError as ke:
                        print("Missing required habit field: {}".format(ke))
                        return -1
                        
                elif table == 'task':
                    try:
                        conditions = {
                            'task_description': data['task_description'],
                            'habit_id': data['habit_id'],
                            'task_number': data['task_number'],
                            'due_date': data['due_date']  # Added due_date to conditions
                        }
                    except KeyError as ke:
                        print("Missing required task field: {}".format(ke))
                        return -1
                else:
                    print("Invalid table: {}".format(table))
                    return -1
                    
                existing_entries = db.read_data(table, conditions)
                
                if existing_entries:
                    print("Error: {} already exists!".format(table.capitalize()))
                    return -1
                    
                record_id = db.create_data(table, data)
                return record_id
                
        except sqlite3.Error as e:
            print("Database error: {}".format(e))
            return -1
        except Exception as e:
            print("General error: {}".format(e))
            return -1
        
    def delete_data(self, table: str, record_id: int) -> bool:
        """Delete record and associated data"""
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
        """Update existing record with verification"""
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
