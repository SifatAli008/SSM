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
    
    # Check if sales table exists and has the required columns
    cursor.execute("PRAGMA table_info(sales)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    # If sales table exists but doesn't have required columns, drop and recreate it
    if columns and ('total_price' not in column_names or 'total_amount' not in column_names):
        print("Existing sales table found without required columns. Recreating the table...")
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
    
    # Add sample customers if empty
    cursor.execute("SELECT COUNT(*) FROM customers")
    if cursor.fetchone()[0] == 0:
        sample_customers = [
            ("John Doe", "555-123-4567", "john.doe@example.com", "123 Main St", "Regular customer", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            ("Jane Smith", "555-987-6543", "jane.smith@example.com", "456 Oak Ave", "VIP customer", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            ("Bob Johnson", "555-555-5555", "bob.johnson@example.com", "789 Pine Blvd", "", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            ("Alice Brown", "555-111-2222", "alice.brown@example.com", "321 Elm St", "New customer", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            ("Charlie Wilson", "555-333-4444", "charlie.wilson@example.com", "654 Maple Dr", "", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        ]
        
        cursor.executemany('''
            INSERT INTO customers (full_name, phone, email, address, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', sample_customers)
        print("Added sample customer data")
    
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
        
        # Get customer IDs
        cursor.execute("SELECT id, full_name FROM customers")
        customers = cursor.fetchall()
        
        # Get inventory items
        cursor.execute("SELECT id, selling_price FROM inventory")
        inventory_items = cursor.fetchall()
        
        if inventory_items and customers:
            # Generate sales for the past 90 days
            for i in range(90):
                sale_date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d %H:%M:%S")
                
                # Generate 1-5 sales for each day
                for _ in range(random.randint(1, 5)):
                    # Select random inventory item and customer
                    item_id, selling_price = random.choice(inventory_items)
                    customer_id, customer_name = random.choice(customers)
                    quantity = random.randint(1, 5)
                    total_amount = quantity * selling_price
                    total_price = total_amount  # Same as total_amount for simplicity
                    discount = round(random.uniform(0, 0.1) * total_price, 2)  # 0-10% discount
                    payment_amount = total_price - discount
                    
                    sample_sales.append((
                        item_id, 
                        quantity, 
                        selling_price, 
                        total_amount,
                        total_price,
                        customer_name, 
                        customer_id,
                        sale_date,
                        discount,
                        payment_amount,
                        'Cash',
                        0,  # due amount
                        'Completed'
                    ))
            
            cursor.executemany('''
                INSERT INTO sales (
                    inventory_id, quantity, sale_price, total_amount, total_price,
                    customer_name, customer_id, sale_date, discount, payment_amount,
                    payment_method, due_amount, status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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