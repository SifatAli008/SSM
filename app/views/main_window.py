from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QStackedWidget, QFrame, QSpacerItem,
    QSizePolicy, QGraphicsDropShadowEffect, QToolButton, QScrollBar, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QDateTime, QPropertyAnimation, QEasingCurve, QSize
from PyQt5.QtGui import QFont, QIcon, QColor


from controllers.inventory_controller import InventoryController
from views.dashboard_view import DashboardPage
from views.inventory_view import InventoryView




class AlertWidget(QWidget):
    """Enhanced alert widget with dismiss button and animations"""
    closed = pyqtSignal()
   
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(0)
        self.target_height = 40
       
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(15, 5, 15, 5)
       
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(16, 16)
        self.layout.addWidget(self.icon_label)
       
        self.message_label = QLabel()
        self.message_label.setFont(QFont("Segoe UI", 11))
        self.message_label.setWordWrap(True)
        self.layout.addWidget(self.message_label, 1)
       
        self.close_btn = QToolButton()
        self.close_btn.setText("✕")
        self.close_btn.setStyleSheet("background: transparent; border: none; color: white; font-size: 12px;")
        self.close_btn.clicked.connect(self.hide_alert)
        self.layout.addWidget(self.close_btn)
       
        self.auto_hide_timer = QTimer(self)
        self.auto_hide_timer.timeout.connect(self.hide_alert)
       
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
       
        # Set default style
        self.setStyleSheet("""
            background-color: #3498db;
            color: white;
            border-radius: 4px;
        """)
        self.message_label.setStyleSheet("color: white;")
   
    def show_alert(self, message, level="info"):
        icons = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌"
        }
       
        # Stop any ongoing animations/timers
        self.auto_hide_timer.stop()
       
        # Set content
        self.icon_label.setText(icons.get(level, "ℹ️"))
        self.message_label.setText(message)
        self.message_label.setFont(QFont("Segoe UI", 12))
       
        # Set alert styling based on level
        colors = {
            "info": "#3498db",
            "success": "#2ecc71",
            "warning": "#f39c12",
            "error": "#e74c3c"
        }
       
        self.setStyleSheet(f"""
            background-color: {colors.get(level, "#3498db")};
            color: white;
            border-radius: 4px;
            font-size: 12px;
        """)
       
        # Animate display
        self.setFixedHeight(0)
        self.show()
        self.animation = QPropertyAnimation(self, b"maximumHeight")
        self.animation.setDuration(250)
        self.animation.setStartValue(0)
        self.animation.setEndValue(self.target_height)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.start()
       
        # Auto-hide after 5 seconds for non-error alerts
        if level != "error":
            self.auto_hide_timer.start(5000)
   
    def hide_alert(self):
        self.animation = QPropertyAnimation(self, b"maximumHeight")
        self.animation.setDuration(250)
        self.animation.setStartValue(self.height())
        self.animation.setEndValue(0)
        self.animation.setEasingCurve(QEasingCurve.InCubic)
        self.animation.finished.connect(lambda: self.closed.emit())
        self.animation.start()




class MainWindow(QMainWindow):
    logout_requested = pyqtSignal()
    back_requested = pyqtSignal()


    def __init__(self, user):
        super().__init__()
        self.current_user = user
        self.inventory_controller = InventoryController()
        self.previous_page_index = 0
        self.setup_animations()


        if not hasattr(self.inventory_controller, 'model'):
            raise AttributeError("InventoryController was not initialized correctly. Check if the database is open.")


        self.nav_buttons = []
        self.init_ui()
        self.apply_styles()


    def setup_animations(self):
        self.fade_animations = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate_sidebar)
        self.timer.start(100)


    def animate_sidebar(self):
        # Animate sidebar elements
        for widget in self.sidebar.findChildren(QWidget):
            if widget.objectName() in ["nav-container", "user-container"]:
                animation = QPropertyAnimation(widget, b"windowOpacity")
                animation.setDuration(500)
                animation.setStartValue(0.0)
                animation.setEndValue(1.0)
                animation.setEasingCurve(QEasingCurve.OutCubic)
                self.fade_animations.append(animation)
                animation.start()
        self.timer.stop()


    def init_ui(self):
        self.setWindowTitle('Smart Shop Manager')
        self.setMinimumSize(1200, 700)


        central_widget = QWidget()
        self.setCentralWidget(central_widget)


        self.main_layout = QHBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)


        self.sidebar = self.create_sidebar()
        self.main_layout.addWidget(self.sidebar, 1)


        content_area = self.create_content_area()
        self.main_layout.addWidget(content_area, 5)


        self.add_dashboard_page()
        self.add_inventory_page()
        self.add_sales_page()
        self.add_customers_page()
        self.add_suppliers_page()
        self.add_reports_page()


        self.content_stack.setCurrentIndex(0)
        self.update_time_bar()
        self.start_footer_timer()
       
        # Show welcome alert with animation
        self.show_alert("Welcome to Smart Shop Manager! You are logged in as " +
                      f"{self.current_user.full_name} ({self.current_user.role.capitalize()}).", "info")


    def create_sidebar(self):
        sidebar_widget = QWidget()
        sidebar_widget.setObjectName("sidebar")
        sidebar_widget.setMinimumWidth(240)
        sidebar_widget.setMaximumWidth(280)


        layout = QVBoxLayout(sidebar_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)


        # App title/logo area with enhanced styling
        title_container = QWidget()
        title_container.setObjectName("sidebar-header")
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(15, 25, 15, 25)


        # Add logo/icon
        logo_label = QLabel("🏪")
        logo_label.setFont(QFont("Segoe UI", 36, QFont.Bold))
        logo_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(logo_label)


        title = QLabel("Smart Shop\nManager")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setObjectName("app-title")
        title_layout.addWidget(title)


        layout.addWidget(title_container)


        # Navigation buttons with enhanced styling
        nav_container = QWidget()
        nav_container.setObjectName("nav-container")
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(10, 15, 10, 15)
        nav_layout.setSpacing(8)


        # Create enhanced navigation buttons
        self.create_nav_button(nav_layout, "🏠 Dashboard", 0)
        self.create_nav_button(nav_layout, "📦 Inventory", 1)
        self.create_nav_button(nav_layout, "💳 Sales", 2)
        self.create_nav_button(nav_layout, "👥 Customers", 3)
        self.create_nav_button(nav_layout, "🏭 Suppliers", 4)
        self.create_nav_button(nav_layout, "📊 Reports", 5)


        layout.addWidget(nav_container)
        layout.addStretch()


        # User info and settings with enhanced styling
        user_container = QWidget()
        user_container.setObjectName("user-container")
        user_layout = QVBoxLayout(user_container)
        user_layout.setContentsMargins(15, 20, 15, 20)
        user_layout.setSpacing(10)


        # Add user avatar
        avatar_label = QLabel("👤")
        avatar_label.setFont(QFont("Segoe UI", 28, QFont.Bold))
        avatar_label.setAlignment(Qt.AlignCenter)
        user_layout.addWidget(avatar_label)


        # Divider line
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setObjectName("sidebar-divider")
        user_layout.addWidget(divider)
        user_layout.addSpacing(10)


        # User info with enhanced styling
        user_name = QLabel(f"{self.current_user.full_name}")
        user_name.setFont(QFont("Segoe UI", 14, QFont.Bold))
        user_name.setAlignment(Qt.AlignCenter)
        user_role = QLabel(f"Role: {self.current_user.role.capitalize()}")
        user_role.setFont(QFont("Segoe UI", 12))
        user_role.setAlignment(Qt.AlignCenter)
        user_role.setStyleSheet("color: #9b59b6; font-weight: bold;")


        user_layout.addWidget(user_name)
        user_layout.addWidget(user_role)
        user_layout.addSpacing(15)


        # Enhanced logout button
        logout_btn = QPushButton("🚪 Logout")
        logout_btn.setObjectName("logout-btn")
        logout_btn.setFont(QFont("Segoe UI", 13, QFont.Bold))
        logout_btn.setStyleSheet("background-color: #e74c3c; color: #fff; border-radius: 8px; padding: 12px; font-weight: bold;")
        logout_btn.clicked.connect(self.logout)
        user_layout.addWidget(logout_btn)


        layout.addWidget(user_container)


        return sidebar_widget


    def create_content_area(self):
        content_container = QWidget()
        layout = QVBoxLayout(content_container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)


        # Alert area
        self.alert_widget = AlertWidget()
        self.alert_widget.setVisible(False)
        layout.addWidget(self.alert_widget)


        # Content header with breadcrumb, back button & time
        header_container = QWidget()
        header_container.setObjectName("content-header")
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(20, 12, 20, 12)
       
        # Back button
        self.back_button = QPushButton("← Back")
        self.back_button.setObjectName("back-button")
        self.back_button.setFont(QFont("Segoe UI", 11))
        self.back_button.clicked.connect(self.go_back)
        header_layout.addWidget(self.back_button)
       
        self.page_title = QLabel("Dashboard")
        self.page_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        header_layout.addWidget(self.page_title)
       
        header_layout.addStretch()
       
        self.time_label = QLabel()
        self.time_label.setObjectName("time-label")
        self.time_label.setFont(QFont("Segoe UI", 11))
        header_layout.addWidget(self.time_label)
       
        layout.addWidget(header_container)


        # Main content
        self.content_stack = QStackedWidget()
        self.content_stack.setObjectName("content-stack")
        layout.addWidget(self.content_stack, 1)  # Give it stretch factor


        # Footer
        footer_container = QWidget()
        footer_container.setObjectName("footer")
        footer_layout = QHBoxLayout(footer_container)
        footer_layout.setContentsMargins(20, 10, 20, 10)
       
        copyright_label = QLabel("© 2025 Smart Shop Manager | Developed by Sifat Ali")
        copyright_label.setFont(QFont("Segoe UI", 10))
        footer_layout.addWidget(copyright_label)
       
        footer_layout.addStretch()
       
        self.datetime_label = QLabel()
        self.datetime_label.setObjectName("datetime-label")
        self.datetime_label.setFont(QFont("Segoe UI", 10))
        footer_layout.addWidget(self.datetime_label)
       
        layout.addWidget(footer_container)


        return content_container


    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow, QWidget#content-stack {
                background-color: #ffffff;
                color: #333333;
            }

            QWidget#sidebar {
                background-color: #2c3e50;
                color: #ffffff;
                border-right: 1px solid #34495e;
            }

            QWidget#sidebar-header {
                background-color: #1a2530;
                border-bottom: 1px solid #34495e;
            }

            QLabel#app-title {
                color: #ffffff;
                font-weight: bold;
                font-size: 16px;
                margin-top: 10px;
            }

            QWidget#content-header, QWidget#footer {
                background-color: #f8f9fa;
                color: #555555;
                border-bottom: 1px solid #e9ecef;
            }

            QFrame#sidebar-divider {
                background-color: #34495e;
                height: 2px;
            }

            QPushButton {
                border-radius: 6px;
                padding: 10px 15px;
                font-weight: 500;
                font-size: 13px;
            }

            QWidget#nav-container QPushButton {
                color: #ffffff;
                border: none;
                text-align: left;
                padding: 12px 20px;
                font-size: 13px;
                border-radius: 8px;
                margin: 2px 0;
            }

            QWidget#nav-container QPushButton:hover {
                background-color: #34495e;
            }

            QWidget#nav-container QPushButton:checked {
                background-color: #3498db;
                font-weight: bold;
                border-left: 4px solid #2980b9;
            }

            QPushButton#logout-btn {
                background-color: #e74c3c;
                color: #ffffff;
                font-weight: bold;
                margin-top: 10px;
                border-radius: 8px;
                padding: 12px;
                text-align: center;
                font-size: 13px;
            }

            QPushButton#logout-btn:hover {
                background-color: #c0392b;
            }

            QPushButton#back-button {
                background-color: #3498db;
                color: #ffffff;
                font-weight: bold;
                border-radius: 6px;
                padding: 8px 15px;
                margin-right: 15px;
                font-size: 13px;
            }

            QPushButton#back-button:hover {
                background-color: #2980b9;
            }

            QLabel#time-label, QLabel#datetime-label {
                color: #444444;
                font-weight: 500;
                font-size: 13px;
            }

            QWidget#user-container {
                color: #ffffff;
                background-color: #34495e;
                border-radius: 10px;
                margin: 10px;
            }

            /* Card styles for dashboard and other pages */
            QFrame.card {
                background-color: #ffffff;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
                padding: 15px;
            }

            QFrame.card QLabel.card-title {
                color: #2c3e50;
                font-size: 14px;
                font-weight: bold;
                padding-bottom: 10px;
            }

            QFrame.card QLabel.card-value {
                color: #3498db;
                font-size: 16px;
                font-weight: bold;
            }

            QFrame.card QLabel.card-description {
                color: #7f8c8d;
                font-size: 13px;
            }

            /* Message box button styles */
            QMessageBox QPushButton {
                min-width: 80px;
                min-height: 30px;
                font-size: 13px;
                font-weight: bold;
                border-radius: 4px;
                padding: 5px 15px;
            }

            QMessageBox QPushButton[text="OK"] {
                background-color: #3498db;
                color: white;
            }

            QMessageBox QPushButton[text="Yes"] {
                background-color: #2ecc71;
                color: white;
            }

            QMessageBox QPushButton[text="No"] {
                background-color: #e74c3c;
                color: white;
            }

            QMessageBox QPushButton[text="Cancel"] {
                background-color: #95a5a6;
                color: white;
            }

            /* Scrollbar styling */
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 10px;
                margin: 0px;
            }

            QScrollBar::handle:vertical {
                background: #c0c0c0;
                min-height: 20px;
                border-radius: 5px;
            }

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)


    def start_footer_timer(self):
        self.footer_timer = QTimer(self)
        self.footer_timer.timeout.connect(self.update_datetime)
        self.footer_timer.start(1000)  # Update every 1 second


    def update_datetime(self):
        current_datetime = QDateTime.currentDateTime()
        time_str = current_datetime.toString("hh:mm:ss AP")
        date_str = current_datetime.toString("dddd, MMMM d, yyyy")
       
        self.time_label.setText(time_str)
        self.datetime_label.setText(date_str)


    def update_time_bar(self):
        current_datetime = QDateTime.currentDateTime()
        date_str = current_datetime.toString("dddd, MMMM d, yyyy")
        time_str = current_datetime.toString("hh:mm:ss AP")
       
        self.time_label.setText(time_str)
        self.datetime_label.setText(date_str)


    def create_nav_button(self, layout, text, page_index):
        button = QPushButton(text)
        button.setFont(QFont("Segoe UI", 13))
        button.setCheckable(True)
        button.setMinimumHeight(45)
        button.clicked.connect(lambda: self.change_page(page_index))
        layout.addWidget(button)
        self.nav_buttons.append(button)


        if page_index == 0:
            button.setChecked(True)


    def change_page(self, index):
        # Store previous page for back button
        self.previous_page_index = self.content_stack.currentIndex()
       
        # Update buttons
        for btn in self.nav_buttons:
            btn.setChecked(False)
       
        if isinstance(self.sender(), QPushButton):
            self.sender().setChecked(True)
        else:
            self.nav_buttons[index].setChecked(True)
       
        # Update content
        self.content_stack.setCurrentIndex(index)
       
        # Refresh data on navigation
        widget = self.content_stack.widget(index)
        if hasattr(widget, 'refresh_from_controller'):
            widget.refresh_from_controller()
       
        # Update page title
        titles = [
            "Dashboard", "Inventory Management",
            "Sales & Billing", "Customer Management",
            "Supplier Management", "Reports & Analytics"
        ]
        self.page_title.setText(titles[index])
       
        # Notification
        self.show_alert(f"Viewing {titles[index]}", "info")


    def go_back(self):
        """Navigate to previous page"""
        self.change_page(self.previous_page_index)
        self.show_alert("Returned to previous page", "info")


    def show_alert(self, message, level="info"):
        self.alert_widget.show_alert(message, level)


    def add_dashboard_page(self):
        dashboard = DashboardPage()
        dashboard.view_inventory_requested.connect(lambda: self.change_page(1))
        dashboard.view_add_product_requested.connect(self.handle_add_product_from_dashboard)
        dashboard.view_orders_requested.connect(lambda: self.change_page(2))
        self.content_stack.addWidget(dashboard)


    def handle_add_product_from_dashboard(self):
        self.change_page(1)
        # Find the inventory view and open add dialog
        inventory_view = None
        for i in range(self.content_stack.count()):
            widget = self.content_stack.widget(i)
            if isinstance(widget, InventoryView):
                inventory_view = widget
                break
        if inventory_view:
            inventory_view.show_add_dialog()


    def add_inventory_page(self):
        inventory_view = InventoryView(self.inventory_controller)
        self.content_stack.addWidget(inventory_view)


    def add_sales_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
       
        header = QLabel("Sales & Billing")
        header.setFont(QFont("Segoe UI", 24, QFont.Bold))
       
        layout.addWidget(header)
       
        info_label = QLabel("Sales interface goes here...")
        info_label.setFont(QFont("Segoe UI", 14))
        layout.addWidget(info_label)
        layout.addStretch()
       
        self.content_stack.addWidget(page)


    def add_customers_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
       
        header = QLabel("Customer Management")
        header.setFont(QFont("Segoe UI", 24, QFont.Bold))
       
        layout.addWidget(header)
       
        info_label = QLabel("Customer records shown here...")
        info_label.setFont(QFont("Segoe UI", 14))
        layout.addWidget(info_label)
        layout.addStretch()
       
        self.content_stack.addWidget(page)


    def add_suppliers_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
       
        header = QLabel("Supplier Management")
        header.setFont(QFont("Segoe UI", 24, QFont.Bold))
       
        layout.addWidget(header)
       
        info_label = QLabel("Supplier list will be added here...")
        info_label.setFont(QFont("Segoe UI", 14))
        layout.addWidget(info_label)
        layout.addStretch()
       
        self.content_stack.addWidget(page)


    def add_reports_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
       
        header = QLabel("Reports & Analytics")
        header.setFont(QFont("Segoe UI", 24, QFont.Bold))
       
        layout.addWidget(header)
       
        info_label = QLabel("Reports dashboard coming soon...")
        info_label.setFont(QFont("Segoe UI", 14))
        layout.addWidget(info_label)
        layout.addStretch()
       
        self.content_stack.addWidget(page)


    def logout(self):
        self.show_alert("Logging out...", "warning")
        # Add slight delay to show the message before actually logging out
        QTimer.singleShot(500, lambda: self.actually_logout())
   
    def actually_logout(self):
        print("Logout initiated")
        self.logout_requested.emit()
        self.close()

