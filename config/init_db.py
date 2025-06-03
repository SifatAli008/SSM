import os
from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import random
import sys

# Import all SQLAlchemy models
sys.path.append(str(Path(__file__).resolve().parent.parent))
from app.models.base import Base, User, Product, Sale, SaleItem, Category

DB_PATH = os.path.join(Path(__file__).resolve().parent.parent, "data", "shop.db")

# Ensure data directory exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

engine = create_engine(f"sqlite:///{DB_PATH}")
Session = sessionmaker(bind=engine)

def create_db():
    # Drop and recreate all tables
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print(f"✅ Database tables created at {DB_PATH}")
    add_sample_data()

def add_sample_data():
    session = Session()
    try:
        # Add sample categories
        cat1 = Category(name="Electronics", description="Electronic items")
        cat2 = Category(name="Books", description="Books and magazines")
        session.add_all([cat1, cat2])
        session.commit()
        # Add sample products
        prod1 = Product(name="Smartphone X1", description="Latest model with 128GB storage", category="Electronics", sku="SPX1-128", price=599.99, cost=400.0, stock=25, min_stock=10)
        prod2 = Product(name="Laptop Pro", description="15-inch, 16GB RAM, 512GB SSD", category="Electronics", sku="LP15-512", price=1299.99, cost=800.0, stock=10, min_stock=5)
        prod3 = Product(name="Wireless Earbuds", description="Noise cancelling, 24hr battery", category="Electronics", sku="WE-24", price=129.99, cost=80.0, stock=50, min_stock=20)
        session.add_all([prod1, prod2, prod3])
        session.commit()
        # Add sample users
        user1 = User(username="admin", email="admin@example.com", password_hash="adminPass123", is_admin=True)
        user2 = User(username="manager", email="manager@example.com", password_hash="managerPass123", is_admin=False)
        session.add_all([user1, user2])
        session.commit()
        print("✅ Added sample categories, products, and users")
        # Add sample sales
        sale1 = Sale(user_id=user1.id, total_amount=599.99, payment_method="Cash", status="completed")
        session.add(sale1)
        session.commit()
        sale_item1 = SaleItem(sale_id=sale1.id, product_id=prod1.id, quantity=1, price=599.99)
        session.add(sale_item1)
        session.commit()
        print("✅ Added sample sales and sale items")
    except Exception as e:
        print(f"❌ Error adding sample data: {e}")
        session.rollback()
        raise
    finally:
        session.close()

def open_database_connection():
    try:
        session = Session()
        print(f"Database connection successful at {DB_PATH}")
        return session
    except Exception as e:
        print(f"Error opening database: {e}")
        return None

if __name__ == "__main__":
    create_db()
    # Check connection
    session = open_database_connection()
    if session:
        print("Database is open and ready to use!")
        session.close()
    else:
        print("Failed to open database!")    