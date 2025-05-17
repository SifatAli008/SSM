from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QScrollArea, QStackedLayout,
    QSizePolicy, QGraphicsDropShadowEffect, QMessageBox
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QIcon, QPainter, QPen, QBrush

# Import our custom components
from app.views.widgets.components import Card, Button, PageHeader
from app.views.widgets.layouts import DashboardLayout, CardGrid
from app.utils.theme_manager import ThemeManager

# Keep original widget imports for backward compatibility
from app.views.widgets.card_widget import CardWidget
from app.views.widgets.graph_widget import Graph
from app.views.inventory_view import InventoryView




class DashboardPage(QWidget):
    """
    Dashboard page using the new component system
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.setup_animations()
        self.update_recent_activities()  # Initialize with recent activities


    def setup_animations(self):
        # Create fade-in animation for cards
        self.fade_animations = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate_cards)
        self.timer.start(100)  # Start animation after 100ms


    def animate_cards(self):
        # Find all card widgets and animate them
        cards = self.findChildren(QFrame)
        delay = 0
        
        for card in cards:
            if isinstance(card, Card) or card.objectName() == "card":
                animation = QPropertyAnimation(card, b"windowOpacity")
                animation.setDuration(500)
                animation.setStartValue(0.0)
                animation.setEndValue(1.0)
                animation.setEasingCurve(QEasingCurve.OutCubic)
                # Use QTimer to start animation with delay
                QTimer.singleShot(delay, lambda a=animation: a.start())
                self.fade_animations.append(animation)
                delay += 50
                
        self.timer.stop()


    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Container for all dashboard content
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(30)

        # Page header
        header = PageHeader("Dashboard Overview", "View and manage your business at a glance")
        
        # Add action buttons to the header
        self.add_product_btn = Button("Add Product", variant="primary")
        header.add_action(self.add_product_btn)
        
        content_layout.addWidget(header)

        # Dashboard layout with metrics and charts
        dashboard = DashboardLayout()
        dashboard.set_columns(3)  # Set to 3 columns for summary cards
        
        # Add summary cards (top metrics)
        revenue_card = CardWidget(
            "Total Revenue",
            "$5,250",
            "Last 7 Days: 12%↑",
            icon="💰",
            color="#2ecc71"
        )
        
        customer_card = CardWidget(
            "Customer Traffic",
            "320",
            "Peak Hour: 5-6 PM",
            icon="👥",
            color="#3498db"
        )
        
        orders_card = CardWidget(
            "Pending Orders",
            "5",
            "Deliveries: 3 Today",
            icon="📦",
            color="#e74c3c"
        )
        
        # Add metrics to dashboard
        dashboard.add_summary_card(revenue_card)
        dashboard.add_summary_card(customer_card)
        dashboard.add_summary_card(orders_card)
        
        # Add graphs section
        graphs_section = Card("Performance Charts")
        graphs_layout = QHBoxLayout()
        graphs_layout.setContentsMargins(15, 15, 15, 15)
        graphs_layout.setSpacing(20)
        
        # Create graph widgets
        sales_graph = Graph(
            "Sales Trend",
            "Weekly | Monthly",
            color="#2ecc71",
            icon="📈"
        )
        
        stock_graph = Graph(
            "Stock Levels",
            "Inventory Alerts",
            color="#f39c12",
            icon="📊"
        )
        
        profit_graph = Graph(
            "Profit & Loss",
            "Forecast: +5% Growth",
            color="#9b59b6",
            icon="💹"
        )
        
        # Add graphs to layout
        graphs_layout.addWidget(sales_graph)
        graphs_layout.addWidget(stock_graph)
        graphs_layout.addWidget(profit_graph)
        
        graphs_section.layout.addLayout(graphs_layout)
        dashboard.add_detail_section(graphs_section)
        
        # Add quick actions section
        actions_section = Card("Quick Actions")
        actions_grid = QHBoxLayout()
        actions_grid.setContentsMargins(15, 15, 15, 15)
        actions_grid.setSpacing(15)
        
        # Action buttons
        inventory_btn = Button("View Inventory", "📦", "primary")
        sales_btn = Button("Process Sale", "💰", "success")
        customers_btn = Button("Manage Customers", "👥", "secondary")
        reports_btn = Button("Generate Reports", "📊", "info")
        
        # Add buttons to grid
        actions_grid.addWidget(inventory_btn)
        actions_grid.addWidget(sales_btn)
        actions_grid.addWidget(customers_btn)
        actions_grid.addWidget(reports_btn)
        
        # Add actions to layout
        actions_section.layout.addLayout(actions_grid)
        dashboard.add_detail_section(actions_section)
        
        # Recent activity section
        self.activity_section = Card("Recent Activity")
        self.activity_layout = QVBoxLayout()
        self.activity_layout.setContentsMargins(15, 5, 15, 15)
        
        # Add activity layout to card
        self.activity_section.layout.addLayout(self.activity_layout)
        dashboard.add_detail_section(self.activity_section)
        
        # Add dashboard to content layout
        content_layout.addWidget(dashboard)
        
        # Create scrollable area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(content_widget)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Add scroll area to main layout
        main_layout.addWidget(scroll_area)
        
        # Connect signals
        inventory_btn.clicked.connect(lambda: self.navigate_to_page(1))
        sales_btn.clicked.connect(lambda: self.navigate_to_page(2))
        customers_btn.clicked.connect(lambda: self.navigate_to_page(3))
        reports_btn.clicked.connect(self.generate_report)

    def get_main_window(self):
        """
        Get the main window from the parent hierarchy
        """
        parent = self.parent()
        while parent and not hasattr(parent, 'change_page'):
            parent = parent.parent()
        return parent

    def navigate_to_page(self, page_index):
        """
        Navigate to a page through the main window
        """
        main_window = self.get_main_window()
        if main_window and hasattr(main_window, 'change_page'):
            main_window.change_page(page_index)
        else:
            print("Cannot navigate: Main window not found or no change_page method.")

    def generate_report(self):
        """Navigate to reports page and show report generation dialog"""
        # First navigate to reports page
        self.navigate_to_page(4)
        
        # After a short delay to ensure the page is loaded, show report options
        QTimer.singleShot(100, self.show_report_options)
    
    def show_report_options(self):
        """Show report generation options"""
        msg = QMessageBox()
        msg.setWindowTitle("Generate Report")
        msg.setText("Select the type of report you want to generate:")
        
        # Add report type buttons
        sales_btn = msg.addButton("Sales Report", QMessageBox.ActionRole)
        inventory_btn = msg.addButton("Inventory Report", QMessageBox.ActionRole)
        financial_btn = msg.addButton("Financial Report", QMessageBox.ActionRole)
        cancel_btn = msg.addButton("Cancel", QMessageBox.RejectRole)
        
        msg.exec_()
        
        # Find the reports page to call its methods
        clicked_btn = msg.clickedButton()
        main_window = self.get_main_window()
        
        if not main_window:
            QMessageBox.warning(self, "Error", "Could not access reports page")
            return
            
        # Find the reports view in the content stack
        reports_view = None
        for i in range(main_window.content_stack.count()):
            widget = main_window.content_stack.widget(i)
            if hasattr(widget, 'generate_sales_report'):
                reports_view = widget
                break
        
        if not reports_view:
            QMessageBox.warning(self, "Error", "Reports page not found")
            return
            
        # Call the appropriate method based on button clicked
        if clicked_btn == sales_btn:
            reports_view.generate_sales_report()
        elif clicked_btn == inventory_btn:
            reports_view.generate_inventory_report()
        elif clicked_btn == financial_btn:
            reports_view.generate_financial_report()

    def update_recent_activities(self):
        """Update the recent activities section with fresh data"""
        # Clear existing activities
        for i in reversed(range(self.activity_layout.count())):
            item = self.activity_layout.itemAt(i)
            if item:
                widget = item.widget()
                if widget:
                    widget.deleteLater()
                else:
                    # If it's a layout, recursively remove all items
                    self.clear_layout(item.layout())
                    self.activity_layout.removeItem(item)
        
        # Add new activity items - in a real app, this would come from a database
        activities = [
            ("💰", "New sale completed", "$120.50", "10 minutes ago"),
            ("📦", "Inventory updated", "25 items", "30 minutes ago"),
            ("👤", "New customer added", "John Smith", "1 hour ago"),
            ("⚠️", "Low stock alert", "Printer Paper", "2 hours ago")
        ]
        
        # Create activity items with enhanced styling
        for icon, title, value, time in activities:
            # Create a container widget for each activity item
            activity_item = QWidget()
            activity_item.setObjectName("activity-item")
            activity_item.setStyleSheet("""
                #activity-item {
                    border-bottom: 1px solid #e0e0e0;
                    padding: 10px 5px;
                    background-color: transparent;
                }
                #activity-item:hover {
                    background-color: #f5f5f5;
                }
            """)
            
            item_layout = QHBoxLayout(activity_item)
            item_layout.setContentsMargins(8, 12, 8, 12)
            item_layout.setSpacing(15)
            
            # Create icon container with colored circle background
            icon_container = QWidget()
            icon_container.setFixedSize(36, 36)
            icon_container.setStyleSheet(f"""
                background-color: {self.get_icon_background_color(icon)};
                border-radius: 18px;
                color: white;
                font-size: 18px;
            """)
            
            # Icon
            icon_layout = QVBoxLayout(icon_container)
            icon_layout.setContentsMargins(0, 0, 0, 0)
            icon_layout.setAlignment(Qt.AlignCenter)
            
            icon_label = QLabel(icon)
            icon_label.setAlignment(Qt.AlignCenter)
            icon_label.setStyleSheet("background-color: transparent;")
            icon_layout.addWidget(icon_label)
            
            item_layout.addWidget(icon_container)
            
            # Details
            details_layout = QVBoxLayout()
            details_layout.setSpacing(4)
            
            title_label = QLabel(title)
            title_label.setFont(QFont(ThemeManager.FONTS["family"], 12, QFont.Bold))
            details_layout.addWidget(title_label)
            
            value_label = QLabel(value)
            value_label.setFont(QFont(ThemeManager.FONTS["family"], 11))
            value_label.setStyleSheet(f"color: {ThemeManager.get_color('text_secondary')};")
            details_layout.addWidget(value_label)
            
            item_layout.addLayout(details_layout, 1)  # Add stretch factor to details
            
            # Time with right alignment
            time_container = QWidget()
            time_layout = QVBoxLayout(time_container)
            time_layout.setContentsMargins(0, 0, 0, 0)
            time_layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            time_label = QLabel(time)
            time_label.setFont(QFont(ThemeManager.FONTS["family"], 10))
            time_label.setStyleSheet(f"color: {ThemeManager.get_color('text_secondary')};")
            time_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            time_layout.addWidget(time_label)
            
            item_layout.addWidget(time_container)
            
            # Add the activity item to the main layout
            self.activity_layout.addWidget(activity_item)
    
    def get_icon_background_color(self, icon):
        """Return an appropriate background color based on icon type"""
        if icon == "💰":  # Sales
            return ThemeManager.get_color("success")
        elif icon == "📦":  # Inventory
            return ThemeManager.get_color("primary")
        elif icon == "👤":  # Customer
            return ThemeManager.get_color("accent")
        elif icon == "⚠️":  # Alert
            return ThemeManager.get_color("warning")
        else:
            return ThemeManager.get_color("info")

    def clear_layout(self, layout):
        """Recursively clear a layout"""
        if layout is None:
            return
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                self.clear_layout(item.layout())

