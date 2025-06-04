from abc import ABC, abstractmethod
from config.settings import COLLECTION_INVENTORY, COLLECTION_SALES
from config.database import FirebaseDB
import sqlite3

class BaseDataProvider(ABC):
    # Inventory
    @abstractmethod
    def get_products(self):
        pass

    @abstractmethod
    def add_product(self, product_data):
        pass

    # Sales
    @abstractmethod
    def get_sales(self):
        pass

    @abstractmethod
    def add_sale(self, sale_data):
        pass

# SQLAlchemy/SQLite implementation
class SQLDataProvider(BaseDataProvider):
    def __init__(self, db_manager):
        self.db = db_manager

    def get_products(self):
        # Query all products from the products table
        conn = self.db.get_qt_connection() if hasattr(self.db, 'get_qt_connection') else self.db
        cur = conn.cursor()
        cur.execute("SELECT * FROM products")
        columns = [desc[0] for desc in cur.description]
        return [dict(zip(columns, row)) for row in cur.fetchall()]

    def add_product(self, product_data):
        # Insert a new product into the products table
        conn = self.db.get_qt_connection() if hasattr(self.db, 'get_qt_connection') else self.db
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO products (name, stock_quantity, price, category, details, buying_price, selling_price)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            product_data.get('name'),
            product_data.get('quantity', product_data.get('stock', 0)),
            product_data.get('price', 0.0),
            product_data.get('category', 'Other'),
            product_data.get('details', ''),
            product_data.get('buying_price', 0.0),
            product_data.get('selling_price', 0.0)
        ))
        conn.commit()
        return cur.lastrowid

    def get_sales(self):
        # Query all sales from the sales table
        conn = self.db.get_qt_connection() if hasattr(self.db, 'get_qt_connection') else self.db
        cur = conn.cursor()
        cur.execute("SELECT * FROM sales")
        columns = [desc[0] for desc in cur.description]
        return [dict(zip(columns, row)) for row in cur.fetchall()]

    def add_sale(self, sale_data):
        # Insert a new sale into the sales table
        conn = self.db.get_qt_connection() if hasattr(self.db, 'get_qt_connection') else self.db
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO sales (invoice_number, date, customer_id, total_price, discount, payment_amount, payment_method, due_amount, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            sale_data.get('invoice_number'),
            sale_data.get('date'),
            sale_data.get('customer_id'),
            sale_data.get('total_price'),
            sale_data.get('discount', 0),
            sale_data.get('payment_amount', 0),
            sale_data.get('payment_method', 'Cash'),
            sale_data.get('due_amount', 0),
            sale_data.get('status', 'Completed'),
            sale_data.get('notes', '')
        ))
        sale_id = cur.lastrowid
        # Insert sale items if provided
        items = sale_data.get('items', [])
        for item in items:
            cur.execute("""
                INSERT INTO sale_items (sale_id, product_id, quantity, unit_price, discount, subtotal)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                sale_id,
                item['product_id'],
                item['quantity'],
                item['unit_price'],
                item.get('discount', 0),
                item['subtotal']
            ))
            # Update inventory
            cur.execute("UPDATE products SET stock_quantity = stock_quantity - ? WHERE id = ?", (item['quantity'], item['product_id']))
        conn.commit()
        return sale_id

# Firebase implementation
class FirebaseDataProvider(BaseDataProvider):
    def __init__(self, firebase_client=None):
        self.client = firebase_client or FirebaseDB()

    def get_products(self):
        # Fetch all products from Firebase inventory collection
        collection = self.client.get_collection(COLLECTION_INVENTORY)
        docs = collection.stream() if collection else []
        return [doc.to_dict() | {'id': doc.id} for doc in docs]

    def add_product(self, product_data):
        # Add a product to Firebase inventory collection
        collection = self.client.get_collection(COLLECTION_INVENTORY)
        if not collection:
            return None
        result = collection.add(product_data)
        return getattr(result, 'id', None) if hasattr(result, 'id') else None

    def get_sales(self):
        # Fetch all sales from Firebase sales collection
        collection = self.client.get_collection(COLLECTION_SALES)
        docs = collection.stream() if collection else []
        return [doc.to_dict() | {'id': doc.id} for doc in docs]

    def add_sale(self, sale_data):
        # Add a sale to Firebase sales collection
        collection = self.client.get_collection(COLLECTION_SALES)
        if not collection:
            return None
        result = collection.add(sale_data)
        return getattr(result, 'id', None) if hasattr(result, 'id') else None 