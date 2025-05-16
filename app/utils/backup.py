import os
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
import zipfile
import json
from app.utils.logger import logger
from app.utils.database import DatabaseManager


class BackupManager:
    """Utility class for managing database backups"""
    
    @staticmethod
    def get_backup_dir():
        """Return the path to the backups directory"""
        base_dir = Path(__file__).resolve().parent.parent.parent
        backup_dir = os.path.join(base_dir, "backups")
        os.makedirs(backup_dir, exist_ok=True)
        return backup_dir
    
    @staticmethod
    def create_backup():
        """
        Create a full backup of the database file
        
        Returns:
            str: Path to the backup file, or None if backup failed
        """
        try:
            # Get database path and backup directory
            db_path = DatabaseManager.get_db_path()
            if not os.path.exists(db_path):
                logger.error(f"Database file not found at {db_path}")
                return None
                
            backup_dir = BackupManager.get_backup_dir()
            
            # Create a timestamped backup filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"shop_db_backup_{timestamp}.db"
            backup_path = os.path.join(backup_dir, backup_filename)
            
            # Make a direct copy of the database file
            shutil.copy2(db_path, backup_path)
            
            logger.info(f"Database backup created at {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Error creating database backup: {str(e)}")
            return None
    
    @staticmethod
    def create_structure_backup():
        """
        Create a backup of the database structure without data
        
        Returns:
            str: Path to the structure backup file, or None if backup failed
        """
        try:
            # Get database path and backup directory
            db_path = DatabaseManager.get_db_path()
            backup_dir = BackupManager.get_backup_dir()
            
            # Create a timestamped backup filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"db_structure_{timestamp}.sql"
            backup_path = os.path.join(backup_dir, backup_filename)
            
            # Connect to the database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get list of all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            # Open the backup file for writing
            with open(backup_path, 'w') as f:
                # Add a header to the file
                f.write("-- Database structure backup\n")
                f.write(f"-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # For each table, get and write the CREATE TABLE statement
                for table in tables:
                    table_name = table[0]
                    
                    # Skip sqlite_sequence table
                    if table_name == 'sqlite_sequence':
                        continue
                        
                    cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}';")
                    create_table_stmt = cursor.fetchone()[0]
                    
                    f.write(f"{create_table_stmt};\n\n")
            
            conn.close()
            
            logger.info(f"Database structure backup created at {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Error creating database structure backup: {str(e)}")
            return None
    
    @staticmethod
    def create_data_export(tables=None):
        """
        Export data from selected tables to JSON format
        
        Args:
            tables: List of table names to export, or None for all tables
            
        Returns:
            str: Path to the exported data file, or None if export failed
        """
        try:
            # Get database path and backup directory
            db_path = DatabaseManager.get_db_path()
            backup_dir = BackupManager.get_backup_dir()
            
            # Create a timestamped export filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_filename = f"data_export_{timestamp}.json"
            export_path = os.path.join(backup_dir, export_filename)
            
            # Connect to the database
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row  # This enables column access by name
            cursor = conn.cursor()
            
            # Get list of all tables if not specified
            if not tables:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [table[0] for table in cursor.fetchall() if table[0] != 'sqlite_sequence']
            
            # Prepare the data dictionary
            export_data = {
                "metadata": {
                    "exported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "tables": tables
                },
                "tables": {}
            }
            
            # For each table, export all data
            for table_name in tables:
                try:
                    cursor.execute(f"SELECT * FROM {table_name};")
                    rows = cursor.fetchall()
                    
                    # Convert rows to list of dictionaries
                    table_data = []
                    for row in rows:
                        table_data.append({key: row[key] for key in row.keys()})
                    
                    export_data["tables"][table_name] = table_data
                    
                except sqlite3.Error as table_error:
                    logger.warning(f"Error exporting table {table_name}: {str(table_error)}")
                    export_data["tables"][table_name] = {"error": str(table_error)}
            
            conn.close()
            
            # Write the data to the JSON file
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"Data export created at {export_path}")
            return export_path
            
        except Exception as e:
            logger.error(f"Error creating data export: {str(e)}")
            return None
    
    @staticmethod
    def restore_backup(backup_path):
        """
        Restore a database from a backup file
        
        Args:
            backup_path: Path to the backup file
            
        Returns:
            bool: True if restore was successful, False otherwise
        """
        try:
            # Verify the backup file exists
            if not os.path.exists(backup_path):
                logger.error(f"Backup file not found at {backup_path}")
                return False
            
            # Get current database path
            db_path = DatabaseManager.get_db_path()
            
            # Create a backup of the current database before restoring
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pre_restore_backup = os.path.join(
                os.path.dirname(db_path), 
                f"pre_restore_backup_{timestamp}.db"
            )
            
            # Make sure the database isn't being used
            try:
                conn = sqlite3.connect(db_path)
                conn.close()
            except sqlite3.Error:
                logger.error("Cannot restore backup while database is in use")
                return False
            
            # Make a backup just in case
            shutil.copy2(db_path, pre_restore_backup)
            
            # Restore the backup
            shutil.copy2(backup_path, db_path)
            
            logger.info(f"Database restored from backup {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error restoring database backup: {str(e)}")
            return False
    
    @staticmethod
    def list_backups():
        """
        List all available database backups
        
        Returns:
            list: List of dictionaries with backup information
        """
        try:
            backup_dir = BackupManager.get_backup_dir()
            backups = []
            
            # Check for database backup files
            for filename in os.listdir(backup_dir):
                if filename.startswith("shop_db_backup_") and filename.endswith(".db"):
                    file_path = os.path.join(backup_dir, filename)
                    file_size = os.path.getsize(file_path)
                    file_date = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    backups.append({
                        "filename": filename,
                        "path": file_path,
                        "size": file_size,
                        "date": file_date.strftime("%Y-%m-%d %H:%M:%S"),
                        "type": "full"
                    })
                elif filename.startswith("db_structure_") and filename.endswith(".sql"):
                    file_path = os.path.join(backup_dir, filename)
                    file_size = os.path.getsize(file_path)
                    file_date = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    backups.append({
                        "filename": filename,
                        "path": file_path,
                        "size": file_size,
                        "date": file_date.strftime("%Y-%m-%d %H:%M:%S"),
                        "type": "structure"
                    })
                elif filename.startswith("data_export_") and filename.endswith(".json"):
                    file_path = os.path.join(backup_dir, filename)
                    file_size = os.path.getsize(file_path)
                    file_date = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    backups.append({
                        "filename": filename,
                        "path": file_path,
                        "size": file_size,
                        "date": file_date.strftime("%Y-%m-%d %H:%M:%S"),
                        "type": "data_export"
                    })
            
            # Sort backups by date (newest first)
            backups.sort(key=lambda x: x["date"], reverse=True)
            
            return backups
            
        except Exception as e:
            logger.error(f"Error listing database backups: {str(e)}")
            return []
    
    @staticmethod
    def cleanup_old_backups(days_to_keep=30):
        """
        Delete backups older than the specified number of days
        
        Args:
            days_to_keep: Number of days to keep backups
            
        Returns:
            int: Number of deleted backup files
        """
        try:
            backup_dir = BackupManager.get_backup_dir()
            now = datetime.now()
            deleted_count = 0
            
            for filename in os.listdir(backup_dir):
                if any(filename.startswith(prefix) for prefix in 
                      ["shop_db_backup_", "db_structure_", "data_export_"]):
                    file_path = os.path.join(backup_dir, filename)
                    file_date = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    # Check if the file is older than days_to_keep
                    if (now - file_date).days > days_to_keep:
                        os.remove(file_path)
                        deleted_count += 1
                        logger.info(f"Deleted old backup: {filename}")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old backups: {str(e)}")
            return 0
