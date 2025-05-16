import sqlite3
import os
from pathlib import Path
from PyQt5.QtSql import QSqlDatabase, QSqlQuery

class DatabaseManager:
    """A utility class to manage database connections and operations"""
    
    @staticmethod
    def get_db_path():
        """Returns the standardized database path"""
        base_dir = Path(__file__).resolve().parent.parent.parent
        db_path = os.path.join(base_dir, "data", "shop.db")
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        return db_path
    
    @staticmethod
    def get_sqlite_connection():
        """Get a raw SQLite connection for direct SQL operations"""
        db_path = DatabaseManager.get_db_path()
        try:
            conn = sqlite3.connect(db_path)
            return conn
        except sqlite3.Error as e:
            print(f"SQLite connection error: {e}")
            return None
    
    @staticmethod
    def get_qt_connection():
        """Get a QSqlDatabase connection for Qt models and views"""
        db = QSqlDatabase.addDatabase("QSQLITE")
        db_path = DatabaseManager.get_db_path()
        db.setDatabaseName(db_path)
        
        if not db.open():
            print(f"❌ Failed to open Qt SQLite database at: {db_path}")
            return None
            
        return db
    
    @staticmethod
    def execute_query(query, params=None):
        """Execute a query and return results"""
        conn = DatabaseManager.get_sqlite_connection()
        if not conn:
            return None
            
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            conn.commit()
            result = cursor.fetchall()
            cursor.close()
            conn.close()
            return result
        except sqlite3.Error as e:
            print(f"Query execution error: {e}")
            if conn:
                conn.close()
            return None
    
    @staticmethod
    def execute_insert(query, params=None):
        """Execute an insert query and return the last row id"""
        conn = DatabaseManager.get_sqlite_connection()
        if not conn:
            return None
            
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            conn.commit()
            last_id = cursor.lastrowid
            cursor.close()
            conn.close()
            return last_id
        except sqlite3.Error as e:
            print(f"Insert execution error: {e}")
            if conn:
                conn.close()
            return None
