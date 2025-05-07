from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QScrollArea, QStackedLayout,
    QSizePolicy, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QIcon

from views.widgets.card_widget import CardWidget
from views.widgets.action_button import ActionButton
from views.widgets.graph_widget import Graph
from views.inventory_view import InventoryView




class DashboardPage(QWidget):
    view_inventory_requested = pyqtSignal()
    view_add_product_requested = pyqtSignal()
    view_orders_requested = pyqtSignal()
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
        for card in self.findChildren(QFrame):
            if card.objectName() == "card":
                animation = QPropertyAnimation(card, b"windowOpacity")
                animation.setDuration(500)
                animation.setStartValue(0.0)
                animation.setEndValue(1.0)
                animation.setEasingCurve(QEasingCurve.OutCubic)
                self.fade_animations.append(animation)
                animation.start()
        self.timer.stop()


    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Add dashboard notification card
        notif_card = QFrame()
        notif_card.setObjectName("dashboardNotif")
        notif_layout = QHBoxLayout(notif_card)
        notif_layout.setContentsMargins(18, 10, 18, 10)
        notif_layout.setSpacing(18)
        notif_card.setCursor(Qt.PointingHandCursor)

        notif_icon1 = QLabel("<span style='font-size:18px;color:#3498db;'>ℹ️</span>")
        notif_text1 = QLabel("<b>Low Stock:</b> 3 Items")
        notif_icon2 = QLabel("<span style='font-size:18px;color:#f39c12;'>⚠️</span>")
        notif_text2 = QLabel("<b>Pending Orders:</b> 2")
        notif_icon3 = QLabel("<span style='font-size:18px;color:#2980b9;'>🛡️</span>")
        notif_text3 = QLabel("<b>Security Alert:</b> 1")

        for w in [notif_icon1, notif_text1, notif_icon2, notif_text2, notif_icon3, notif_text3]:
            notif_layout.addWidget(w)
        notif_layout.addStretch()

        main_layout.addWidget(notif_card)

        # Add a clean dashboard header with shadow
        header_container = QFrame()
        header_container.setObjectName("dashboardHeader")
        header_layout = QVBoxLayout(header_container)
        header_layout.setContentsMargins(20, 20, 20, 20)


        header = QLabel("📊 Dashboard Overview")
        header.setObjectName("dashboardTitle")
        header.setFont(QFont("Segoe UI", 24, QFont.Bold))
        header_layout.addWidget(header)


        # Add shadow effect to header
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 2)
        header_container.setGraphicsEffect(shadow)


        main_layout.addWidget(header_container)


        # Central stacked layout
        self.stack_layout = QStackedLayout()
        self.dashboard_widget = self.create_scroll_area()
        self.inventory_widget = InventoryView()


        self.stack_layout.addWidget(self.dashboard_widget)
        self.stack_layout.addWidget(self.inventory_widget)


        central_widget = QWidget()
        central_widget.setLayout(self.stack_layout)
        main_layout.addWidget(central_widget)


        self.apply_stylesheets()


    def create_scroll_area(self):
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(30)


        content_layout.addLayout(self.create_top_metrics())
        content_layout.addLayout(self.create_graphs())
        content_layout.addLayout(self.create_additional_metrics())
        content_layout.addLayout(self.create_action_buttons())


        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(content_widget)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
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
        return scroll_area


    def create_top_metrics(self):
        layout = QHBoxLayout()
        layout.setSpacing(20)

        # Create enhanced metric cards with fixed min height and visible titles
        revenue_card = CardWidget(
            "Total Revenue",
            "$5,000",
            "Last 7 Days: 12%↑",
            icon="💰",
            color="#2ecc71"
        )
        revenue_card.setMinimumHeight(110)
        traffic_card = CardWidget(
            "Customer Traffic",
            "320",
            "Peak Hour: 5-6 PM",
            icon="👥",
            color="#3498db"
        )
        traffic_card.setMinimumHeight(110)
        orders_card = CardWidget(
            "Pending Orders",
            "5",
            "Deliveries: 3 Today",
            icon="📦",
            color="#e74c3c"
        )
        orders_card.setMinimumHeight(110)

        layout.addWidget(revenue_card)
        layout.addWidget(traffic_card)
        layout.addWidget(orders_card)

        return layout


    def create_graphs(self):
        layout = QHBoxLayout()
        layout.setSpacing(20)


        # Create enhanced graph widgets
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


        layout.addWidget(sales_graph)
        layout.addWidget(stock_graph)
        layout.addWidget(profit_graph)


        return layout


    def create_additional_metrics(self):
        layout = QHBoxLayout()
        layout.setSpacing(20)


        # Create enhanced metric cards
        payments_card = CardWidget(
            "Due Payments",
            "$1,200",
            "Last 7 Days: 12%↑",
            icon="💳",
            color="#e67e22"
        )
        stock_card = CardWidget(
            "Stock Info",
            "500",
            "Low Stock: 5 items...",
            icon="📦",
            color="#f1c40f"
        )
        returns_card = CardWidget(
            "Customer Returns",
            "7%",
            "Satisfaction: 92%↑",
            icon="🔄",
            color="#1abc9c"
        )


        layout.addWidget(payments_card)
        layout.addWidget(stock_card)
        layout.addWidget(returns_card)


        return layout


    def create_action_buttons(self):
        layout = QHBoxLayout()
        layout.setSpacing(20)

        # Create enhanced action sections with fixed min height and improved button style
        invoice_frame = self.build_action_section(
            "Invoice & Billing",
            [
                ActionButton("View & Print", color="#27ae60", icon="📄"),
                ActionButton("New Invoice", color="#2ecc71", icon="➕")
            ]
        )
        invoice_frame.setMinimumHeight(110)
        layout.addWidget(invoice_frame)

        quick_actions_frame = self.build_action_section(
            "Quick Actions",
            [
                self.create_add_product_button(),
                self.create_manage_orders_button(),
                self.create_inventory_button()
            ]
        )
        quick_actions_frame.setMinimumHeight(110)
        layout.addWidget(quick_actions_frame)

        search_stock_frame = QFrame()
        search_stock_frame.setObjectName("card")
        search_stock_frame.setMinimumHeight(110)
        search_stock_layout = QVBoxLayout(search_stock_frame)

        title = QLabel("🔍 Search Stock")
        title.setObjectName("cardTitle")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setWordWrap(True)
        search_stock_layout.addWidget(title)

        input_field = QLineEdit()
        input_field.setPlaceholderText("Enter product name...")
        input_field.setObjectName("searchInput")
        input_field.setMinimumHeight(40)
        search_stock_layout.addWidget(input_field)
        search_stock_layout.addStretch()

        layout.addWidget(search_stock_frame)
        return layout


    def create_inventory_button(self):
        btn = ActionButton("View Inventory", color="#9b59b6", icon="📦")
        btn.clicked.connect(self.emit_view_inventory)
        return btn


    def create_add_product_button(self):
        btn = ActionButton("Add Product", color="#27ae60", icon="➕")
        btn.clicked.connect(self.emit_add_product)
        return btn


    def create_manage_orders_button(self):
        btn = ActionButton("Manage Orders", color="#3498db", icon="📦")
        btn.clicked.connect(self.emit_manage_orders)
        return btn


    def emit_view_inventory(self):
        self.view_inventory_requested.emit()


    def emit_add_product(self):
        self.view_add_product_requested.emit()


    def emit_manage_orders(self):
        self.view_orders_requested.emit()


    def show_inventory_view(self):
        # This is now handled by the main window via the signal
        pass


    def build_action_section(self, title_text, buttons):
        frame = QFrame()
        frame.setObjectName("card")
        frame.setMinimumHeight(110)
        layout = QVBoxLayout(frame)

        title = QLabel(title_text)
        title.setObjectName("cardTitle")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setWordWrap(True)
        layout.addWidget(title)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        for btn in buttons:
            btn.setMinimumHeight(36)
            btn.setMinimumWidth(120)
            btn.setStyleSheet("font-size: 13px; font-weight: bold;")
            btn_row.addWidget(btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)
        layout.addStretch()
        return frame


    def apply_stylesheets(self):
        self.setStyleSheet("""
            #dashboardHeader {
                background-color: #ffffff;
                border-bottom: 1px solid #e0e0e0;
            }

            #dashboardNotif {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #eaf6ff, stop:1 #f7fbff);
                border: 2px solid #3498db;
                border-radius: 12px;
                margin: 18px 18px 0 18px;
                font-size: 15px;
                font-weight: 600;
            }
            #dashboardNotif:hover {
                border-color: #217dbb;
            }

            #dashboardTitle {
                color: #2c3e50;
                font-size: 24px;
                font-weight: bold;
            }

            #card {
                background-color: #ffffff;
                border-radius: 12px;
                padding: 20px;
                border: 1px solid #e0e0e0;
                min-height: 110px;
            }

            #cardTitle {
                color: #2c3e50;
                font-size: 15px;
                font-weight: bold;
                margin-bottom: 10px;
            }

            #searchInput {
                padding: 10px 15px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
                background-color: #f8f9fa;
            }

            #searchInput:focus {
                border-color: #3498db;
                background-color: #ffffff;
            }

            QPushButton, .QPushButton {
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 13px;
            }

            QPushButton:hover, .QPushButton:hover {
            }
        """)

