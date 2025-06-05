import firebase_admin
from firebase_admin import credentials, auth, db
import os
import random
from datetime import datetime, timedelta

# Path to your service account key
SERVICE_ACCOUNT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../config/firebase_key.json'))

# Initialize the Firebase app
if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://smart-shop-manager-9ba3a-default-rtdb.asia-southeast1.firebasedatabase.app'
    })

# Authentication functions (admin only, not client-side)
def register(email, password):
    try:
        user = auth.create_user(email=email, password=password)
        return user, None
    except Exception as e:
        return None, str(e)

def get_user_by_email(email):
    try:
        user = auth.get_user_by_email(email)
        return user
    except Exception as e:
        return None

def delete_user(uid):
    try:
        auth.delete_user(uid)
        return True
    except Exception as e:
        return False

def get_db():
    return db.reference('/')

def populate_dummy_data():
    db_ref = get_db()
    # Dummy inventory
    categories = ['Electronics', 'Clothing', 'Food & Beverages', 'Books']
    inventory = []
    for i in range(12):
        item = {
            'name': f'Product {i+1}',
            'category': random.choice(categories),
            'stock': random.randint(0, 50),
            'buying_price': random.randint(10, 200),
            'selling_price': random.randint(20, 300),
            'created_at': datetime.now().isoformat()
        }
        inventory.append(item)
    db_ref.child('inventory').set({f'item_{i+1}': item for i, item in enumerate(inventory)})
    # Dummy customers
    customers = []
    for i in range(10):
        cust = {
            'name': f'Customer {i+1}',
            'email': f'customer{i+1}@example.com',
            'joined': (datetime.now() - timedelta(days=random.randint(0, 365))).isoformat(),
            'total_spent': random.randint(100, 5000),
            'orders': random.randint(1, 20)
        }
        customers.append(cust)
    db_ref.child('customers').set({f'cust_{i+1}': cust for i, cust in enumerate(customers)})
    # Dummy sales
    sales = []
    for i in range(25):
        sale = {
            'product': random.choice(inventory)['name'],
            'customer': random.choice(customers)['name'],
            'amount': random.randint(20, 500),
            'date': (datetime.now() - timedelta(days=random.randint(0, 180))).isoformat(),
            'quantity': random.randint(1, 5)
        }
        sales.append(sale)
    db_ref.child('sales').set({f'sale_{i+1}': sale for i, sale in enumerate(sales)})
    print('Dummy data uploaded to Firebase!')

if __name__ == '__main__':
    populate_dummy_data()

# Note: firebase-admin does not support client-side login/logout (session management)
# Use get_user_by_email to look up users, and register to create users. 