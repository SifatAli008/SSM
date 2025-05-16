import sqlite3

class CustomersModel:
    def __init__(self, db_conn):
        self.conn = db_conn
        self.create_table()

    def create_table(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                contact TEXT,
                address TEXT,
                history TEXT,
                created_at TEXT
            )
        ''')
        self.conn.commit()

    def add_customer(self, name, contact, address, history, created_at):
        cur = self.conn.cursor()
        cur.execute('''
            INSERT INTO customers (name, contact, address, history, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, contact, address, history, created_at))
        self.conn.commit()
        return cur.lastrowid

    def get_customers(self, search=None):
        cur = self.conn.cursor()
        if search:
            cur.execute('''SELECT * FROM customers WHERE name LIKE ? OR contact LIKE ? ORDER BY created_at DESC''', (f'%{search}%', f'%{search}%'))
        else:
            cur.execute('''SELECT * FROM customers ORDER BY created_at DESC''')
        return cur.fetchall()

    def update_customer(self, customer_id, **kwargs):
        fields = ', '.join([f'{k}=?' for k in kwargs])
        values = list(kwargs.values())
        values.append(customer_id)
        self.conn.execute(f'''UPDATE customers SET {fields} WHERE id=?''', values)
        self.conn.commit()

    def delete_customer(self, customer_id):
        self.conn.execute('''DELETE FROM customers WHERE id=?''', (customer_id,))
        self.conn.commit()
