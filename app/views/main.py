from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QStackedWidget, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

from controllers.inventory_controller import InventoryController
from models.users import User

class MainWindow(QMainWindow):
    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user
        self.inventory_controller = InventoryController()
        
        self.init_ui()
        
    def init_ui(self):
        # Set window properties
        self.setWindowTitle('Smart Shop Manager')
        self.setMinimumSize(1000, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar, 1)
        
        # Create main content area
        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack, 4)
        
        # Add pages to stack
        self.add_dashboard_page()
        self.add_inventory_page()
        self.add_sales_page()
        self.add_customers_page()
        self.add_suppliers_page()
        self.add_reports_page()
        
        # Show dashboard by default
        self.content_stack.setCurrentIndex(0)
        
    def create_sidebar(self):
        sidebar_widget = QWidget()
        sidebar_widget.setObjectName("sidebar")
        sidebar_widget.setStyleSheet("""
            #sidebar {
                background-color: #2c3e50;
                color: white;
            }
            QPushButton {
                color: white;
                border: none;
                text-align: left;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
            QPushButton:checked {
                background-color: #3498db;
                font-weight: bold;
            }
        """)
        
        sidebar_layout = QVBoxLayout(sidebar_widget)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # Logo/Title area
        title_label = QLabel("Smart Shop\nManager")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("padding: 20px; color: white;")
        sidebar_layout.addWidget(title_label)
        
        # Navigation buttons
        self.create_nav_button(sidebar_layout, "Dashboard", 0)
        self.create_nav_button(sidebar_layout, "Inventory", 1)
        self.create_nav_button(sidebar_layout, "Sales", 2)
        self.create_nav_button(sidebar_layout, "Customers", 3)
        self.create_nav_button(sidebar_layout, "Suppliers", 4)
        self.create_nav_button(sidebar_layout, "Reports", 5)
        
        # Add spacer to push user info to bottom
        sidebar_layout.addStretch()
        
        # User info
        user_frame = QFrame()
        user_layout = QVBoxLayout(user_frame)
        
        user_name = QLabel(f"{self.current_user.full_name}")
        user_name.setStyleSheet("color: white; font-weight: bold;")
        user_role = QLabel(f"Role: {self.current_user.role.capitalize()}")
        user_role.setStyleSheet("color: #bdc3c7; font-size: 12px;")
        
        user_layout.addWidget(user_name)
        user_layout.addWidget(user_role)
        
        sidebar_layout.addWidget(user_frame)
        
        # Logout button
        logout_btn = QPushButton("Logout")
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                margin: 10px;
                border-radius: 5px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        # Connect logout button to function
        logout_btn.clicked.connect(self.logout)
        
        sidebar_layout.addWidget(logout_btn)
        
        return sidebar_widget
    
    def create_nav_button(self, layout, text, page_index):
        button = QPushButton(text)
        button.setCheckable(True)
        button.clicked.connect(lambda: self.change_page(page_index))
        
        # Set the first button as checked by default
        if page_index == 0:
            button.setChecked(True)
            
        layout.addWidget(button)
        return button
    
    def change_page(self, index):
        # Uncheck all nav buttons
        for i in range(self.layout().itemAt(0).widget().layout().count()):
            item = self.layout().itemAt(0).widget().layout().itemAt(i)
            if item.widget() and isinstance(item.widget(), QPushButton):
                item.widget().setChecked(False)
        
        # Check the selected button
        sender = self.sender()
        if sender:
            sender.setChecked(True)
            
        # Change the page
        self.content_stack.setCurrentIndex(index)
    
    def add_dashboard_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        title = QLabel("Dashboard")
        title.setFont(QFont("Arial", 24))
        layout.addWidget(title)
        
        # Add dashboard widgets here
        layout.addWidget(QLabel("Welcome to Smart Shop Manager!"))
        
        self.content_stack.addWidget(page)
    
    def add_inventory_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        title = QLabel("Inventory Management")
        title.setFont(QFont("Arial", 24))
        layout.addWidget(title)
        
        # Add inventory widgets here
        
        self.content_stack.addWidget(page)
    
    def add_sales_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        title = QLabel("Sales & Billing")
        title.setFont(QFont("Arial", 24))
        layout.addWidget(title)
        
        # Add sales widgets here
        
        self.content_stack.addWidget(page)
    
    def add_customers_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        title = QLabel("Customer Management")
        title.setFont(QFont("Arial", 24))
        layout.addWidget(title)
        
        # Add customer widgets here
        
        self.content_stack.addWidget(page)
    
    def add_suppliers_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        title = QLabel("Supplier Management")
        title.setFont(QFont("Arial", 24))
        layout.addWidget(title)
        
        # Add supplier widgets here
        
        self.content_stack.addWidget(page)
    
    def add_reports_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        title = QLabel("Reports & Analytics")
        title.setFont(QFont("Arial", 24))
        layout.addWidget(title)
        
        # Add reports widgets here
        
        self.content_stack.addWidget(page)
    
    def logout(self):
        # TODO: Implement logout functionality
        # Close main window and show login window
        pass