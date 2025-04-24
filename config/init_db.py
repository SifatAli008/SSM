import sqlite3
import os

def create_db():
    # Path to the database
    db_path = 'E:/UDH/smart_shop_manager/data/shop.db'  # Ensure this path is correct
    os.makedirs(os.path.dirname(db_path), exist_ok=True)  # Create directories if not exist

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

    print("Database created and table initialized.")

def open_database_connection():
    # Path to the database
    db_path = 'E:/UDH/smart_shop_manager/data/shop.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print("Database connection successful!")
        return conn, cursor
    except sqlite3.Error as e:
        print(f"Error opening database: {e}")
        return None, None

if __name__ == "__main__":
    create_db()
    # Check connection
    conn, cursor = open_database_connection()
    if conn:
        print("Database is open and ready to use!")
    else:
        print("Failed to open database!")
    if conn:
        conn.close()    