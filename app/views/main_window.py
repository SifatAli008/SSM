from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QStackedWidget, QFrame, QSpacerItem,
    QSizePolicy, QGraphicsDropShadowEffect, QToolButton, QScrollBar, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QDateTime, QPropertyAnimation, QEasingCurve, QSize
from PyQt5.QtGui import QFont, QIcon, QColor

# Import controllers
from app.controllers.inventory_controller import InventoryController

# Import views
from app.views.dashboard_view import DashboardPage
from app.views.inventory_view import InventoryView
from app.views.sales_view import SalesView
from app.views.customer_view import CustomerView
from app.views.reports_view import ReportsView

# Import components
from app.views.widgets.components import Sidebar, Button, Card, PageHeader
from app.views.widgets.layouts import PageLayout
from app.utils.theme_manager import ThemeManager, ThemeType

# Keep the AlertWidget for now - we'll refactor it later
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
        
        # Initialize properties
        self.current_user = user
        self.inventory_controller = InventoryController()
        self.previous_page_index = 0
        
        # Initialize UI
        ThemeManager.apply_theme(ThemeType.LIGHT)
        self.init_ui()
        
        # Initialize sidebar with animation
        self.setup_animations()

    def setup_animations(self):
        self.fade_animations = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate_sidebar)
        self.timer.start(100)

    def animate_sidebar(self):
        # Animate sidebar elements with fade-in effect
        animation = QPropertyAnimation(self.sidebar, b"maximumWidth")
        animation.setDuration(300)
        animation.setStartValue(0)
        animation.setEndValue(250)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        self.fade_animations.append(animation)
        animation.start()
        
        self.timer.stop()

    def init_ui(self):
        # Set window properties
        self.setWindowTitle('Smart Shop Manager')
        self.setMinimumSize(1200, 700)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        self.main_layout = QHBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Create sidebar using our new component
        self.sidebar = self.create_sidebar()
        self.main_layout.addWidget(self.sidebar)

        # Create content area
        self.content_area = self.create_content_area()
        self.main_layout.addWidget(self.content_area, 5)

        # Initialize page stack
        self.add_dashboard_page()
        self.add_inventory_page()
        self.add_sales_page()
        self.add_customers_page()
        self.add_reports_page()
        self.add_settings_page()

        # Set active page
        self.content_stack.setCurrentIndex(0)
        self.update_time_bar()
        self.start_footer_timer()

    def create_sidebar(self):
        # Create sidebar with our new component
        sidebar = Sidebar()
        
        # Set up navigation pages with icons
        pages = {
            "dashboard": {"title": "Dashboard", "icon": "🏠"},
            "inventory": {"title": "Inventory", "icon": "📦"},
            "sales": {"title": "Sales", "icon": "💰"},
            "customers": {"title": "Customers", "icon": "👥"},
            "reports": {"title": "Reports", "icon": "📊"},
            "settings": {"title": "Settings", "icon": "⚙️"}
        }
        
        # Set up navigation
        sidebar.setup_navigation(pages)
        
        # Connect the page_changed signal
        sidebar.page_changed.connect(self.handle_page_changed)
        
        # Set up profile info
        if self.current_user and hasattr(self.current_user, 'full_name') and self.current_user.full_name:
            sidebar.profile_info.setText(self.current_user.full_name)
            if self.current_user.full_name:
                initials = "".join(name[0].upper() for name in self.current_user.full_name.split(' ')[:2])
                sidebar.profile_icon.setText(initials)
        
        # Settings button now points to the settings page
        sidebar.settings_button.clicked.connect(lambda: self.change_page(5))
        
        return sidebar

    def handle_page_changed(self, page_id):
        # Map page IDs to indexes
        page_indexes = {
            "dashboard": 0,
            "inventory": 1,
            "sales": 2,
            "customers": 3,
            "reports": 4,
            "settings": 5
        }
        
        # Change to the selected page
        if page_id in page_indexes:
            self.change_page(page_indexes[page_id])

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
        self.back_button = Button("← Back", variant="secondary")
        self.back_button.clicked.connect(self.go_back)
        header_layout.addWidget(self.back_button)
       
        self.page_title = QLabel("Dashboard")
        self.page_title.setFont(QFont(ThemeManager.FONTS["family"], ThemeManager.FONTS["size_xlarge"], QFont.Bold))
        header_layout.addWidget(self.page_title)
       
        header_layout.addStretch()
       
        self.time_label = QLabel()
        self.time_label.setFont(QFont(ThemeManager.FONTS["family"], ThemeManager.FONTS["size_normal"]))
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
        copyright_label.setFont(QFont(ThemeManager.FONTS["family"], ThemeManager.FONTS["size_small"]))
        footer_layout.addWidget(copyright_label)
       
        footer_layout.addStretch()
       
        self.datetime_label = QLabel()
        self.datetime_label.setFont(QFont(ThemeManager.FONTS["family"], ThemeManager.FONTS["size_small"]))
        footer_layout.addWidget(self.datetime_label)
       
        layout.addWidget(footer_container)

        return content_container

    def start_footer_timer(self):
        # Update time every second
        self.datetime_timer = QTimer(self)
        self.datetime_timer.timeout.connect(self.update_datetime)
        self.datetime_timer.start(1000)
        self.update_datetime()

    def update_datetime(self):
        current_datetime = QDateTime.currentDateTime()
        datetime_text = current_datetime.toString("dddd, MMMM d, yyyy - hh:mm:ss AP")
        self.datetime_label.setText(datetime_text)
        self.time_label.setText(current_datetime.toString("hh:mm:ss AP"))

    def update_time_bar(self):
        current_time = QDateTime.currentDateTime().toString("hh:mm:ss AP")
        self.time_label.setText(current_time)

    def change_page(self, index):
        # Store previous page for back button
        self.previous_page_index = self.content_stack.currentIndex()
        
        # Change to new page
        self.content_stack.setCurrentIndex(index)
        
        # Update page title
        page_titles = [
            "Dashboard",
            "Inventory Management",
            "Sales & Orders",
            "Customer Management",
            "Reports & Analytics",
            "Application Settings"
        ]
        
        if 0 <= index < len(page_titles):
            self.page_title.setText(page_titles[index])
        
        # Update sidebar selection
        page_ids = [
            "dashboard",
            "inventory",
            "sales", 
            "customers",
            "reports",
            "settings"
        ]
        
        if 0 <= index < len(page_ids):
            self.sidebar.select_page(page_ids[index])

    def go_back(self):
        self.change_page(self.previous_page_index)

    def show_alert(self, message, level="info"):
        self.alert_widget.show_alert(message, level)

    def add_dashboard_page(self):
        # Create dashboard page
        dashboard = DashboardPage(self)
        dashboard.add_product_btn.clicked.connect(self.handle_add_product_from_dashboard)
        self.content_stack.addWidget(dashboard)

    def handle_add_product_from_dashboard(self):
        # Find the inventory page index
        inventory_idx = -1
        for i in range(self.content_stack.count()):
            if isinstance(self.content_stack.widget(i), InventoryView):
                inventory_idx = i
                break
        
        # If inventory page found, change to it and trigger add product
        if inventory_idx >= 0:
            self.change_page(inventory_idx)
            inventory_page = self.content_stack.widget(inventory_idx)
            if hasattr(inventory_page, 'show_add_product_dialog'):
                inventory_page.show_add_product_dialog()
        else:
            self.show_alert("Inventory page not found", "error")

    def add_inventory_page(self):
        # Create inventory page
        inventory_view = InventoryView()
        self.content_stack.addWidget(inventory_view)

    def add_sales_page(self):
        # Create sales page
        sales_view = SalesView()
        self.content_stack.addWidget(sales_view)

    def add_customers_page(self):
        # Create customers page
        customers_view = CustomerView()
        self.content_stack.addWidget(customers_view)

    def add_reports_page(self):
        # Create reports page using ReportsView
        reports_view = ReportsView()
        self.content_stack.addWidget(reports_view)

    def add_settings_page(self):
        """Create dedicated settings page"""
        from app.views.settings_view import SettingsView
        settings_view = SettingsView(self)
        self.content_stack.addWidget(settings_view)

    def logout(self):
        # Ask for confirmation before logout
        response = QMessageBox.question(self, "Confirm Logout", 
                                      "Are you sure you want to logout?", 
                                      QMessageBox.Yes | QMessageBox.No)
        if response == QMessageBox.Yes:
            # Add slight animation and delay before logging out
            QTimer.singleShot(300, self.actually_logout)

    def actually_logout(self):
        self.logout_requested.emit()
        
    def show_settings(self):
        """Display the theme selection dialog and apply chosen theme"""
        # Create a themed dialog for settings
        themes = [
            {"name": "Light Theme", "type": ThemeType.LIGHT},
            {"name": "Dark Theme", "type": ThemeType.DARK},
            {"name": "Blue Theme", "type": ThemeType.BLUE}
        ]
        
        msg = QMessageBox()
        msg.setWindowTitle("Application Settings")
        msg.setText("Select a theme:")
        
        # Add theme buttons
        theme_buttons = []
        for theme in themes:
            button = msg.addButton(theme["name"], QMessageBox.ActionRole)
            button.setProperty("theme_type", theme["type"])
            theme_buttons.append(button)
        
        cancel_button = msg.addButton("Cancel", QMessageBox.RejectRole)
        
        msg.exec_()
        
        # Handle button click
        clicked_button = msg.clickedButton()
        if clicked_button and clicked_button != cancel_button:
            theme_type = clicked_button.property("theme_type")
            
            # Apply the selected theme
            if theme_type:
                try:
                    ThemeManager.apply_theme(theme_type)
                    self.show_alert(f"Theme changed to {clicked_button.text()}", "success")
                except Exception as e:
                    self.show_alert(f"Error changing theme: {str(e)}", "error")

