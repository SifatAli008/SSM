# File: views/main_window.py

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QStackedWidget, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from controllers.inventory_controller import InventoryController
from views.dashboard_view import DashboardPage  # Dashboard page class


class MainWindow(QMainWindow):
    logout_requested = pyqtSignal()

    def __init__(self, user):
        super().__init__()
        self.current_user = user
        self.inventory_controller = InventoryController()
        self.nav_buttons = []

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Smart Shop Manager')
        self.setMinimumSize(1000, 600)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar, 1)

        # Content area
        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack, 4)

        # Add content pages
        self.add_dashboard_page()
        self.add_inventory_page()
        self.add_sales_page()
        self.add_customers_page()
        self.add_suppliers_page()
        self.add_reports_page()

        # Default page
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
                padding: 12px;
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

        layout = QVBoxLayout(sidebar_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Title
        title = QLabel("Smart Shop\nManager")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("padding: 20px; color: white;")
        layout.addWidget(title)

        # Nav buttons
        self.create_nav_button(layout, "Dashboard", 0)
        self.create_nav_button(layout, "Inventory", 1)
        self.create_nav_button(layout, "Sales", 2)
        self.create_nav_button(layout, "Customers", 3)
        self.create_nav_button(layout, "Suppliers", 4)
        self.create_nav_button(layout, "Reports", 5)

        layout.addStretch()

        # User info
        user_info = QFrame()
        user_layout = QVBoxLayout(user_info)
        user_name = QLabel(f"{self.current_user.full_name}")
        user_role = QLabel(f"Role: {self.current_user.role.capitalize()}")

        user_name.setStyleSheet("color: white; font-weight: bold;")
        user_role.setStyleSheet("color: #bdc3c7; font-size: 12px;")

        user_layout.addWidget(user_name)
        user_layout.addWidget(user_role)
        layout.addWidget(user_info)

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
        logout_btn.clicked.connect(self.logout)
        layout.addWidget(logout_btn)

        return sidebar_widget

    def create_nav_button(self, layout, text, page_index):
        button = QPushButton(text)
        button.setCheckable(True)
        button.clicked.connect(lambda: self.change_page(page_index))
        layout.addWidget(button)
        self.nav_buttons.append(button)

        if page_index == 0:
            button.setChecked(True)

    def change_page(self, index):
        for btn in self.nav_buttons:
            btn.setChecked(False)

        sender = self.sender()
        if sender:
            sender.setChecked(True)

        self.content_stack.setCurrentIndex(index)

    def add_dashboard_page(self):
        dashboard = DashboardPage()
        self.content_stack.addWidget(dashboard)

    def add_inventory_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        title = QLabel("Inventory Management")
        title.setFont(QFont("Arial", 24))
        layout.addWidget(title)
        layout.addWidget(QLabel("Inventory tools will be here..."))
        self.content_stack.addWidget(page)

    def add_sales_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        title = QLabel("Sales & Billing")
        title.setFont(QFont("Arial", 24))
        layout.addWidget(title)
        layout.addWidget(QLabel("Sales interface goes here..."))
        self.content_stack.addWidget(page)

    def add_customers_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        title = QLabel("Customer Management")
        title.setFont(QFont("Arial", 24))
        layout.addWidget(title)
        layout.addWidget(QLabel("Customer records shown here..."))
        self.content_stack.addWidget(page)

    def add_suppliers_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        title = QLabel("Supplier Management")
        title.setFont(QFont("Arial", 24))
        layout.addWidget(title)
        layout.addWidget(QLabel("Supplier list will be added here..."))
        self.content_stack.addWidget(page)

    def add_reports_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        title = QLabel("Reports & Analytics")
        title.setFont(QFont("Arial", 24))
        layout.addWidget(title)
        layout.addWidget(QLabel("Reports dashboard coming soon..."))
        self.content_stack.addWidget(page)

    def logout(self):
        print("Logout clicked!")
        self.logout_requested.emit()
        self.close()
