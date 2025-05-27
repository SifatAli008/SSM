import sqlite3
import os
from pathlib import Path
from datetime import datetime, timedelta
import random

def create_db():
    # Use a relative path to find the database
    base_dir = Path(__file__).resolve().parent.parent
    db_path = os.path.join(base_dir, "data", "shop.db")
    
    # Create directories if they don't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # Connect to the SQLite database (it will be created if it doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Drop existing tables to ensure clean state
        cursor.execute("DROP TABLE IF EXISTS sales")
        cursor.execute("DROP TABLE IF EXISTS inventory")
        cursor.execute("DROP TABLE IF EXISTS customers")
        cursor.execute("DROP TABLE IF EXISTS users")
        
        # Create inventory table first
        cursor.execute('''  
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                details TEXT,
                category TEXT DEFAULT 'Other',
                stock INTEGER DEFAULT 0 CHECK (stock >= 0),
                buying_price REAL DEFAULT 0.0 CHECK (buying_price >= 0),
                selling_price REAL DEFAULT 0.0 CHECK (selling_price >= 0),
                reorder_level INTEGER DEFAULT 10 CHECK (reorder_level >= 0),
                sku TEXT UNIQUE,
                supplier_id INTEGER,
                expiry_date TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create indexes after table creation
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_inventory_category ON inventory(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_inventory_sku ON inventory(sku)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_inventory_stock ON inventory(stock)')

        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                role TEXT DEFAULT 'staff',
                email TEXT,
                last_login TEXT
            )
        ''')
        
        # Create customers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                address TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create sales table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inventory_id INTEGER,
                quantity INTEGER,
                sale_price REAL,
                total_amount REAL,
                total_price REAL,
                customer_name TEXT,
                customer_id INTEGER,
                sale_date TEXT,
                discount REAL DEFAULT 0,
                payment_amount REAL DEFAULT 0,
                payment_method TEXT DEFAULT 'Cash',
                due_amount REAL DEFAULT 0,
                status TEXT DEFAULT 'Completed',
                notes TEXT,
                FOREIGN KEY (inventory_id) REFERENCES inventory (id),
                FOREIGN KEY (customer_id) REFERENCES customers (id)
            )
        ''')
        
        # Add sample data
        add_sample_data(cursor)
        
        # Commit changes
        conn.commit()
        print(f"✅ Database created and tables initialized at {db_path}")
        
    except sqlite3.Error as e:
        print(f"❌ Error creating database: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def add_sample_data(cursor):
    """Add sample data to the database"""
    try:
        # Add sample customers
        sample_customers = [
            ("John Doe", "555-123-4567", "john.doe@example.com", "123 Main St", "Regular customer", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            ("Jane Smith", "555-987-6543", "jane.smith@example.com", "456 Oak Ave", "VIP customer", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            ("Bob Johnson", "555-555-5555", "bob.johnson@example.com", "789 Pine Blvd", "", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        ]
        
        cursor.executemany('''
            INSERT INTO customers (full_name, phone, email, address, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', sample_customers)
        print("✅ Added sample customer data")
        
        # Add sample inventory
        sample_inventory = [
            ("Smartphone X1", "Latest model with 128GB storage", "Electronics", 25, 400.0, 599.99, 10, "SPX1-128", None, None, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            ("Laptop Pro", "15-inch, 16GB RAM, 512GB SSD", "Electronics", 10, 800.0, 1299.99, 5, "LP15-512", None, None, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            ("Wireless Earbuds", "Noise cancelling, 24hr battery", "Electronics", 50, 80.0, 129.99, 20, "WE-24", None, None, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        ]
        
        cursor.executemany('''
            INSERT INTO inventory (name, details, category, stock, buying_price, selling_price, reorder_level, sku, supplier_id, expiry_date, created_at, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_inventory)
        print("✅ Added sample inventory data")
        
    except sqlite3.Error as e:
        print(f"❌ Error adding sample data: {e}")
        raise

def open_database_connection():
    # Use a relative path to find the database
    base_dir = Path(__file__).resolve().parent.parent
    db_path = os.path.join(base_dir, "data", "shop.db")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print(f"Database connection successful at {db_path}")
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