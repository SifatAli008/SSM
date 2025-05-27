import unittest
from datetime import datetime
from app.models.inventory import Inventory
from app.models.sales import Sales
from app.models.user import User
from app.models.customer import Customer
from app.utils.database import DatabaseManager

class TestInventoryModel(unittest.TestCase):
    def setUp(self):
        self.db = DatabaseManager()
        self.db.initialize(":memory:")
        self.model = Inventory(self.db)
        
    def test_create_product(self):
        """Test creating a new product"""
        product = self.model.create(
            name="Test Product",
            quantity=10,
            price=99.99,
            category="Test"
        )
        self.assertIsNotNone(product)
        self.assertEqual(product.name, "Test Product")
        self.assertEqual(product.quantity, 10)
        self.assertEqual(product.price, 99.99)
        
    def test_get_product(self):
        """Test retrieving a product"""
        # Create product first
        self.model.create("Test Product", 10, 99.99, "Test")
        
        # Get product
        product = self.model.get_by_name("Test Product")
        self.assertIsNotNone(product)
        self.assertEqual(product.name, "Test Product")
        
    def test_update_product(self):
        """Test updating a product"""
        # Create product first
        product = self.model.create("Test Product", 10, 99.99, "Test")
        
        # Update product
        updated = self.model.update(
            product.id,
            quantity=20,
            price=89.99
        )
        self.assertTrue(updated)
        
        # Verify update
        product = self.model.get_by_name("Test Product")
        self.assertEqual(product.quantity, 20)
        self.assertEqual(product.price, 89.99)

class TestSalesModel(unittest.TestCase):
    def setUp(self):
        self.db = DatabaseManager()
        self.db.initialize(":memory:")
        self.model = Sales(self.db)
        
    def test_create_sale(self):
        """Test creating a new sale"""
        sale = self.model.create(
            items=[{"product_id": 1, "quantity": 2, "price": 99.99}],
            customer_id=1,
            total_amount=199.98
        )
        self.assertIsNotNone(sale)
        self.assertEqual(sale.total_amount, 199.98)
        self.assertEqual(len(sale.items), 1)
        
    def test_get_sale(self):
        """Test retrieving a sale"""
        # Create sale first
        sale = self.model.create(
            items=[{"product_id": 1, "quantity": 1, "price": 99.99}],
            customer_id=1,
            total_amount=99.99
        )
        
        # Get sale
        retrieved = self.model.get_by_id(sale.id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.total_amount, 99.99)
        
    def test_get_sales_by_date(self):
        """Test getting sales by date range"""
        # Create some test sales
        self.model.create(
            items=[{"product_id": 1, "quantity": 1, "price": 99.99}],
            customer_id=1,
            total_amount=99.99
        )
        
        # Get sales for date range
        sales = self.model.get_by_date_range(
            start_date="2024-01-01",
            end_date="2024-12-31"
        )
        self.assertEqual(len(sales), 1)

class TestUserModel(unittest.TestCase):
    def setUp(self):
        self.db = DatabaseManager()
        self.db.initialize(":memory:")
        self.model = User(self.db)
        
    def test_create_user(self):
        """Test creating a new user"""
        user = self.model.create(
            username="testuser",
            password="testpass",
            role="admin"
        )
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.role, "admin")
        
    def test_get_user(self):
        """Test retrieving a user"""
        # Create user first
        self.model.create("testuser", "testpass", "admin")
        
        # Get user
        user = self.model.get_by_username("testuser")
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "testuser")
        
    def test_verify_password(self):
        """Test password verification"""
        # Create user first
        user = self.model.create("testuser", "testpass", "admin")
        
        # Verify password
        self.assertTrue(user.verify_password("testpass"))
        self.assertFalse(user.verify_password("wrongpass"))

class TestCustomerModel(unittest.TestCase):
    def setUp(self):
        self.db = DatabaseManager()
        self.db.initialize(":memory:")
        self.model = Customer(self.db)
        
    def test_create_customer(self):
        """Test creating a new customer"""
        customer = self.model.create(
            name="Test Customer",
            email="test@example.com",
            phone="1234567890"
        )
        self.assertIsNotNone(customer)
        self.assertEqual(customer.name, "Test Customer")
        self.assertEqual(customer.email, "test@example.com")
        
    def test_get_customer(self):
        """Test retrieving a customer"""
        # Create customer first
        self.model.create("Test Customer", "test@example.com", "1234567890")
        
        # Get customer
        customer = self.model.get_by_email("test@example.com")
        self.assertIsNotNone(customer)
        self.assertEqual(customer.name, "Test Customer")
        
    def test_update_customer(self):
        """Test updating a customer"""
        # Create customer first
        customer = self.model.create("Test Customer", "test@example.com", "1234567890")
        
        # Update customer
        updated = self.model.update(
            customer.id,
            phone="0987654321"
        )
        self.assertTrue(updated)
        
        # Verify update
        customer = self.model.get_by_email("test@example.com")
        self.assertEqual(customer.phone, "0987654321")

if __name__ == '__main__':
    unittest.main()
