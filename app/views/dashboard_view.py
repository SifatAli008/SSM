from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QFrame, QScrollArea, QStackedLayout
)
from PyQt5.QtCore import Qt, QTimer

from views.widgets.card_widget import CardWidget
from views.widgets.alert_widget import AlertWidget
from views.widgets.action_button import ActionButton
from views.widgets.graph_widget import Graph
from views.inventory_view import InventoryView  # Assuming this exists


class DashboardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        main_layout.addWidget(self.create_alert_bar())

        # Central area with stack
        self.stack_layout = QStackedLayout()
        self.dashboard_widget = self.create_scroll_area()
        self.inventory_widget = InventoryView()

        self.stack_layout.addWidget(self.dashboard_widget)
        self.stack_layout.addWidget(self.inventory_widget)

        central_widget = QWidget()
        central_widget.setLayout(self.stack_layout)
        main_layout.addWidget(central_widget)

        main_layout.addWidget(self.create_footer())
        self.apply_stylesheets()

    def create_alert_bar(self):
        alert_bar = QFrame()
        alert_bar.setObjectName("alertBar")
        alert_bar.setFixedHeight(40)

        layout = QHBoxLayout(alert_bar)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(15)

        layout.addWidget(AlertWidget("Low Stock: 3 items", color="#f9c74f"))
        layout.addWidget(AlertWidget("Pending Orders: 2", color="#f8961e"))
        layout.addWidget(AlertWidget("Security Alert: 1", color="#f94144"))
        layout.addStretch()

        return alert_bar

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
        return scroll_area

    def create_top_metrics(self):
        layout = QHBoxLayout()
        layout.setSpacing(20)

        layout.addWidget(CardWidget("Total Revenue", "$5,000", "Last 7 Days: 12%↑"))
        layout.addWidget(CardWidget("Customer Traffic", "320", "Peak Hour: 5-6 PM"))
        layout.addWidget(CardWidget("Pending Orders", "5", "Deliveries: 3 Today"))

        return layout

    def create_graphs(self):
        layout = QHBoxLayout()
        layout.setSpacing(20)

        layout.addWidget(Graph("Sales Trend", "Weekly | Monthly"))
        layout.addWidget(Graph("Stock Levels", "Inventory Alerts"))
        layout.addWidget(Graph("Profit & Loss", "Forecast: +5% Growth"))

        return layout

    def create_additional_metrics(self):
        layout = QHBoxLayout()
        layout.setSpacing(20)

        layout.addWidget(CardWidget("Due Payments", "$1,200", "Last 7 Days: 12%↑"))
        layout.addWidget(CardWidget("Stock Info", "500", "Low Stock: 5 items..."))
        layout.addWidget(CardWidget("Customer Returns", "7%", "Satisfaction: 92%↑"))

        return layout

    def create_action_buttons(self):
        layout = QHBoxLayout()
        layout.setSpacing(20)

        # Invoice Section
        invoice_frame = self.build_action_section("Invoice & Billing", [
            ActionButton("View & Print", color="#27ae60")
        ])
        layout.addWidget(invoice_frame)

        # Quick Actions
        quick_actions_frame = self.build_action_section("Quick Actions", [
            ActionButton("Add Product", color="#27ae60"),
            ActionButton("Manage Orders", color="#3498db"),
            self.create_inventory_button()
        ])
        layout.addWidget(quick_actions_frame)

        # Search Stock
        search_stock_frame = QFrame()
        search_stock_frame.setObjectName("card")
        search_stock_layout = QVBoxLayout(search_stock_frame)

        title = QLabel("Search Stock")
        title.setObjectName("cardTitle")
        search_stock_layout.addWidget(title)

        input_field = QLineEdit()
        input_field.setPlaceholderText("Enter product name...")
        input_field.setObjectName("searchInput")
        search_stock_layout.addWidget(input_field)
        search_stock_layout.addStretch()

        layout.addWidget(search_stock_frame)
        return layout

    def create_inventory_button(self):
        btn = ActionButton("View Inventory", color="#9b59b6")
        btn.clicked.connect(self.show_inventory_view)
        return btn

    def show_inventory_view(self):
        self.stack_layout.setCurrentWidget(self.inventory_widget)

    def build_action_section(self, title_text, buttons):
        frame = QFrame()
        frame.setObjectName("card")
        layout = QVBoxLayout(frame)

        title = QLabel(title_text)
        title.setObjectName("cardTitle")
        layout.addWidget(title)

        for btn in buttons:
            layout.addWidget(btn)
        layout.addStretch()
        return frame

    def create_footer(self):
        footer = QFrame()
        footer.setObjectName("footer")
        footer.setFixedHeight(40)

        layout = QHBoxLayout(footer)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(30)

        layout.addWidget(QLabel("System Closed: 08:00 PM"))
        layout.addWidget(QLabel("System Opened: 10:00 AM"))
        layout.addWidget(QLabel("Users Online: 1"))

        self.current_time_label = QLabel()
        layout.addWidget(self.current_time_label)
        layout.addStretch()

        return footer

    def update_time(self):
        self.current_time_label.setText("Current Time: " + datetime.now().strftime("%H:%M:%S"))

    def apply_stylesheets(self):
        self.setStyleSheet("""
        #alertBar {
            background-color: #eef2f3;
            color: #333;
            border-bottom: 1px solid #ccc;
        }

        #card {
            background-color: #ffffff;
            border-radius: 12px;
            padding: 20px;
            border: 1px solid #e0e0e0;
        }

        #cardTitle {
            font-size: 15px;
            font-weight: bold;
            color: #2c3e50;
        }

        #searchInput {
            padding: 8px 12px;
            border: 1px solid #ccc;
            border-radius: 6px;
        }

        #footer {
            background-color: #f9f9f9;
            border-top: 1px solid #dcdcdc;
            color: #7f8c8d;
            font-size: 12px;
        }
        """)
