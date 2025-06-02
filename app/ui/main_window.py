from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget, QMenuBar, QMenu
from PyQt5.QtCore import Qt
from app.utils.logger import logger
from app.core.auth import AuthManager
from app.core.event_system import EventSystem
from app.core.backup import BackupManager
from app.core.reports import ReportManager
from app.core.inventory import InventoryManager
from app.core.sales import SalesManager
from app.core.users import UserManager

class DummyEventSystem:
    def subscribe(self, event, handler):
        pass

class MainWindow(QMainWindow):
    def __init__(self, auth_manager=None, event_system=None, backup_manager=None, report_manager=None, inventory_manager=None, sales_manager=None, user_manager=None):
        super().__init__()
        self.setWindowTitle("Smart Shop Manager")
        self.auth_manager = auth_manager
        self.event_system = event_system or DummyEventSystem()
        self.backup_manager = backup_manager
        self.report_manager = report_manager
        self.inventory_manager = inventory_manager
        self.sales_manager = sales_manager
        self.user_manager = user_manager
        
        menubar = QMenuBar(self)
        self.setMenuBar(menubar)
        self.menus = {}
        for menu_name in ["File", "Edit", "View", "Help"]:
            menu = QMenu(menu_name, menubar)
            menubar.addMenu(menu)
            self.menus[menu_name] = menu
        
        self.setup_ui()
        self.setup_event_handlers()
    
    def setup_ui(self):
        """Set up the main window UI."""
        self.setMinimumSize(1024, 768)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Add tabs
        self.setup_dashboard_tab(tab_widget)
        self.setup_sales_tab(tab_widget)
        self.setup_inventory_tab(tab_widget)
        self.setup_reports_tab(tab_widget)
        self.setup_users_tab(tab_widget)
        self.setup_settings_tab(tab_widget)
        
        logger.info("Main window UI setup completed")
    
    def setup_dashboard_tab(self, tab_widget: QTabWidget):
        """Set up the dashboard tab."""
        dashboard_widget = QWidget()
        layout = QVBoxLayout(dashboard_widget)
        
        # Add dashboard widgets here
        
        tab_widget.addTab(dashboard_widget, "Dashboard")
    
    def setup_sales_tab(self, tab_widget: QTabWidget):
        """Set up the sales tab."""
        sales_widget = QWidget()
        layout = QVBoxLayout(sales_widget)
        
        # Add sales widgets here
        
        tab_widget.addTab(sales_widget, "Sales")
    
    def setup_inventory_tab(self, tab_widget: QTabWidget):
        """Set up the inventory tab."""
        inventory_widget = QWidget()
        layout = QVBoxLayout(inventory_widget)
        
        # Add inventory widgets here
        
        tab_widget.addTab(inventory_widget, "Inventory")
    
    def setup_reports_tab(self, tab_widget: QTabWidget):
        """Set up the reports tab."""
        reports_widget = QWidget()
        layout = QVBoxLayout(reports_widget)
        
        # Add reports widgets here
        
        tab_widget.addTab(reports_widget, "Reports")
    
    def setup_users_tab(self, tab_widget: QTabWidget):
        """Set up the users tab."""
        users_widget = QWidget()
        layout = QVBoxLayout(users_widget)
        
        # Add users widgets here
        
        tab_widget.addTab(users_widget, "Users")
    
    def setup_settings_tab(self, tab_widget: QTabWidget):
        """Set up the settings tab."""
        settings_widget = QWidget()
        layout = QVBoxLayout(settings_widget)
        
        # Add settings widgets here
        
        tab_widget.addTab(settings_widget, "Settings")
    
    def setup_event_handlers(self):
        """Set up event handlers."""
        # Subscribe to relevant events
        self.event_system.subscribe("user.login", self.handle_user_login)
        self.event_system.subscribe("user.logout", self.handle_user_logout)
        self.event_system.subscribe("sale.created", self.handle_sale_created)
        self.event_system.subscribe("product.low_stock", self.handle_low_stock)
        
        logger.info("Event handlers setup completed")
    
    def handle_user_login(self, data: dict):
        """Handle user login event."""
        logger.info(f"User logged in: {data.get('username')}")
        # Update UI accordingly
    
    def handle_user_logout(self, data: dict):
        """Handle user logout event."""
        logger.info(f"User logged out: {data.get('username')}")
        # Update UI accordingly
    
    def handle_sale_created(self, data: dict):
        """Handle sale created event."""
        logger.info(f"Sale created: {data.get('sale_id')}")
        # Update UI accordingly
    
    def handle_low_stock(self, data: dict):
        """Handle low stock event."""
        logger.warning(f"Low stock alert: {data.get('product_name')}")
        # Update UI accordingly
    
    def closeEvent(self, event):
        """Handle window close event."""
        logger.info("Main window closing")
        # Perform cleanup
        event.accept() 