import sqlite3
import os
from pathlib import Path

def create_db():
    """Create SQLite database and initialize the inventory table."""
    # Use a relative path to find the database
    base_dir = Path(__file__).resolve().parent.parent
    db_path = os.path.join(base_dir, "data", "shop.db")
    
    # Create directories if they don't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # Connect to the SQLite database (it will be created if it doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create inventory table if it doesn't already exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            stock INTEGER DEFAULT 0,
            buying_price REAL DEFAULT 0.0,
            selling_price REAL DEFAULT 0.0
        )
    ''')

    # Commit changes and close the connection
    conn.commit()
    conn.close()

    print(f"Database created and table initialized at {db_path}")

if __name__ == "__main__":
    create_db()
