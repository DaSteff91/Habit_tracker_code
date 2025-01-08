import sqlite3
from typing import Optional, List, Tuple, Dict, Any

class DatabaseConnectorTesting:
    """Test-specific database connector"""
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.connection: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None

    def connect(self):
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()
        self.create_tables()
        
    def create_tables(self) -> bool:
        """Create necessary database tables"""
        self._create_habit_table()
        self._create_task_table()
        self.connection.commit()

    def close(self) -> None:
        """Close database connection"""
        self.connection.close()

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

    def create_data(self, table: str, data: Dict[str, Any]) -> int:
        """Create test record"""
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = "INSERT INTO {} ({}) VALUES ({})".format(
            table, columns, placeholders)
        self.cursor.execute(query, list(data.values()))
        self.connection.commit()
        return self.cursor.lastrowid

    def read_data(self, table: str, conditions: Dict = None) -> List[Tuple]:
        """Read test data"""
        query = f"SELECT * FROM {table}"
        if conditions:
            where = ' AND '.join([f"{k}=?" for k in conditions])
            query += f" WHERE {where}"
            self.cursor.execute(query, list(conditions.values()))
        else:
            self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def update_data(self, table: str, record_id: int, data: Dict[str, Any]) -> bool:
        """Update test record"""
        set_clause = ', '.join([f"{k}=?" for k in data.keys()])
        query = "UPDATE {} SET {} WHERE id=?".format(table, set_clause)
        values = list(data.values()) + [record_id]
        self.cursor.execute(query, values)
        self.connection.commit() 
        return True

    def delete_data(self, table: str, record_id: int) -> bool:
            """Delete test record"""
            self.cursor.execute(
                "DELETE FROM {} WHERE id=?".format(table), 
                [record_id])
            self.connection.commit()
            return True
    
    def get_tables(self) -> List[str]:
        """Get list of tables in database"""
        self.cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table'
            ORDER BY name;
        """)
        return [table[0] for table in self.cursor.fetchall()]

    def create_test_habit(self, habit_data: Dict[str, Any]) -> int:
        """Create test habit and return ID"""
        return self.create_data('habit', habit_data)

    def create_test_task(self, task_data: Dict[str, Any]) -> int:
        """Create test task and return ID"""
        return self.create_data('task', task_data)

    def create_test_habit_with_tasks(self, habit_data: Dict[str, Any], 
                                   task_data: Dict[str, Any]) -> Tuple[int, int]:
        """Create test habit with associated tasks"""
        habit_id = self.create_test_habit(habit_data)
        task_data['habit_id'] = habit_id
        task_id = self.create_test_task(task_data)
        return habit_id, task_id