import sqlite3

class PurchasesModel:
    def __init__(self, db_conn):
        self.conn = db_conn
        self.create_table()

    def create_table(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                product TEXT,
                quantity INTEGER,
                price REAL,
                total REAL,
                date TEXT,
                FOREIGN KEY(customer_id) REFERENCES customers(id)
            )
        ''')
        self.conn.commit()

    def add_purchase(self, customer_id, product, quantity, price, total, date):
        cur = self.conn.cursor()
        cur.execute('''
            INSERT INTO purchases (customer_id, product, quantity, price, total, date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (customer_id, product, quantity, price, total, date))
        self.conn.commit()
        return cur.lastrowid

    def get_all_purchases(self):
        cur = self.conn.cursor()
        cur.execute('''
            SELECT p.id, c.name, p.product, p.quantity, p.price, p.total, p.date
            FROM purchases p
            LEFT JOIN customers c ON p.customer_id = c.id
            ORDER BY p.date DESC
        ''')
        return cur.fetchall()

    def get_purchases_by_customer(self, customer_id):
        cur = self.conn.cursor()
        cur.execute('''
            SELECT p.id, c.name, p.product, p.quantity, p.price, p.total, p.date
            FROM purchases p
            LEFT JOIN customers c ON p.customer_id = c.id
            WHERE p.customer_id = ?
            ORDER BY p.date DESC
        ''', (customer_id,))
        return cur.fetchall() 