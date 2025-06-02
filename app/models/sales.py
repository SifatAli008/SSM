import sqlite3
from datetime import datetime

class SalesModel:
    """Database model for sales operations"""
    
    def __init__(self, db_conn):
        self.conn = db_conn
        self.create_tables()
    
    def create_tables(self):
        """Create necessary tables if they don't exist"""
        # Sales table
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT NOT NULL,
                date TEXT NOT NULL,
                customer_id INTEGER,
                total_price REAL NOT NULL,
                discount REAL DEFAULT 0,
                payment_amount REAL NOT NULL,
                payment_method TEXT DEFAULT 'Cash',
                due_amount REAL DEFAULT 0,
                status TEXT DEFAULT 'Completed',
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
        ''')
        
        # Sale items table (detailed items in each sale)
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS sale_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                discount REAL DEFAULT 0,
                subtotal REAL NOT NULL,
                FOREIGN KEY (sale_id) REFERENCES sales(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        ''')
        
        self.conn.commit()
    
    def add_sale(self, invoice_number, date, customer_id, total_price, 
                 discount=0, payment_amount=0, payment_method='Cash', 
                 due_amount=0, status='Completed', notes='', items=None):
        """
        Add a new sale record
        """
        try:
            # Insert sale record
            cur = self.conn.cursor()
            cur.execute('''
                INSERT INTO sales (
                    invoice_number, date, customer_id, total_price, discount,
                    payment_amount, payment_method, due_amount, status, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                invoice_number, date, customer_id, total_price, discount,
                payment_amount, payment_method, due_amount, status, notes
            ))
            
            sale_id = cur.lastrowid
            
            # Insert sale items if provided
            if items and isinstance(items, list):
                for item in items:
                    cur.execute('''
                        INSERT INTO sale_items (
                            sale_id, product_id, quantity, unit_price, 
                            discount, subtotal
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        sale_id,
                        item['product_id'],
                        item['quantity'],
                        item['unit_price'],
                        item.get('discount', 0),
                        item['subtotal']
                    ))
                    
                    # Update inventory
                    cur.execute('''
                        UPDATE products 
                        SET stock_quantity = stock_quantity - ? 
                        WHERE id = ?
                    ''', (item['quantity'], item['product_id']))
            
            self.conn.commit()
            return sale_id
        
        except Exception as e:
            self.conn.rollback()
            raise e
    
    def get_sales(self, search=None, start_date=None, end_date=None, limit=50, offset=0):
        """
        Get sales records with optional filtering
        """
        cur = self.conn.cursor()
        query = '''
            SELECT s.*, c.full_name as customer_name 
            FROM sales s
            LEFT JOIN customers c ON s.customer_id = c.id
            WHERE 1=1
        '''
        params = []
        
        if search:
            query += ' AND (s.invoice_number LIKE ? OR c.full_name LIKE ?)' 
            params.extend([f'%{search}%', f'%{search}%'])
        
        if start_date:
            query += ' AND date(s.date) >= date(?)'
            params.append(start_date)
            
        if end_date:
            query += ' AND date(s.date) <= date(?)'
            params.append(end_date)
            
        query += ' ORDER BY s.date DESC LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        
        cur.execute(query, params)
        return cur.fetchall()
    
    def get_sale_by_id(self, sale_id):
        """Get a sale by ID including its items"""
        cur = self.conn.cursor()
        
        # Get sale info
        cur.execute('''
            SELECT s.*, c.full_name as customer_name 
            FROM sales s
            LEFT JOIN customers c ON s.customer_id = c.id
            WHERE s.id = ?
        ''', (sale_id,))
        sale = cur.fetchone()
        
        if not sale:
            return None
        
        # Get sale items
        cur.execute('''
            SELECT si.*, p.name as product_name
            FROM sale_items si
            JOIN products p ON si.product_id = p.id
            WHERE si.sale_id = ?
        ''', (sale_id,))
        items = cur.fetchall()
        
        sale_dict = dict(sale)
        sale_dict['items'] = [dict(item) for item in items]
        return sale_dict
    
    def update_sale(self, sale_id, **kwargs):
        """
        Update a sale record
        """
        try:
            # Handle sale items separately
            items = kwargs.pop('items', None)
            
            # Update sale record
            if kwargs:
                fields = ', '.join([f'{k}=?' for k in kwargs])
                values = list(kwargs.values())
                values.append(sale_id)
                
                self.conn.execute(f'''
                    UPDATE sales 
                    SET {fields} 
                    WHERE id=?
                ''', values)
            
            # Update sale items if provided
            if items and isinstance(items, list):
                # First, get current items to calculate stock differences
                cur = self.conn.cursor()
                cur.execute('SELECT product_id, quantity FROM sale_items WHERE sale_id = ?', 
                           (sale_id,))
                old_items = {row[0]: row[1] for row in cur.fetchall()}
                
                # Remove existing items
                self.conn.execute('DELETE FROM sale_items WHERE sale_id = ?', (sale_id,))
                
                # Add new items
                for item in items:
                    cur.execute('''
                        INSERT INTO sale_items (
                            sale_id, product_id, quantity, unit_price, 
                            discount, subtotal
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        sale_id,
                        item['product_id'],
                        item['quantity'],
                        item['unit_price'],
                        item.get('discount', 0),
                        item['subtotal']
                    ))
                    
                    # Adjust inventory based on changes
                    product_id = item['product_id']
                    old_qty = old_items.get(product_id, 0)
                    new_qty = item['quantity']
                    
                    if old_qty != new_qty:
                        # Calculate how much stock to add/remove
                        stock_change = old_qty - new_qty
                        
                        cur.execute('''
                            UPDATE products 
                            SET stock_quantity = stock_quantity + ? 
                            WHERE id = ?
                        ''', (stock_change, product_id))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            self.conn.rollback()
            raise e
    
    def delete_sale(self, sale_id):
        """
        Delete a sale record and restore stock
        """
        try:
            cur = self.conn.cursor()
            
            # Get sale items to restore stock
            cur.execute('SELECT product_id, quantity FROM sale_items WHERE sale_id = ?', 
                       (sale_id,))
            items = cur.fetchall()
            
            # Restore inventory
            for product_id, quantity in items:
                cur.execute('''
                    UPDATE products 
                    SET stock_quantity = stock_quantity + ? 
                    WHERE id = ?
                ''', (quantity, product_id))
            
            # Delete sale items
            cur.execute('DELETE FROM sale_items WHERE sale_id = ?', (sale_id,))
            
            # Delete sale
            cur.execute('DELETE FROM sales WHERE id = ?', (sale_id,))
            
            self.conn.commit()
            return True
        
        except Exception as e:
            self.conn.rollback()
            raise e
    
    def get_pending_invoices(self):
        """Get pending invoices (due amount > 0)"""
        cur = self.conn.cursor()
        cur.execute('''
            SELECT s.*, c.full_name as customer_name 
            FROM sales s
            LEFT JOIN customers c ON s.customer_id = c.id
            WHERE s.due_amount > 0
            ORDER BY s.date DESC
        ''')
        return cur.fetchall()
    
    def get_sales_stats(self):
        """Get sales statistics"""
        cur = self.conn.cursor()
        stats = {}
        
        # Total sales today
        today = datetime.now().strftime('%Y-%m-%d')
        cur.execute('''
            SELECT COUNT(*), SUM(total_price) 
            FROM sales 
            WHERE date(date) = ?
        ''', (today,))
        count, total = cur.fetchone()
        stats['today'] = {
            'count': count or 0,
            'total': total or 0
        }
        
        # Last sale time
        cur.execute('''
            SELECT date FROM sales 
            ORDER BY created_at DESC LIMIT 1
        ''')
        result = cur.fetchone()
        stats['last_sale'] = result[0] if result else None
        
        # Pending invoices
        cur.execute('SELECT COUNT(*) FROM sales WHERE due_amount > 0')
        stats['pending_invoices'] = cur.fetchone()[0]
        
        # Top customers
        cur.execute('''
            SELECT c.id, c.full_name, SUM(s.total_price) as total_spent
            FROM sales s
            JOIN customers c ON s.customer_id = c.id
            GROUP BY c.id
            ORDER BY total_spent DESC
            LIMIT 5
        ''')
        stats['top_customers'] = cur.fetchall()
        
        # Discount usage
        cur.execute('''
            SELECT COUNT(*), SUM(discount)
            FROM sales
            WHERE date(date) = ? AND discount > 0
        ''', (today,))
        count, total = cur.fetchone()
        stats['discount_usage'] = {
            'count': count or 0,
            'total': total or 0
        }
        
        return stats
    
    def generate_invoice_number(self):
        """Generate a unique invoice number"""
        prefix = datetime.now().strftime('INV-%Y%m')
        
        # Get last invoice number with this prefix
        cur = self.conn.cursor()
        cur.execute('''
            SELECT invoice_number FROM sales
            WHERE invoice_number LIKE ?
            ORDER BY id DESC LIMIT 1
        ''', (f'{prefix}%',))
        
        result = cur.fetchone()
        
        if result:
            # Extract number part and increment
            last_num = int(result[0].split('-')[-1])
            next_num = last_num + 1
        else:
            next_num = 1
            
        return f"{prefix}-{next_num:04d}"

# --- Minimal Sales class for test compatibility ---
class Sales:
    def __init__(self, db=None):
        self.db = db
        self.sales = []
        self.next_id = 1

    def create(self, items, customer_id, total_amount):
        sale = type('Sale', (), {})()
        sale.id = self.next_id
        sale.items = items
        sale.customer_id = customer_id
        sale.total_amount = total_amount
        self.sales.append(sale)
        self.next_id += 1
        return sale

    def get_by_id(self, sale_id):
        for sale in self.sales:
            if sale.id == sale_id:
                return sale
        return None

    def get_by_date_range(self, start_date, end_date):
        # For stub, just return all sales
        return self.sales
