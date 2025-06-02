from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QScrollArea, QStackedLayout,
    QSizePolicy, QGraphicsDropShadowEffect, QMessageBox, QGridLayout, QProgressBar, QCheckBox
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QIcon, QPainter, QPen, QBrush

# Import our custom components
from app.views.widgets.components import Card, Button, PageHeader
from app.views.widgets.layouts import DashboardLayout, CardGrid
from app.utils.theme_manager import ThemeManager

# Keep original widget imports for backward compatibility
from app.views.widgets.card_widget import CardWidget

# Import enhanced visualization widgets
from app.views.widgets.enhanced_graph import EnhancedGraph
from app.views.widgets.enhanced_activity import EnhancedActivity

# Deprecated - keep for backward compatibility
# from app.views.widgets.graph_widget import Graph
from app.views.inventory_view import InventoryView

# Controllers for database access
from app.controllers.inventory_controller import InventoryController
from app.utils.database import DatabaseManager
from app.utils.event_system import global_event_system
from datetime import datetime, timedelta

# Replace all data access with InventoryManager and SalesManager methods
# Example: inventory_manager = InventoryManager()
# Use inventory_manager.list_products(), sales_manager.list_sales(), etc. for all dashboard data

from app.core.inventory import InventoryManager
from app.core.sales import SalesManager




class DashboardPage(QWidget):
    """
    Dashboard page using the new component system
    """
    data_refreshed = pyqtSignal()
    error_occurred = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.setup_animations()
        self.setup_data_controllers()
        self.setup_event_listeners()
        self.setup_refresh_timer()
        self.update_summary_cards()
        self.update_recent_activities()
    
    def setup_data_controllers(self):
        self.inventory_manager = InventoryManager(None)
        self.sales_manager = SalesManager(None)
    
    def setup_event_listeners(self):
        """Set up listeners for the global event system"""
        # Listen for inventory updates
        global_event_system.inventory_updated.connect(self.on_inventory_updated)
        
        # Listen for sales updates
        global_event_system.sales_updated.connect(self.on_sales_updated)
        
        # Listen for customer updates
        global_event_system.customer_updated.connect(self.on_customer_updated)

    def on_inventory_updated(self, data):
        """Handle inventory update events"""
        action = data.get('action', 'unknown')
        product = data.get('product', {})
        
        if action == 'add':
            product_name = product.get('name', 'Unknown product')
            product_category = product.get('category', 'Unknown category')
            product_quantity = product.get('quantity', 0)
            
            # Adding a product might affect low stock count
            low_stock_count = self.get_low_stock_count()
            self.stock_graph.set_title("Stock Flow", f"Low Stock: {low_stock_count} items")
            
            # Update inventory value
            inventory_value = self.get_inventory_value()
            self.profit_graph.set_title("Profit Analysis", f"Inventory Value: ${inventory_value:,.2f}")
            
        elif action == 'delete':
            product_name = product.get('name', 'Unknown product')
            
            # Deleting a product affects inventory value
            inventory_value = self.get_inventory_value()
            self.profit_graph.set_title("Profit Analysis", f"Inventory Value: ${inventory_value:,.2f}")
            
            # May also affect low stock count
            low_stock_count = self.get_low_stock_count()
            self.stock_graph.set_title("Stock Flow", f"Low Stock: {low_stock_count} items")
            
        elif action == 'update':
            product_name = product.get('name', 'Unknown product')
            quantity = product.get('quantity', 'unknown quantity')
            
            # Update stock count and value if quantity changed
            low_stock_count = self.get_low_stock_count()
            self.stock_graph.set_title("Stock Flow", f"Low Stock: {low_stock_count} items")
            self.stock_graph.update_indicator(f"{low_stock_count} items", "#e67e22")
            
            inventory_value = self.get_inventory_value()
            self.profit_graph.set_title("Profit Analysis", f"Inventory Value: ${inventory_value:,.2f}")
            
        elif action == 'sale_impact':
            # Inventory changed due to a sale
            sale_id = data.get('sale_id', None)
            
            # Update stock levels
            low_stock_count = self.get_low_stock_count()
            self.stock_graph.set_title("Stock Flow", f"Low Stock: {low_stock_count} items")
            
            # Update inventory value
            inventory_value = self.get_inventory_value()
            self.profit_graph.set_title("Profit Analysis", f"Inventory Value: ${inventory_value:,.2f}")
        
        # Update metrics that depend on inventory
        self.update_summary_cards()
        
        # Update recent activities to show inventory changes
        self.update_recent_activities()

    def on_sales_updated(self, data):
        """Handle sales update events"""
        action = data.get('action', 'unknown')
        sale = data.get('sale', {})
        
        if action == 'add':
            customer = sale.get('customer', 'Unknown customer')
            amount = sale.get('total', 0)
            
        elif action == 'update':
            sale_id = sale.get('id', 'Unknown ID')
            amount = sale.get('total', 0)
        
        elif action == 'delete':
            sale_id = sale.get('id', 'Unknown ID')
        
        # Update revenue metrics with real-time data
        total_revenue = self.get_total_revenue()
        weekly_change = self.get_revenue_weekly_change()
        change_text = f"Last 7 Days: {weekly_change:.1f}%{'↑' if weekly_change >= 0 else '↓'}"
        self.revenue_card.update_values(f"${total_revenue:,.2f}", change_text)
        
        # Update indicator color based on trend
        color = "#27ae60" if weekly_change >= 0 else "#e74c3c"
        self.sales_graph.update_indicator(f"{weekly_change:+.1f}%", color)
        
        # Update pending orders
        pending_orders = self.get_pending_orders()
        deliveries = self.get_todays_deliveries()
        self.orders_card.update_values(f"{pending_orders}", f"Deliveries: {deliveries} Today")
        
        # Update activities to show new sales activity
        self.update_recent_activities()

    def on_customer_updated(self, data):
        """Handle customer update events"""
        action = data.get('action', 'unknown')
        customer = data.get('customer', {})
        
        if action == 'add':
            customer_name = customer.get('name', 'Unknown customer')
            
        elif action == 'update':
            customer_id = customer.get('id', 'Unknown ID')
            customer_name = customer.get('name', 'Unknown customer')
        
        elif action == 'delete':
            customer_id = customer.get('id', 'Unknown ID')
        
        # Update customer metrics with real-time data
        customer_count = self.get_customer_count()
        self.customer_card.update_values(f"{customer_count}", "Active Customers")
        
        # Update activities to show customer activity
        self.update_recent_activities()

    def setup_refresh_timer(self):
        """Set up a timer to refresh data periodically"""
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_dashboard_data)
        self.refresh_timer.start(60000)  # Refresh every 60 seconds

    def refresh_dashboard_data(self):
        """Refresh all dashboard data to ensure real-time updates"""
        try:
            # Update revenue metrics
            total_revenue = self.get_total_revenue()
            weekly_change = self.get_revenue_weekly_change()
            change_text = f"Last 7 Days: {weekly_change:.1f}%{'↑' if weekly_change >= 0 else '↓'}"
            self.revenue_card.update_values(f"${total_revenue:,.2f}", change_text)
            
            # Update indicator color based on trend
            color = "#27ae60" if weekly_change >= 0 else "#e74c3c"  # Green if positive, red if negative
            self.sales_graph.update_indicator(f"{weekly_change:+.1f}%", color)
            
            # Update sales chart with real data 
            sales_data = self.get_weekly_sales_data()
            if sales_data:
                self.sales_graph.set_data(sales_data.get('data', []), sales_data.get('labels', []), chart_type='line', color="#2ecc71")
            
            # Update customer metrics
            customer_count = self.get_customer_count()
            self.customer_card.update_values(f"{customer_count}", "Active Customers")
            
            # Update pending orders
            pending_orders = self.get_pending_orders()
            deliveries = self.get_todays_deliveries()
            self.orders_card.update_values(f"{pending_orders}", f"Deliveries: {deliveries} Today")
            
            # Update stock flow chart
            low_stock_count = self.get_low_stock_count()
            self.stock_graph.set_title("Stock Flow", f"Low Stock: {low_stock_count} items")
            stock_flow_data = self.get_stock_flow_data()
            if isinstance(stock_flow_data, dict) and 'data' in stock_flow_data and 'labels' in stock_flow_data:
                self.stock_graph.set_data(stock_flow_data['data'], stock_flow_data['labels'], chart_type='bar', color="#f39c12")
            else:
                self.stock_graph.set_data(stock_flow_data, chart_type='bar', color="#f39c12")
            self.stock_graph.update_indicator(f"{low_stock_count} Low", "#f39c12")
            
            # Update profit chart with quarterly data
            inventory_value = self.get_inventory_value()
            self.profit_graph.set_title("Quarterly Profit", f"Inventory Value: ${inventory_value:,.2f}")
            profit_data = self.get_quarterly_profit_data()
            self.profit_graph.set_data(profit_data.get('data', []), profit_data.get('labels', []), chart_type='bar', color="#9b59b6")
            self.profit_graph.update_indicator(f"${inventory_value:,.2f}", "#9b59b6")
            
            # Update recent activities
            self.update_recent_activities()
            
        except Exception as e:
            pass
        
        return True
    
    def update_summary_cards(self):
        """Update summary cards with real data"""
        # Update revenue card
        total_revenue = self.get_total_revenue()
        if not total_revenue:
            total_revenue = 0.0
        weekly_change = self.get_revenue_weekly_change()
        change_text = f"Last 7 Days: {weekly_change:.1f}%{'↑' if weekly_change >= 0 else '↓'}"
        self.revenue_card.update_values(f"${total_revenue:,.2f}", change_text)
        
        # Update customer card
        customer_count = self.get_customer_count()
        if not customer_count:
            customer_count = 0
        self.customer_card.update_values(f"{customer_count}", "Active Customers")
        
        # Update orders card
        pending_orders = self.get_pending_orders()
        if not pending_orders:
            pending_orders = 0
        deliveries = self.get_todays_deliveries()
        if not deliveries:
            deliveries = 0
        self.orders_card.update_values(f"{pending_orders}", f"Deliveries: {deliveries} Today")

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
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.setSpacing(32)

        # Header row: title/subtitle on left, actions on right
        header_row = QHBoxLayout()
        header_row.setContentsMargins(0, 0, 0, 0)
        header_row.setSpacing(0)
        header_col = QVBoxLayout()
        header_col.setSpacing(2)
        header_title = QLabel("Dashboard Overview")
        header_title.setObjectName("page-title")
        header_title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        header_col.addWidget(header_title)
        header_subtitle = QLabel("View and manage your business at a glance")
        header_subtitle.setStyleSheet("color: #888; font-size: 15px;")
        header_col.addWidget(header_subtitle)
        header_row.addLayout(header_col, 1)
        header_row.addStretch()
        self.add_product_btn = Button("Add Product", variant="primary")
        self.add_product_btn.clicked.connect(self.add_new_product)
        self.add_product_btn.setToolTip("Add a new product to inventory")
        self.add_product_btn.setAccessibleName("Add Product Button")
        header_row.addWidget(self.add_product_btn)
        self.refresh_btn = Button("Refresh Data", variant="secondary")
        self.refresh_btn.clicked.connect(self.refresh_dashboard_data)
        self.refresh_btn.setToolTip("Refresh dashboard data")
        self.refresh_btn.setAccessibleName("Refresh Data Button")
        header_row.addWidget(self.refresh_btn)
        content_layout.addLayout(header_row)
        content_layout.addSpacing(4)
        # Add loading bar
        self.loading_bar = QProgressBar()
        self.loading_bar.setVisible(False)
        self.loading_bar.setTextVisible(False)
        self.loading_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background: #f0f0f0;
                height: 4px;
            }
            QProgressBar::chunk {
                background: #3498db;
            }
        """)
        content_layout.addWidget(self.loading_bar)
        # Add last updated label
        self.last_updated_label = QLabel()
        self.last_updated_label.setStyleSheet("color: #888; font-size: 12px; margin-bottom: 8px;")
        content_layout.addWidget(self.last_updated_label)
        # --- Move toggles and divider here ---
        customize_label = QLabel("Customize Dashboard")
        customize_label.setStyleSheet("font-weight: bold; font-size: 15px; margin-bottom: 8px;")
        content_layout.addWidget(customize_label)
        self.toggle_layout = QHBoxLayout()
        self.toggle_layout.setSpacing(24)
        self.toggle_layout.setContentsMargins(12, 8, 12, 8)
        self.toggle_layout.addStretch()
        self.toggle_cards = {}
        toggle_items = [
            ("Show Revenue", "revenue_card", "💰"),
            ("Show Customers", "customer_card", "👥"),
            ("Show Orders", "orders_card", "📦"),
            ("Show Sales Graph", "sales_graph", "📈"),
            ("Show Stock Graph", "stock_graph", "📊"),
            ("Show Profit Graph", "profit_graph", "💹"),
        ]
        for label, widget, icon in toggle_items:
            cb = QCheckBox(f"{icon} {label}")
            cb.setChecked(True)
            cb.setToolTip(f"Toggle {label.lower()} on dashboard")
            cb.setAccessibleName(label)
            cb.stateChanged.connect(lambda state, w=widget: self.toggle_dashboard_widget(w, state))
            self.toggle_layout.addWidget(cb)
            self.toggle_cards[widget] = cb
        self.toggle_layout.addStretch()
        toggle_bar = QFrame()
        toggle_bar.setLayout(self.toggle_layout)
        toggle_bar.setStyleSheet("""
            QFrame {
                background: #f8fafd;
                border-radius: 12px;
                border: 1px solid #e0e6ed;
                margin-bottom: 8px;
            }
        """)
        content_layout.addWidget(toggle_bar)
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        divider.setStyleSheet("margin-bottom: 12px; margin-top: 0px; color: #e0e6ed;")
        content_layout.addWidget(divider)
        # --- Section: Summary ---
        summary_label = QLabel("Summary")
        summary_label.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 8px; margin-top: 8px;")
        content_layout.addWidget(summary_label)
        summary_divider = QFrame()
        summary_divider.setFrameShape(QFrame.HLine)
        summary_divider.setFrameShadow(QFrame.Sunken)
        summary_divider.setStyleSheet("margin-bottom: 12px; margin-top: 0px; color: #e0e6ed;")
        content_layout.addWidget(summary_divider)
        # Dashboard layout with metrics and charts
        dashboard = DashboardLayout()
        dashboard.set_columns(3)
        # Add summary cards (top metrics)
        self.revenue_card = CardWidget(
            "Total Revenue",
            "$0.00",
            "Loading...",
            icon="💰",
            color="#2ecc71"
        )
        self.customer_card = CardWidget(
            "Customer Traffic",
            "0",
            "Loading...",
            icon="👥",
            color="#3498db"
        )
        self.orders_card = CardWidget(
            "Pending Orders",
            "0",
            "Loading...",
            icon="📦",
            color="#e74c3c"
        )
        dashboard.add_summary_card(self.revenue_card)
        dashboard.add_summary_card(self.customer_card)
        dashboard.add_summary_card(self.orders_card)
        content_layout.addWidget(dashboard)
        # --- Section: Performance Charts ---
        # Add graphs section
        graphs_section = Card("Performance Charts")
        graphs_section.setStyleSheet("""
            background-color: #e0f7fa; /* TEMP: for debugging bounds */
            border-radius: 18px;
            border: none;
            padding-top: 8px;
            padding-bottom: 8px;
            margin-top: 0px;
            margin-bottom: 0px;
        """)
        graphs_section.setMinimumHeight(340)
        graphs_section.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Arrange graphs in a row and add to the Card's layout
        graphs_row = QHBoxLayout()
        graphs_row.setSpacing(32)
        self.sales_graph = EnhancedGraph()
        self.sales_graph.set_title("Sales Trend", "Weekly Sales Data")
        sales_data = self.get_weekly_sales_data()
        self.sales_graph.set_data(sales_data.get('data', []), sales_data.get('labels', []), chart_type='line', color="#2ecc71")
        self.sales_graph.setMinimumHeight(320)
        self.sales_graph.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        weekly_change = self.get_revenue_weekly_change()
        change_color = "#27ae60" if weekly_change >= 0 else "#e74c3c"
        self.sales_graph.update_indicator(f"{weekly_change:+.1f}%", change_color)
        self.sales_graph.set_on_click(self.navigate_to_reports)
        
        self.stock_graph = EnhancedGraph()
        low_stock_count = self.get_low_stock_count()
        self.stock_graph.set_title("Stock Flow", f"Low Stock: {low_stock_count} items")
        stock_data = self.get_stock_flow_data()
        if isinstance(stock_data, dict) and 'data' in stock_data and 'labels' in stock_data:
            self.stock_graph.set_data(stock_data['data'], stock_data['labels'], chart_type='bar', color="#f39c12")
        else:
            self.stock_graph.set_data(stock_data, chart_type='bar', color="#f39c12")
        self.stock_graph.setMinimumHeight(320)
        self.stock_graph.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.stock_graph.update_indicator(f"{low_stock_count} Low", "#f39c12")
        self.stock_graph.set_on_click(lambda: self.navigate_to_page(1))
        
        self.profit_graph = EnhancedGraph()
        inventory_value = self.get_inventory_value()
        self.profit_graph.set_title("Quarterly Profit", f"Inventory Value: ${inventory_value:,.2f}")
        profit_data = self.get_quarterly_profit_data()
        self.profit_graph.set_data(profit_data.get('data', []), profit_data.get('labels', []), chart_type='bar', color="#9b59b6")
        self.profit_graph.setMinimumHeight(320)
        self.profit_graph.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.profit_graph.update_indicator(f"${inventory_value:,.2f}", "#9b59b6")
        self.profit_graph.set_on_click(self.navigate_to_reports)
        graphs_row.addWidget(self.sales_graph)
        graphs_row.addWidget(self.stock_graph)
        graphs_row.addWidget(self.profit_graph)
        graphs_section.layout.addLayout(graphs_row)
        content_layout.addWidget(graphs_section)
        # Add quick actions section
        actions_section = Card("Quick Actions")
        actions_section.setStyleSheet("""
            background-color: #ffffff;
            border-radius: 18px;
            border: none;
        """)
        actions_grid = QHBoxLayout()
        actions_grid.setContentsMargins(20, 20, 20, 20)
        actions_grid.setSpacing(20)
        inventory_btn = Button("View Inventory", "📦", "primary")
        sales_btn = Button("Process Sale", "💰", "success")
        customers_btn = Button("Manage Customers", "👥", "secondary")
        reports_btn = Button("Generate Reports", "📊", "info")
        
        # Connect button click events
        inventory_btn.clicked.connect(lambda: self.navigate_to_page(1))  # Inventory page
        sales_btn.clicked.connect(lambda: self.navigate_to_page(2))      # Sales page
        customers_btn.clicked.connect(lambda: self.navigate_to_page(3))  # Customers page
        reports_btn.clicked.connect(self.navigate_to_reports)            # Reports page
        
        actions_grid.addWidget(inventory_btn)
        actions_grid.addWidget(sales_btn)
        actions_grid.addWidget(customers_btn)
        actions_grid.addWidget(reports_btn)
        actions_section.layout.addLayout(actions_grid)
        content_layout.addWidget(actions_section)
        self.activity_widget = EnhancedActivity()
        self.activity_widget.activity_clicked.connect(self.handle_activity_click)
        content_layout.addWidget(self.activity_widget)
        # If all toggles are off, show a message
        self.no_widgets_label = QLabel("No widgets selected. Use the toggles above to customize your dashboard.")
        self.no_widgets_label.setStyleSheet("color: #888; font-size: 16px; margin: 32px 0px 0px 0px; text-align: center;")
        self.no_widgets_label.setAlignment(Qt.AlignCenter)
        self.no_widgets_label.setVisible(False)
        content_layout.addWidget(self.no_widgets_label)
        # Create scrollable area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(content_widget)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        main_layout.addWidget(scroll_area)
        self.data_refreshed.connect(self.on_data_refreshed)
        self.error_occurred.connect(self.on_error_occurred)

    def toggle_dashboard_widget(self, widget_name, state):
        widget = getattr(self, widget_name, None)
        if widget:
            widget.setVisible(bool(state))
        # Show/hide the 'no widgets' label if all toggles are off
        if all(not cb.isChecked() for cb in self.toggle_cards.values()):
            self.no_widgets_label.setVisible(True)
        else:
            self.no_widgets_label.setVisible(False)

    def get_low_stock_count(self):
        """Get count of items with low stock"""
        if hasattr(self, 'inventory_manager'):
            return self.inventory_manager.count_low_stock(threshold=10)
        return 0

    def get_inventory_value(self):
        """Get total inventory value"""
        if hasattr(self, 'inventory_manager'):
            return self.inventory_manager.calculate_inventory_value()
        return 0

    def get_total_revenue(self):
        try:
            summary = self.sales_manager.get_sales_summary()
            return summary.get('total_revenue', 0.0)
        except Exception:
            return 0.0

    def get_revenue_weekly_change(self):
        try:
            sales = self.sales_manager.list_sales()
            if not sales:
                return 0.0
            # Group sales by week
            from datetime import datetime, timedelta
            now = datetime.now()
            week_ago = now - timedelta(days=7)
            prev_week_ago = now - timedelta(days=14)
            curr_week_sales = [s for s in sales if hasattr(s, 'sale_date') and week_ago <= pd.to_datetime(s.sale_date) <= now]
            prev_week_sales = [s for s in sales if hasattr(s, 'sale_date') and prev_week_ago <= pd.to_datetime(s.sale_date) < week_ago]
            curr_revenue = sum(s.total_price for s in curr_week_sales)
            prev_revenue = sum(s.total_price for s in prev_week_sales)
            if prev_revenue > 0:
                return ((curr_revenue - prev_revenue) / prev_revenue) * 100
            elif curr_revenue > 0:
                return 100.0
            else:
                return 0.0
        except Exception:
            return 0.0

    def get_customer_count(self):
        try:
            customers_obj = get_db().child('customers').get()
            customers = customers_obj.val() if hasattr(customers_obj, 'val') else customers_obj or {}
            return len(customers)
        except Exception:
            return 0

    def get_pending_orders(self):
        try:
            sales = self.sales_manager.list_sales()
            return sum(1 for s in sales if getattr(s, 'status', '').lower() == 'pending' or getattr(s, 'due_amount', 0) > 0)
        except Exception:
            return 0

    def get_todays_deliveries(self):
        try:
            sales = self.sales_manager.list_sales()
            today = datetime.now().strftime('%Y-%m-%d')
            return sum(1 for s in sales if hasattr(s, 'delivery_date') and getattr(s, 'delivery_date', '') == today)
        except Exception:
            return 0

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
            pass

    def navigate_to_reports(self):
        """Navigate directly to reports page"""
        self.navigate_to_page(4)

    def add_new_product(self):
        """Navigate to inventory page and show add product dialog"""
        main_window = self.get_main_window()
        if main_window:
            # Navigate to inventory page
            self.navigate_to_page(1)
            
            # Find the inventory view
            inventory_view = None
            for i in range(main_window.content_stack.count()):
                widget = main_window.content_stack.widget(i)
                if hasattr(widget, 'show_add_product_dialog'):
                    inventory_view = widget
                    break
            
            # Show add product dialog after a short delay
            if inventory_view:
                QTimer.singleShot(100, inventory_view.show_add_product_dialog)
            else:
                pass

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
            pass
            return
            
        # Find the reports view in the content stack
        reports_view = None
        for i in range(main_window.content_stack.count()):
            widget = main_window.content_stack.widget(i)
            if hasattr(widget, 'generate_sales_report'):
                reports_view = widget
                break
        
        if not reports_view:
            pass
            return
            
        # Call the appropriate method based on button clicked
        if clicked_btn == sales_btn:
            reports_view.generate_sales_report()
        elif clicked_btn == inventory_btn:
            reports_view.generate_inventory_report()
        elif clicked_btn == financial_btn:
            reports_view.generate_financial_report()

    def update_recent_activities(self):
        """Update the recent activities section with latest data"""
        try:
            # Clear existing activities
            self.activity_widget.clear_activities()
            
            # Get recent activities from database
            activities = self.get_recent_activities()
            
            # Update the activity widget with real data
            self.activity_widget.update_activities(activities)
            
        except Exception as e:
            pass

    def handle_activity_click(self, activity_type, item_id):
        """Handle clicks on activity items by navigating to the related screen"""
        if activity_type == "sale":
            # Navigate to sales page
            self.navigate_to_page(2)
            # Ideally, we would also select the specific sale in the sales view
            
        elif activity_type == "inventory":
            # Navigate to inventory page
            self.navigate_to_page(1)
            # Ideally, we would also select the specific inventory item
            
        elif activity_type == "customer":
            # Navigate to customers page
            self.navigate_to_page(3)
            # Ideally, we would also select the specific customer
            
        elif activity_type == "alert":
            # Navigate to inventory page (for low stock alerts)
            self.navigate_to_page(1)
            # Ideally, we would filter for low stock items

    def get_recent_activities(self):
        activities = []
        try:
            sales = self.sales_manager.list_sales()
            for s in sorted(sales, key=lambda x: getattr(x, 'sale_date', ''), reverse=True)[:4]:
                activities.append({
                    "icon": "💰",
                    "title": f"Sale to {getattr(s, 'customer_name', 'Unknown')}",
                    "value": f"${getattr(s, 'total_price', 0):.2f}",
                    "time": getattr(s, 'sale_date', ''),
                    "activity_type": "sale",
                    "item_id": getattr(s, 'id', None)
                })
            inventory = self.inventory_manager.list_products()
            for p in inventory[:3]:
                activities.append({
                    "icon": "📦",
                    "title": "Inventory Updated",
                    "value": getattr(p, 'name', 'Unknown'),
                    "time": getattr(p, 'created_at', ''),
                    "activity_type": "inventory",
                    "item_id": getattr(p, 'id', None)
                })
            customers_obj = get_db().child('customers').get()
            customers = customers_obj.val() if hasattr(customers_obj, 'val') else customers_obj or {}
            for i, (cid, cust) in enumerate(list(customers.items())[:2]):
                activities.append({
                    "icon": "👤",
                    "title": "New Customer",
                    "value": cust.get('name', 'Unknown'),
                    "time": cust.get('joined', ''),
                    "activity_type": "customer",
                    "item_id": cid
                })
        except Exception:
            pass
        return activities

    def time_value(self, time_str):
        """Convert time string to numeric value for sorting"""
        try:
            if isinstance(time_str, (int, float)):
                return float(time_str)
            if 'minute' in time_str:
                return float(time_str.split()[0]) / (24 * 60)
            elif 'hour' in time_str:
                return float(time_str.split()[0]) / 24
            elif 'day' in time_str:
                return float(time_str.split()[0])
            elif 'Recent' in time_str:  # Handle "Recently" case
                return 0.01  # Very recent
            else:
                return 0  # Default case
        except (ValueError, IndexError):
            # Default value if parsing fails
            return 0
    
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

    def get_weekly_sales_data(self):
        try:
            sales = self.sales_manager.list_sales()
            from datetime import datetime, timedelta
            now = datetime.now()
            labels = [(now - timedelta(days=i)).strftime('%a') for i in range(6, -1, -1)]
            data = [0]*7
            for s in sales:
                if hasattr(s, 'sale_date'):
                    idx = (now - pd.to_datetime(s.sale_date)).days
                    if 0 <= idx < 7:
                        data[6-idx] += getattr(s, 'total_price', 0)
            return {"labels": labels, "data": data}
        except Exception:
            return {"labels": [], "data": []}

    def get_stock_flow_data(self):
        try:
            products = self.inventory_manager.list_products()
            low = sum(1 for p in products if (getattr(p, 'quantity', 0) or 0) < 5)
            medium = sum(1 for p in products if 5 <= (getattr(p, 'quantity', 0) or 0) < 20)
            high = sum(1 for p in products if (getattr(p, 'quantity', 0) or 0) >= 20)
            orders = self.get_pending_orders()
            return {"labels": ["Low", "Medium", "High", "Orders"], "data": [low, medium, high, orders]}
        except Exception:
            return {"labels": [], "data": []}

    def get_quarterly_profit_data(self):
        try:
            sales = self.sales_manager.list_sales()
            from datetime import datetime
            now = datetime.now()
            quarters = [((now.month-1)//3+1)-i for i in range(4)]
            data = [0]*4
            labels = [f"Q{q}" for q in reversed(quarters)]
            for s in sales:
                if hasattr(s, 'sale_date'):
                    month = pd.to_datetime(s.sale_date).month
                    q = (month-1)//3
                    idx = 3-q if 0 <= q < 4 else 0
                    data[idx] += getattr(s, 'total_price', 0)
            return {"labels": labels, "data": data}
        except Exception:
            return {"labels": [], "data": []}

    def on_data_refreshed(self):
        # Update the last updated label
        self.last_updated_label.setText(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    def on_error_occurred(self, error_message):
        pass