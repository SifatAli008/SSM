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

    # Create inventory table if it doesn't already exist
    cursor.execute('''  
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            details TEXT,
            category TEXT DEFAULT 'Other',
            stock INTEGER DEFAULT 0,
            buying_price REAL DEFAULT 0.0,
            selling_price REAL DEFAULT 0.0,
            last_updated TEXT
        )
    ''')

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
    
    # Check if sales table exists and has the total_amount column
    cursor.execute("PRAGMA table_info(sales)")
    columns = cursor.fetchall()
    has_total_amount = any(col[1] == 'total_amount' for col in columns)
    
    # If sales table exists but doesn't have total_amount, drop and recreate it
    if columns and not has_total_amount:
        print("Existing sales table found without total_amount column. Recreating the table...")
        cursor.execute("DROP TABLE IF EXISTS sales")
        # Tables will be recreated below
    
    # Create sales table with all needed columns
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            inventory_id INTEGER,
            quantity INTEGER,
            sale_price REAL,
            total_amount REAL,
            customer_name TEXT,
            sale_date TEXT,
            FOREIGN KEY (inventory_id) REFERENCES inventory (id)
        )
    ''')
    
    # Add sample inventory data if empty
    cursor.execute("SELECT COUNT(*) FROM inventory")
    if cursor.fetchone()[0] == 0:
        sample_inventory = [
            ("Smartphone X1", "Latest model with 128GB storage", "Electronics", 25, 400.0, 599.99, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            ("Laptop Pro", "15-inch, 16GB RAM, 512GB SSD", "Electronics", 10, 800.0, 1299.99, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            ("Wireless Earbuds", "Noise cancelling, 24hr battery", "Electronics", 50, 80.0, 129.99, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            ("Smart Watch", "Fitness tracking, heart monitor", "Electronics", 30, 120.0, 199.99, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            ("Coffee Maker", "Programmable, 12-cup", "Appliances", 15, 45.0, 89.99, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            ("Blender", "High-speed, 5 settings", "Appliances", 20, 60.0, 119.99, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            ("T-Shirt", "100% cotton, various colors", "Clothing", 100, 8.0, 19.99, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            ("Jeans", "Slim fit, blue denim", "Clothing", 75, 25.0, 49.99, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            ("Sneakers", "Running shoes, sizes 7-12", "Footwear", 40, 35.0, 79.99, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            ("Backpack", "Water resistant, 30L capacity", "Accessories", 35, 30.0, 59.99, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        ]
        
        cursor.executemany('''
            INSERT INTO inventory (name, details, category, stock, buying_price, selling_price, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', sample_inventory)
        print("Added sample inventory data")
    
    # Create sample sales data if table is empty
    cursor.execute("SELECT COUNT(*) FROM sales")
    if cursor.fetchone()[0] == 0:
        # Generate random sales data for the past 90 days
        sample_sales = []
        customers = ["John Doe", "Jane Smith", "Bob Johnson", "Alice Brown", "Charlie Wilson", 
                     "Emma Davis", "Michael Miller", "Olivia Wilson", "James Taylor", "Sophia White"]
        
        # Get inventory items
        cursor.execute("SELECT id, selling_price FROM inventory")
        inventory_items = cursor.fetchall()
        
        if inventory_items:
            # Generate sales for the past 90 days
            for i in range(90):
                sale_date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d %H:%M:%S")
                
                # Generate 1-5 sales for each day
                for _ in range(random.randint(1, 5)):
                    # Select random inventory item
                    item_id, selling_price = random.choice(inventory_items)
                    quantity = random.randint(1, 5)
                    customer = random.choice(customers)
                    total_amount = quantity * selling_price
                    
                    sample_sales.append((item_id, quantity, selling_price, total_amount, customer, sale_date))
            
            cursor.executemany('''
                INSERT INTO sales (inventory_id, quantity, sale_price, total_amount, customer_name, sale_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', sample_sales)
            print(f"Added {len(sample_sales)} sample sales records")

    # Commit changes and close the connection
    conn.commit()
    conn.close()

    print(f"Database created and tables initialized at {db_path}")

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