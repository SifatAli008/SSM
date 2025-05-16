from PyQt5.QtSql import QSqlDatabase
import os
from pathlib import Path

def init_sqlite_connection():
    db = QSqlDatabase.addDatabase("QSQLITE")
    
    # Use a relative path to find the database
    base_dir = Path(__file__).resolve().parent.parent
    db_path = os.path.join(base_dir, "data", "shop.db")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    db.setDatabaseName(db_path)

    if not db.open():
        print(f"❌ Failed to open SQLite database at: {db_path}")
        return None

    print(f"✅ SQLite database connection opened at: {db_path}")
    return db
