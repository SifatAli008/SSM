from PyQt5.QtSql import QSqlDatabase
import os

def init_sqlite_connection():
    db = QSqlDatabase.addDatabase("QSQLITE")
    
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "E:/UDH/smart_shop_manager/data/shop.db"))
    db.setDatabaseName(db_path)

    if not db.open():
        print("❌ Failed to open SQLite database at:", db_path)
        return None

    print("✅ SQLite database connection opened at:", db_path)
    return db
