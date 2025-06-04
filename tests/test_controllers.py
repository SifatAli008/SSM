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
from app.data.data_provider import BaseDataProvider

class MockDataProvider(BaseDataProvider):
    def __init__(self):
        self.products = []
        self.sales = []
        self.next_product_id = 1
    def get_products(self):
        return self.products
    def add_product(self, product_data):
        # Check for duplicate
        for p in self.products:
            if p['name'] == product_data['name']:
                return False
        if product_data.get('quantity', 0) < 0 or product_data.get('price', 0) < 0:
            return False
        product_data = dict(product_data)  # Copy
        product_data['product_id'] = self.next_product_id
        self.next_product_id += 1
        self.products.append(product_data)
        return product_data['product_id']
    def get_product_by_id(self, product_id):
        for p in self.products:
            if p['product_id'] == product_id:
                return p
        return None
    def get_sales(self):
        return self.sales
    def add_sale(self, sale_data):
        # Decrement stock for each item
        for item in sale_data.get('items', []):
            prod = self.get_product_by_id(item['product_id'])
            if not prod:
                raise Exception(f"Product with id {item['product_id']} does not exist.")
            if item['quantity'] > prod.get('quantity', 0):
                raise Exception(f"Insufficient stock for product id {item['product_id']}")
            prod['quantity'] -= item['quantity']
        self.sales.append(sale_data)
        return True

class TestInventoryController(unittest.TestCase):
    def setUp(self):
        self.data_provider = MockDataProvider()
        self.controller = InventoryController(self.data_provider)
        
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
        self.assertEqual(product['name'], "Test Product")
        self.assertEqual(product['quantity'], 10)
        self.assertEqual(product['price'], 99.99)
        
    def test_update_product(self):
        """Test updating an existing product"""
        # Add product first
        self.controller.add_product(name="Test Product", quantity=10, price=99.99, category="Test")
        
        # Update product
        result = self.controller.update_product(
            name="Test Product",
            quantity=20,
            price=89.99
        )
        self.assertTrue(result)
        
        # Verify update
        product = self.controller.get_product("Test Product")
        self.assertEqual(product['quantity'], 20)
        self.assertEqual(product['price'], 89.99)
        
    def test_delete_product(self):
        """Test deleting a product"""
        # Add product first
        self.controller.add_product(name="Test Product", quantity=10, price=99.99, category="Test")
        
        # Delete product
        result = self.controller.delete_product("Test Product")
        self.assertTrue(result)
        
        # Verify deletion
        product = self.controller.get_product("Test Product")
        self.assertIsNone(product)

class TestSalesController(unittest.TestCase):
    def setUp(self):
        self.data_provider = MockDataProvider()
        self.controller = SalesController(self.data_provider)
        self.controller.inventory_controller = InventoryController(self.data_provider)
        
    def test_create_sale(self):
        """Test creating a new sale"""
        # Add a product and get its product_id
        prod_id = self.data_provider.add_product({
            'name': 'Test Product',
            'quantity': 10,
            'price': 99.99,
            'category': 'Test'
        })
        result = self.controller.create_sale(
            items=[{"product_id": prod_id, "quantity": 2, "price": 99.99}],
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

    def test_create_sale_with_empty_cart(self):
        """Test creating a sale with an empty cart (should fail)"""
        with self.assertRaises(Exception):
            self.controller.create_sale(items=[], customer_id=1, total_amount=0)

    def test_add_product_with_insufficient_stock(self):
        """Test adding a product to sale with insufficient stock (should fail)"""
        self.controller.inventory_controller.add_product(name="Test Product", quantity=1, price=10, category="Test")
        # Try to create sale with quantity greater than stock
        with self.assertRaises(Exception):
            self.controller.create_sale(items=[{"product_id": 1, "quantity": 5, "price": 10}], customer_id=1, total_amount=50)

    def test_add_duplicate_product(self):
        """Test adding a duplicate product (should fail)"""
        self.controller.inventory_controller.add_product(name="Test Product", quantity=10, price=10, category="Test")
        result = self.controller.inventory_controller.add_product(name="Test Product", quantity=5, price=10, category="Test")
        self.assertFalse(result)

    def test_add_product_with_invalid_data(self):
        """Test adding a product with invalid data (negative price/quantity)"""
        result1 = self.controller.inventory_controller.add_product(name="Invalid Product", quantity=-5, price=10, category="Test")
        result2 = self.controller.inventory_controller.add_product(name="Invalid Product", quantity=5, price=-10, category="Test")
        self.assertFalse(result1)
        self.assertFalse(result2)

    @patch('app.models.inventory.Inventory.add_product', side_effect=Exception("DB error"))
    def test_add_product_db_failure(self, mock_add):
        """Test DB failure on add_product (should show error)"""
        with self.assertRaises(Exception):
            self.controller.inventory_controller.add_product(name="DBFail", quantity=1, price=1, category="Test")

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

    def test_generate_sales_report_empty_data(self):
        """Test generating sales report with no sales data"""
        # Clear sales data if possible
        if hasattr(self.controller, 'clear_sales'):
            self.controller.clear_sales()
        report = self.controller.generate_sales_report(
            start_date="1990-01-01",
            end_date="1990-12-31"
        )
        self.assertIsNotNone(report)
        self.assertEqual(report.get("total_sales", 0), 0)

    def test_generate_sales_report_invalid_dates(self):
        """Test generating sales report with invalid date range"""
        with self.assertRaises(Exception):
            self.controller.generate_sales_report(
                start_date="2024-12-31",
                end_date="2024-01-01"
            )

if __name__ == '__main__':
    unittest.main()
