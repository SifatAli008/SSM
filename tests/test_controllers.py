import unittest
from unittest.mock import Mock, patch
from app.controllers.inventory_controller import InventoryController
from app.controllers.sales_controller import SalesController
from app.controllers.user_controller import UserController
from app.controllers.report_controller import ReportController
from app.models.inventory import Inventory
from app.models.sales import Sales
from app.models.user import User
from app.utils.database import DatabaseManager

class TestInventoryController(unittest.TestCase):
    def setUp(self):
        self.db = DatabaseManager()
        self.db.initialize(":memory:")
        self.controller = InventoryController(self.db)
        
    def test_add_product(self):
        """Test adding a new product"""
        result = self.controller.add_product(
            name="Test Product",
            quantity=10,
            price=99.99,
            category="Test"
        )
        self.assertTrue(result)
        
        # Verify product was added
        product = self.controller.get_product("Test Product")
        self.assertEqual(product.name, "Test Product")
        self.assertEqual(product.quantity, 10)
        self.assertEqual(product.price, 99.99)
        
    def test_update_product(self):
        """Test updating an existing product"""
        # Add product first
        self.controller.add_product("Test Product", 10, 99.99, "Test")
        
        # Update product
        result = self.controller.update_product(
            name="Test Product",
            quantity=20,
            price=89.99
        )
        self.assertTrue(result)
        
        # Verify update
        product = self.controller.get_product("Test Product")
        self.assertEqual(product.quantity, 20)
        self.assertEqual(product.price, 89.99)
        
    def test_delete_product(self):
        """Test deleting a product"""
        # Add product first
        self.controller.add_product("Test Product", 10, 99.99, "Test")
        
        # Delete product
        result = self.controller.delete_product("Test Product")
        self.assertTrue(result)
        
        # Verify deletion
        product = self.controller.get_product("Test Product")
        self.assertIsNone(product)

class TestSalesController(unittest.TestCase):
    def setUp(self):
        self.db = DatabaseManager()
        self.db.initialize(":memory:")
        self.controller = SalesController(self.db)
        
    def test_create_sale(self):
        """Test creating a new sale"""
        result = self.controller.create_sale(
            items=[{"product_id": 1, "quantity": 2, "price": 99.99}],
            customer_id=1,
            total_amount=199.98
        )
        self.assertTrue(result)
        
        # Verify sale was created
        sale = self.controller.get_sale(result)
        self.assertEqual(sale.total_amount, 199.98)
        self.assertEqual(len(sale.items), 1)
        
    def test_get_sales_by_date(self):
        """Test getting sales by date range"""
        # Create some test sales
        self.controller.create_sale(
            items=[{"product_id": 1, "quantity": 1, "price": 99.99}],
            customer_id=1,
            total_amount=99.99
        )
        
        # Get sales for today
        sales = self.controller.get_sales_by_date_range(
            start_date="2024-01-01",
            end_date="2024-12-31"
        )
        self.assertEqual(len(sales), 1)

class TestUserController(unittest.TestCase):
    def setUp(self):
        self.db = DatabaseManager()
        self.db.initialize(":memory:")
        self.controller = UserController(self.db)
        
    def test_create_user(self):
        """Test creating a new user"""
        result = self.controller.create_user(
            username="testuser",
            password="testpass",
            role="admin"
        )
        self.assertTrue(result)
        
        # Verify user was created
        user = self.controller.get_user("testuser")
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.role, "admin")
        
    def test_authenticate_user(self):
        """Test user authentication"""
        # Create user first
        self.controller.create_user("testuser", "testpass", "admin")
        
        # Test authentication
        result = self.controller.authenticate("testuser", "testpass")
        self.assertTrue(result)
        
        # Test wrong password
        result = self.controller.authenticate("testuser", "wrongpass")
        self.assertFalse(result)

class TestReportController(unittest.TestCase):
    def setUp(self):
        self.db = DatabaseManager()
        self.db.initialize(":memory:")
        self.controller = ReportController(self.db)
        
    def test_generate_sales_report(self):
        """Test generating sales report"""
        report = self.controller.generate_sales_report(
            start_date="2024-01-01",
            end_date="2024-12-31"
        )
        self.assertIsNotNone(report)
        self.assertIn("total_sales", report)
        self.assertIn("sales_by_date", report)
        
    def test_generate_inventory_report(self):
        """Test generating inventory report"""
        report = self.controller.generate_inventory_report()
        self.assertIsNotNone(report)
        self.assertIn("total_items", report)
        self.assertIn("low_stock_items", report)

if __name__ == '__main__':
    unittest.main()
