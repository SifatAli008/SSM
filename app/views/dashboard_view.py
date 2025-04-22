"""
Smart Shop Manager - Dashboard Page
File: views/dashboard_page.py
"""
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QFrame, QScrollArea)
from PyQt5.QtCore import Qt, QTimer

from views.widgets.card_widget import CardWidget
from views.widgets.alert_widget import AlertWidget
from views.widgets.action_button import ActionButton
from views.widgets.graph_widget import Graph

class DashboardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
        # Update time
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        
    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Alert bar
        alert_bar = self.create_alert_bar()
        main_layout.addWidget(alert_bar)
        
        # Content scroll area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # Add dashboard components
        content_layout.addLayout(self.create_top_metrics())
        content_layout.addLayout(self.create_graphs())
        content_layout.addLayout(self.create_additional_metrics())
        content_layout.addLayout(self.create_action_buttons())
        
        # Make content scrollable
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(content_widget)
        scroll_area.setFrameShape(QFrame.NoFrame)
        main_layout.addWidget(scroll_area)
        
        # Footer
        footer = self.create_footer()
        main_layout.addWidget(footer)
        
        # Apply stylesheets
        self.apply_stylesheets()
        
    def create_alert_bar(self):
        alert_bar = QFrame()
        alert_bar.setObjectName("alertBar")
        alert_bar.setFixedHeight(40)
        
        layout = QHBoxLayout(alert_bar)
        layout.setContentsMargins(20, 0, 20, 0)
        
        # Low stock alert
        low_stock_alert = AlertWidget("Low Stock: 3 items", color="#f0d0ff")
        layout.addWidget(low_stock_alert)
        
        # Pending orders alert
        pending_orders_alert = AlertWidget("Pending Orders: 2", color="#f0d0ff")
        layout.addWidget(pending_orders_alert)
        
        # Security alert
        security_alert = AlertWidget("Security Alert: 1", color="#f0d0ff")
        layout.addWidget(security_alert)
        
        layout.addStretch()
        return alert_bar
    
    def create_top_metrics(self):
        layout = QHBoxLayout()
        
        revenue_card = CardWidget("Total Revenue", "$5,000", "last 7 Days: 12%↑")
        layout.addWidget(revenue_card)
        
        traffic_card = CardWidget("Customer Traffic", "320", "Peak Hour: 5-6 PM")
        layout.addWidget(traffic_card)
        
        orders_card = CardWidget("Pending Orders", "5", "Deliveries: 3 Today")
        layout.addWidget(orders_card)
        
        return layout
    
    def create_graphs(self):
        layout = QHBoxLayout()
        
        sales_graph = Graph("Sales Trend", "weekly | Monthly")
        layout.addWidget(sales_graph)
        
        stock_graph = Graph("Stock Levels", "Inventory Alerts")
        layout.addWidget(stock_graph)
        
        profit_graph = Graph("Profit & Loss", "Forecast: +5% Growth")
        layout.addWidget(profit_graph)
        
        return layout
    
    def create_additional_metrics(self):
        layout = QHBoxLayout()
        
        payments_card = CardWidget("Due Payments", "$1,200", "last 7 Days: 12%↑")
        layout.addWidget(payments_card)
        
        stock_info_card = CardWidget("Stock Info", "500", "Low Stock: 5 items...")
        layout.addWidget(stock_info_card)
        
        returns_card = CardWidget("Customer Returns", "7%", "Satisfaction: 92%↑")
        layout.addWidget(returns_card)
        
        return layout
    
    def create_action_buttons(self):
        layout = QHBoxLayout()
        
        # Invoice & Billing section
        invoice_frame = QFrame()
        invoice_frame.setObjectName("card")
        invoice_layout = QVBoxLayout(invoice_frame)
        
        invoice_title = QLabel("Invoice & Billing")
        invoice_title.setObjectName("cardTitle")
        invoice_layout.addWidget(invoice_title)
        
        view_invoice_btn = ActionButton("View & Print", color="#27ae60")
        invoice_layout.addWidget(view_invoice_btn)
        invoice_layout.addStretch()
        
        layout.addWidget(invoice_frame)
        
        # Quick Actions section
        quick_actions_frame = QFrame()
        quick_actions_frame.setObjectName("card")
        quick_actions_layout = QVBoxLayout(quick_actions_frame)
        
        quick_actions_title = QLabel("Quick Actions")
        quick_actions_title.setObjectName("cardTitle")
        quick_actions_layout.addWidget(quick_actions_title)
        
        add_product_btn = ActionButton("Add Product", color="#27ae60")
        quick_actions_layout.addWidget(add_product_btn)
        
        manage_orders_btn = ActionButton("Manage Orders", color="#3498db")
        quick_actions_layout.addWidget(manage_orders_btn)
        
        quick_actions_layout.addStretch()
        
        layout.addWidget(quick_actions_frame)
        
        # Search Stock section
        search_stock_frame = QFrame()
        search_stock_frame.setObjectName("card")
        search_stock_layout = QVBoxLayout(search_stock_frame)
        
        search_stock_title = QLabel("Search Stock")
        search_stock_title.setObjectName("cardTitle")
        search_stock_layout.addWidget(search_stock_title)
        
        search_stock_input = QLineEdit()
        search_stock_input.setPlaceholderText("Enter Name")
        search_stock_layout.addWidget(search_stock_input)
        
        search_stock_layout.addStretch()
        
        layout.addWidget(search_stock_frame)
        
        return layout
    
    def create_footer(self):
        footer = QFrame()
        footer.setObjectName("footer")
        footer.setFixedHeight(40)
        
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(20, 0, 20, 0)
        
        # System closed time
        closed_time_label = QLabel("Last Day System Closed 08:00PM")
        layout.addWidget(closed_time_label)
        
        # System opened time
        opened_time_label = QLabel("Last Day System Opened 10:00 am")
        layout.addWidget(opened_time_label)
        
        # Current users
        users_label = QLabel("Current user in the system: 1")
        layout.addWidget(users_label)
        
        # Current time (will be updated by timer)
        self.current_time_label = QLabel()
        layout.addWidget(self.current_time_label)
        
        layout.addStretch()
        
        return footer
    
    def update_time(self):
        current_time = datetime.now().strftime("%H:%M:%S")
        self.current_time_label.setText(f"Current Time: {current_time}")
    
    def apply_stylesheets(self):
        # Define component-specific stylesheets
        self.setStyleSheet("""
        #alertBar {
            background-color: #b19cd9;
            color: #4a235a;
        }
        
        #card {
            background-color: white;
            border-radius: 8px;
            padding: 15px;
            border: 1px solid #e0e0e0;
        }
        
        #cardTitle {
            color: #7f8c8d;
            font-size: 14px;
        }
        
        #cardValue {
            color: #2c3e50;
            margin-top: 5px;
        }
        
        #cardSubtitle {
            color: #7f8c8d;
            margin-top: 5px;
        }
        
        #footer {
            background-color: white;
            border-top: 1px solid #e0e0e0;
            color: #7f8c8d;
        }
        """)