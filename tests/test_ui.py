import unittest
from PyQt5.QtWidgets import QApplication, QMenu
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt, QDate
import sys
import os
from app.ui.main_window import MainWindow
from app.views.inventory_view import InventoryView
from app.views.sales_view import SalesView
from app.views.reports_view import ReportsView
from app.views.settings_view import SettingsView
from app.controllers.inventory_controller import InventoryController
from app.controllers.sales_controller import SalesController
from app.utils.database import DatabaseManager
from app.controllers.user_controller import UserController

class TestMainWindow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication(sys.argv)
        
    def setUp(self):
        self.db = DatabaseManager()
        self.db.initialize(":memory:")
        self.main_window = MainWindow()
        
    def test_window_title(self):
        """Test that window title is set correctly"""
        self.assertEqual(self.main_window.windowTitle(), "Smart Shop Manager")
        
    def test_menu_bar(self):
        """Test that menu bar contains all required menus"""
        menu_bar = self.main_window.menuBar()
        menus = [menu.title() for menu in menu_bar.findChildren(QMenu)]
        required_menus = ["File", "Edit", "View", "Help"]
        for menu in required_menus:
            self.assertIn(menu, menus)
            
    def test_status_bar(self):
        """Test that status bar is present and shows correct message"""
        self.assertIsNotNone(self.main_window.statusBar())
        self.main_window.statusBar().showMessage("Ready")
        self.assertEqual(self.main_window.statusBar().currentMessage(), "Ready")

class TestInventoryView(unittest.TestCase):
    def setUp(self):
        self.db = DatabaseManager()
        self.db.initialize(":memory:")
        self.controller = InventoryController(self.db)
        self.view = InventoryView(self.controller)
        
    def test_add_product_form(self):
        """Test adding a product through the UI"""
        # Fill in the form
        self.view.name_input.setText("Test Product")
        self.view.quantity_input.setValue(10)
        self.view.price_input.setValue(99.99)
        self.view.category_input.setText("Test")
        
        # Click add button
        QTest.mouseClick(self.view.add_button, Qt.LeftButton)
        
        # Verify product was added
        products = self.controller.get_all_products()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].name, "Test Product")
        
    def test_search_functionality(self):
        """Test product search functionality"""
        # Add a test product
        self.controller.add_product("Test Product", 10, 99.99, "Test")
        
        # Search for the product
        self.view.search_input.setText("Test")
        QTest.keyClick(self.view.search_input, Qt.Key_Return)
        
        # Verify search results
        self.assertEqual(self.view.product_table.rowCount(), 1)
        
    def test_edit_product(self):
        """Test editing a product through the UI"""
        # Add a test product
        self.controller.add_product("Test Product", 10, 99.99, "Test")
        
        # Select the product in the table
        self.view.product_table.selectRow(0)
        
        # Click edit button
        QTest.mouseClick(self.view.edit_button, Qt.LeftButton)
        
        # Update the form
        self.view.name_input.setText("Updated Product")
        self.view.quantity_input.setValue(20)
        
        # Save changes
        QTest.mouseClick(self.view.save_button, Qt.LeftButton)
        
        # Verify changes
        product = self.controller.get_product("Updated Product")
        self.assertIsNotNone(product)
        self.assertEqual(product.quantity, 20)

class TestSalesView(unittest.TestCase):
    def setUp(self):
        self.db = DatabaseManager()
        self.db.initialize(":memory:")
        self.controller = SalesController(self.db)
        self.view = SalesView(self.controller)
        
    def test_create_sale(self):
        """Test creating a new sale through the UI"""
        # Add a test product
        self.controller.inventory_controller.add_product("Test Product", 10, 99.99, "Test")
        
        # Add product to sale
        self.view.product_search.setText("Test Product")
        QTest.keyClick(self.view.product_search, Qt.Key_Return)
        self.view.quantity_input.setValue(2)
        QTest.mouseClick(self.view.add_to_sale_button, Qt.LeftButton)
        
        # Complete sale
        QTest.mouseClick(self.view.complete_sale_button, Qt.LeftButton)
        
        # Verify sale was created
        sales = self.controller.get_sales_by_date_range("2024-01-01", "2024-12-31")
        self.assertEqual(len(sales), 1)
        self.assertEqual(sales[0].total_amount, 199.98)
        
    def test_customer_selection(self):
        """Test customer selection in sales view"""
        # Add a test customer
        self.controller.customer_controller.create_customer(
            name="Test Customer",
            email="test@example.com",
            phone="1234567890"
        )
        
        # Search for customer
        self.view.customer_search.setText("Test Customer")
        QTest.keyClick(self.view.customer_search, Qt.Key_Return)
        
        # Verify customer was selected
        self.assertEqual(self.view.selected_customer.name, "Test Customer")

class TestReportsView(unittest.TestCase):
    def setUp(self):
        self.db = DatabaseManager()
        self.db.initialize(":memory:")
        self.view = ReportsView()
        
    def test_date_range_selection(self):
        """Test date range selection for reports"""
        # Set date range
        self.view.start_date.setDate(QDate(2024, 1, 1))
        self.view.end_date.setDate(QDate(2024, 12, 31))
        
        # Generate report
        QTest.mouseClick(self.view.generate_button, Qt.LeftButton)
        
        # Verify report was generated
        self.assertIsNotNone(self.view.current_report)
        
    def test_report_export(self):
        """Test exporting reports"""
        # Generate a report
        self.view.start_date.setDate(QDate(2024, 1, 1))
        self.view.end_date.setDate(QDate(2024, 12, 31))
        QTest.mouseClick(self.view.generate_button, Qt.LeftButton)
        
        # Export report
        QTest.mouseClick(self.view.export_button, Qt.LeftButton)
        
        # Verify export file exists
        self.assertTrue(os.path.exists("reports/sales_report_2024.pdf"))

class TestSettingsView(unittest.TestCase):
    def setUp(self):
        self.db = DatabaseManager()
        self.db.initialize(":memory:")
        self.controller = UserController(self.db)
        self.view = SettingsView(self.controller)
        
    def test_user_creation(self):
        """Test creating a new user through the UI"""
        # Fill in the form
        self.view.username_input.setText("testuser")
        self.view.password_input.setText("testpass")
        self.view.role_combo.setCurrentText("admin")
        
        # Create user
        QTest.mouseClick(self.view.create_user_button, Qt.LeftButton)
        
        # Verify user was created
        user = self.controller.get_user("testuser")
        self.assertIsNotNone(user)
        self.assertEqual(user.role, "admin")
        
    def test_settings_save(self):
        """Test saving application settings"""
        # Change settings
        self.view.theme_combo.setCurrentText("Dark")
        self.view.language_combo.setCurrentText("English")
        
        # Save settings
        QTest.mouseClick(self.view.save_settings_button, Qt.LeftButton)
        
        # Verify settings were saved
        self.assertEqual(self.view.current_theme, "Dark")
        self.assertEqual(self.view.current_language, "English")

if __name__ == '__main__':
    unittest.main() 