from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QScrollArea, QStackedLayout,
    QSizePolicy, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QIcon

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

        # Add alert notifications at the top
        alert_card = Card()
        alert_layout = QHBoxLayout()
        alert_layout.setContentsMargins(15, 10, 15, 10)
        alert_layout.setSpacing(18)
        
        alert_items = [
            ("ℹ️", "<b>Low Stock:</b> 3 Items", ThemeManager.get_color("primary")),
            ("⚠️", "<b>Pending Orders:</b> 2", ThemeManager.get_color("warning")),
            ("🛡️", "<b>Security Alert:</b> 1", ThemeManager.get_color("danger"))
        ]
        
        for icon, text, color in alert_items:
            icon_label = QLabel(f"<span style='font-size:18px;color:{color};'>{icon}</span>")
            text_label = QLabel(text)
            alert_layout.addWidget(icon_label)
            alert_layout.addWidget(text_label)
        
        alert_layout.addStretch()
        alert_card.layout.addLayout(alert_layout)
        content_layout.addWidget(alert_card)

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
        activity_section = Card("Recent Activity")
        activity_layout = QVBoxLayout()
        activity_layout.setContentsMargins(15, 5, 15, 15)
        
        # Activity items
        activities = [
            ("💰", "New sale completed", "$120.50", "10 minutes ago"),
            ("📦", "Inventory updated", "25 items", "30 minutes ago"),
            ("👤", "New customer added", "John Smith", "1 hour ago"),
            ("⚠️", "Low stock alert", "Printer Paper", "2 hours ago")
        ]
        
        for icon, title, value, time in activities:
            item_layout = QHBoxLayout()
            
            # Icon
            icon_label = QLabel(icon)
            icon_label.setFont(QFont(ThemeManager.FONTS["family"], 16))
            item_layout.addWidget(icon_label)
            
            # Details
            details_layout = QVBoxLayout()
            title_label = QLabel(title)
            title_label.setFont(QFont(ThemeManager.FONTS["family"], 12, QFont.Bold))
            details_layout.addWidget(title_label)
            
            value_label = QLabel(value)
            value_label.setFont(QFont(ThemeManager.FONTS["family"], 11))
            value_label.setStyleSheet(f"color: {ThemeManager.get_color('text_secondary')};")
            details_layout.addWidget(value_label)
            
            item_layout.addLayout(details_layout)
            item_layout.addStretch()
            
            # Time
            time_label = QLabel(time)
            time_label.setFont(QFont(ThemeManager.FONTS["family"], 10))
            time_label.setStyleSheet(f"color: {ThemeManager.get_color('text_secondary')};")
            item_layout.addWidget(time_label)
            
            activity_layout.addLayout(item_layout)
            
            # Add separator except for last item
            if activities.index((icon, title, value, time)) < len(activities) - 1:
                separator = QFrame()
                separator.setFrameShape(QFrame.HLine)
                separator.setStyleSheet(f"background-color: {ThemeManager.get_color('border')};")
                activity_layout.addWidget(separator)
        
        activity_section.layout.addLayout(activity_layout)
        dashboard.add_detail_section(activity_section)
        
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
        inventory_btn.clicked.connect(lambda: self.parent().change_page(1))
        sales_btn.clicked.connect(lambda: self.parent().change_page(2))
        customers_btn.clicked.connect(lambda: self.parent().change_page(3))
        reports_btn.clicked.connect(lambda: self.parent().change_page(5))

