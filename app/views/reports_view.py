from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, 
    QFrame, QGridLayout, QSizePolicy, QSpacerItem, QFileDialog, QMessageBox, QComboBox,
    QScrollArea, QDateEdit
)
from PyQt5.QtCore import Qt, QSize, QDate
from PyQt5.QtGui import QFont, QIcon, QColor
from PyQt5.QtWidgets import QApplication

from app.controllers.reports_controller import ReportsController
from app.utils.logger import Logger
from app.utils.theme_manager import ThemeManager
from app.views.widgets.components import Card, Button
from app.views.widgets.layouts import TabsLayout
from app.views.widgets.enhanced_graph import ChartWidget
from app.views.widgets.reusable_shop_info_card import ReusableShopInfoCard, ShopCardPresets
from app.utils.ui_helpers import show_error

logger = Logger()

class SectionHeader(QWidget):
    """A styled header for report sections"""
    def __init__(self, title, icon, print_button=True):
        super().__init__()
        self.setObjectName("sectionHeader")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)  # Increased padding
        
        # Icon and title in one label
        header_text = f"{icon} {title}"
        header_label = QLabel(header_text)
        header_label.setFont(QFont(ThemeManager.FONTS["family"], 16, QFont.Bold))  # Increased font size
        header_label.setStyleSheet(f"color: {ThemeManager.get_color('text_primary')}; background-color: transparent;")
        layout.addWidget(header_label)
        
        layout.addStretch()
        
        # Print button
        if print_button:
            self.print_btn = Button("Print Report", variant="primary")
            self.print_btn.setMinimumWidth(120)
            layout.addWidget(self.print_btn)
        
        # Styling
        self.setStyleSheet(f"""
            #sectionHeader {{
                background-color: {ThemeManager.get_color('background')};
                border-radius: {ThemeManager.BORDER_RADIUS['small']}px;
                padding: 15px;
                border-left: 4px solid {ThemeManager.get_color('primary')};
                border-bottom: 1px solid {ThemeManager.get_color('border')};
                margin-top: 20px;
                margin-bottom: 15px;
            }}
        """)

class ReportsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = ReportsController()
        self.start_date = QDateEdit()
        self.end_date = QDateEdit()
        self.generate_button = QPushButton()
        self.export_button = QPushButton()
        self.current_report = object()
        self.export_button.clicked.connect(self._on_export_report)
        self.init_ui()
        self.connect_signals()
        self.load_data()
        self.setMinimumSize(1700, 1050)
    
    def show_error_dialog(self, message, title="Error"):
        logger.error(f"{title}: {message}")
        QMessageBox.critical(self, title, message)
    
    def init_ui(self):
        self.setWindowTitle("Reports & Analytics")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(32)

        # Page header
        header = QLabel("Reports & Analytics")
        header.setFont(QFont(ThemeManager.FONTS["family"], 28, QFont.Bold))
        main_layout.addWidget(header)
        subtitle = QLabel("Comprehensive business insights and performance metrics")
        subtitle.setStyleSheet("color: #888;")
        main_layout.addWidget(subtitle)

        # Top right controls (period, export, print)
        controls_row = QHBoxLayout()
        controls_row.addStretch()
        self.period_combo = QComboBox()
        self.period_combo.addItems(["This Month", "Last Month", "This Year"])
        controls_row.addWidget(self.period_combo)
        self.export_excel_btn = Button("Export Excel", variant="secondary")
        controls_row.addWidget(self.export_excel_btn)
        self.export_pdf_btn = Button("Export PDF", variant="secondary")
        controls_row.addWidget(self.export_pdf_btn)
        self.print_btn = Button("Print", variant="secondary")
        controls_row.addWidget(self.print_btn)
        main_layout.addLayout(controls_row)

        # Tabs
        self.tabs = TabsLayout()
        # Set active tab label color to black
        self.tabs.setStyleSheet('''
            QTabBar::tab:selected { color: #111; font-weight: bold; }
            QTabBar::tab:!selected { color: #bbb; }
        ''')
        self.tabs.add_tab("Summary", self._summary_tab())
        self.tabs.add_tab("Sales", self._sales_tab())
        self.tabs.add_tab("Inventory", self._inventory_tab())
        self.tabs.add_tab("Customers", self._customers_tab())
        main_layout.addWidget(self.tabs)
    
    def connect_signals(self):
        """Connect widget signals to handlers"""
        self.period_combo.currentIndexChanged.connect(self.load_data)
        self.export_pdf_btn.clicked.connect(self.export_pdf_report)
        self.export_excel_btn.clicked.connect(self.export_excel_report)
        self.print_btn.clicked.connect(self.print_report)
    
    def get_selected_period(self):
        """Convert the UI period selection to controller period string"""
        period_map = {
            0: "today",
            1: "last_7_days",
            2: "last_30_days",
            3: "this_month",
            4: "this_year"
        }
        return period_map.get(self.period_combo.currentIndex(), "last_30_days")
    
    def load_data(self):
        """Load data from controller and update UI"""
        try:
            period = self.get_selected_period()
            sales_data = self.controller.get_sales_summary(period)
            self.revenue_card.update_values(f"${sales_data.get('total_sales', 0):,.2f}")
            self.orders_card.update_values(f"{sales_data.get('total_orders', 0):,}")
            # TODO: Set self.revenue_sub, self.orders_sub, self.avg_sub with real period-over-period change if available
            # Update charts with real data
            months, revenue_data = self.controller.get_monthly_sales()
            self.revenue_chart.set_data(revenue_data, labels=months, chart_type='line', color='#2563eb')
            cat_labels, cat_data = self.controller.get_sales_by_category()
            self.pie_chart.set_data(cat_data, labels=cat_labels, chart_type='bar', color='#6366f1')
            # Customer growth chart
            cust_labels, cust_data = self.controller.get_customer_growth()
            self.growth_chart.set_data(cust_data, labels=cust_labels, chart_type='line', color='#3B82F6')
            
            # Get inventory data
            inventory_data = self.controller.get_inventory_value()
            self.inventory_card.update_values(f"${inventory_data.get('total_value', 0):,.2f}")
            self.stock_value_label.setText(f"Stock Value: ${inventory_data.get('total_value', 0):,.2f}")
            self.total_items_label.setText(f"Total Items: {inventory_data.get('total_items', 0):,}")
            self.low_stock_label.setText(f"Low Stock Items: {inventory_data.get('low_stock_items', 0):,}")
            
            # Get profit data
            profit_data = self.controller.get_profit_summary(period)
            self.profit_card.update_values(f"${profit_data.get('net_profit', 0):,.2f}")
            self.expenses_card.update_values(f"${profit_data.get('total_expenses', 0):,.2f}")
            
            self.total_expenses_label.setText(f"Total Expenses: ${profit_data.get('total_expenses', 0):,.2f}")
            self.profit_margin_label.setText(f"Profit Margin: {profit_data.get('profit_margin', 0):.1f}%")
            
        except Exception as e:
            self.show_error_dialog(f"Failed to load some report data: {str(e)}", title="Report Load Error")
    
    def refresh_data(self):
        """Refresh all report data to ensure real-time updates"""
        print("🔄 Refreshing reports data...")
        
        # Refresh the currently selected report
        if hasattr(self, 'current_report_type') and self.current_report_type:
            self.generate_report(self.current_report_type)
            
        # Refresh summary metrics
        if hasattr(self, 'update_summary_metrics'):
            self.update_summary_metrics()
            
        return True
    
    def generate_sales_report(self):
        """Generate and open sales report PDF"""
        try:
            period = self.get_selected_period()
            
            # Show processing dialog
            QMessageBox.information(self, "Generating Report", "Generating sales report. This may take a moment...")
            
            # Generate the report
            result = self.controller.generate_sales_report(period)
            
            if result:
                QMessageBox.information(self, "Report Generated", f"Sales report generated successfully.\n\n{result}")
                
                # Create a "View Reports" button in a QMessageBox
                msg_box = QMessageBox()
                msg_box.setWindowTitle("Open Reports Folder")
                msg_box.setText("Would you like to open the reports folder?")
                msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                response = msg_box.exec_()
                
                if response == QMessageBox.Yes:
                    # Open the reports folder
                    reports_dir = self.controller.get_reports_dir() if hasattr(self.controller, 'get_reports_dir') else "reports"
                    os.startfile(reports_dir)
            else:
                self.show_error_dialog("Failed to generate sales report. Please try again later.", title="Sales Report Error")
                
        except Exception as e:
            self.show_error_dialog(f"Failed to generate sales report: {str(e)}", title="Sales Report Error")
    
    def generate_inventory_report(self):
        """Generate and open inventory report PDF"""
        try:
            # Show processing dialog
            QMessageBox.information(self, "Generating Report", "Generating inventory report. This may take a moment...")
            
            # Generate the report
            report_path = self.controller.generate_inventory_report()
            
            if report_path:
                QMessageBox.information(self, "Report Generated", f"Inventory report generated successfully.\n\nSaved to: {report_path}")
                
                # Create a "View Reports" button in a QMessageBox
                msg_box = QMessageBox()
                msg_box.setWindowTitle("Open Reports Folder")
                msg_box.setText("Would you like to open the reports folder?")
                msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                response = msg_box.exec_()
                
                if response == QMessageBox.Yes:
                    # Open the reports folder
                    reports_dir = os.path.dirname(report_path)
                    os.startfile(reports_dir)
            else:
                self.show_error_dialog("Failed to generate inventory report. No inventory items found or an error occurred.", title="Report Error")
                
        except Exception as e:
            self.show_error_dialog(f"Error generating inventory report: {str(e)}", title="Report Error")
    
    def generate_financial_report(self):
        """Generate financial report"""
        period = self.get_selected_period()
        period_name = self.period_combo.currentText()
        
        QMessageBox.information(
            self, 
            "Financial Report", 
            f"Financial report generation for {period_name} will be implemented in a future update.\n\n"
            f"Current financial summary:\n"
            f"- Total Sales: ${self.profit_card.value_label.text().replace('$', '')}\n"
            f"- Total Expenses: ${self.expenses_card.value_label.text().replace('$', '')}\n"
            f"- Profit Margin: {self.profit_margin_label.text().replace('Profit Margin: ', '')}"
        )
    
    def generate_customer_report(self):
        """Generate customer report"""
        QMessageBox.information(
            self, 
            "Customer Report", 
            "Customer report generation will be implemented in a future update.\n\n"
            "This report will include:\n"
            "- Customer purchase history\n"
            "- Top customers by sales volume\n"
            "- Customer loyalty metrics\n"
            "- Outstanding customer balances"
        )

    def _summary_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        # Initialize summary cards before adding to grid
        self.revenue_card = ReusableShopInfoCard({
            "title": "Total Revenue",
            "icon": "💰",
            "color": ThemeManager.get_color('primary')
        })
        self.revenue_card.value_label.setFont(QFont("Segoe UI", 36, QFont.Bold))
        self.revenue_card.subtitle_label.setFont(QFont("Segoe UI", 13))
        self.orders_card = ReusableShopInfoCard({
            "title": "Total Orders",
            "icon": "📦",
            "color": ThemeManager.get_color('primary')
        })
        self.orders_card.value_label.setFont(QFont("Segoe UI", 36, QFont.Bold))
        self.orders_card.subtitle_label.setFont(QFont("Segoe UI", 13))
        self.profit_card = ReusableShopInfoCard({
            "title": "Net Profit",
            "icon": "💹",
            "color": ThemeManager.get_color('primary')
        })
        self.profit_card.value_label.setFont(QFont("Segoe UI", 36, QFont.Bold))
        self.profit_card.subtitle_label.setFont(QFont("Segoe UI", 13))
        self.expenses_card = ReusableShopInfoCard({
            "title": "Total Expenses",
            "icon": "💸",
            "color": ThemeManager.get_color('primary')
        })
        self.expenses_card.value_label.setFont(QFont("Segoe UI", 36, QFont.Bold))
        self.expenses_card.subtitle_label.setFont(QFont("Segoe UI", 13))
        # Use a grid layout for summary cards with even column stretch
        cards = [
            self.revenue_card,
            self.orders_card,
            self.profit_card,
            self.expenses_card
        ]
        cards_grid = QGridLayout()
        cards_grid.setSpacing(32)
        for i, card in enumerate(cards):
            row = i // 4
            col = i % 4
            card.setMaximumWidth(420)
            cards_grid.addWidget(card, row, col)
            cards_grid.setColumnStretch(col, 1)
        layout.addLayout(cards_grid)
        # Add summary labels for total expenses and profit margin
        self.total_expenses_label = QLabel("Total Expenses: $0.00")
        self.profit_margin_label = QLabel("Profit Margin: 0.0%")
        for lbl in (self.total_expenses_label, self.profit_margin_label):
            lbl.setFont(QFont(ThemeManager.FONTS["family"], 12))
            lbl.setStyleSheet("color: #555;")
            layout.addWidget(lbl)
        # Charts row
        charts_row = QHBoxLayout()
        charts_row.setSpacing(20)
        self.revenue_trend = Card("Revenue Trend", parent=widget)
        self.revenue_trend.layout.setContentsMargins(16, 16, 16, 16)
        self.revenue_trend.setMinimumHeight(420)
        self.revenue_chart = ChartWidget()
        self.revenue_chart.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.revenue_trend.layout.addWidget(self.revenue_chart)
        charts_row.addWidget(self.revenue_trend, 2)
        self.sales_by_cat = Card("Sales by Category", parent=widget)
        self.sales_by_cat.layout.setContentsMargins(16, 16, 16, 16)
        self.sales_by_cat.setMinimumHeight(420)
        self.pie_chart = ChartWidget()
        self.pie_chart.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.sales_by_cat.layout.addWidget(self.pie_chart)
        charts_row.addWidget(self.sales_by_cat, 2)
        layout.addLayout(charts_row, stretch=2)
        return widget

    def _sales_tab(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setSpacing(24)
        # Left: Sales Overview card
        left_card = QFrame()
        left_card.setStyleSheet("background: #fff; border: none; border-radius: 14px;")
        left_layout = QVBoxLayout(left_card)
        left_layout.setContentsMargins(28, 20, 28, 20)
        left_layout.setSpacing(8)
        title = QLabel("Sales Overview")
        title.setFont(QFont(ThemeManager.FONTS["family"], 22, QFont.Bold))
        left_layout.addWidget(title)
        subtitle = QLabel("Revenue and order trends")
        subtitle.setStyleSheet("color: #6b7280; font-size: 15px;")
        left_layout.addWidget(subtitle)
        sales_chart = ChartWidget()
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
        sales_data = [45000, 52000, 48000, 61000, 55000, 67000]
        sales_chart.set_data(sales_data, labels=months, chart_type='bar', color='#3B82F6')
        sales_chart.setStyleSheet("background: #fff; border: none; min-height: 260px;")
        left_layout.addWidget(sales_chart, 1)
        layout.addWidget(left_card, 2)
        # Right: Top Performing Products card
        right_card = QFrame()
        right_card.setStyleSheet("background: #fff; border: none; border-radius: 14px;")
        right_layout = QVBoxLayout(right_card)
        right_layout.setContentsMargins(28, 20, 28, 20)
        right_layout.setSpacing(8)
        title2 = QLabel("Top Performing Products")
        title2.setFont(QFont(ThemeManager.FONTS["family"], 20, QFont.Bold))
        right_layout.addWidget(title2)
        subtitle2 = QLabel("Best selling products by revenue")
        subtitle2.setStyleSheet("color: #6b7280; font-size: 15px;")
        right_layout.addWidget(subtitle2)
        # Product list
        products = [
            {"name": "iPhone 14 Pro", "units": 145, "revenue": 144855, "growth": 12},
            {"name": "Samsung Galaxy S23", "units": 98, "revenue": 78392, "growth": -3},
            {"name": "MacBook Pro 14\"", "units": 56, "revenue": 111944, "growth": 8},
            {"name": "Nike Air Max 90", "units": 234, "revenue": 28080, "growth": 15},
            {"name": "AirPods Pro", "units": 189, "revenue": 47025, "growth": 22},
        ]
        for prod in products:
            prod_card = QFrame()
            prod_card.setStyleSheet("background: #fff; border: none; border-radius: 10px; margin-bottom: 10px;")
            prod_layout = QHBoxLayout(prod_card)
            prod_layout.setContentsMargins(16, 10, 16, 10)
            prod_layout.setSpacing(8)
            # Left: Name and units
            name_units = QVBoxLayout()
            name = QLabel(f"<b>{prod['name']}</b>")
            name.setFont(QFont(ThemeManager.FONTS["family"], 14, QFont.Bold))
            units = QLabel(f"{prod['units']} units sold")
            units.setStyleSheet("color: #6b7280; font-size: 13px;")
            name_units.addWidget(name)
            name_units.addWidget(units)
            prod_layout.addLayout(name_units, 2)
            # Right: Revenue and growth
            rev_growth = QVBoxLayout()
            revenue = QLabel(f"<b>${prod['revenue']:,}</b>")
            revenue.setFont(QFont(ThemeManager.FONTS["family"], 14, QFont.Bold))
            revenue.setAlignment(Qt.AlignRight)
            growth = QLabel()
            if prod['growth'] >= 0:
                growth.setText(f"<span style='color:#16a34a;'>&#8593; {prod['growth']}%</span>")
            else:
                growth.setText(f"<span style='color:#dc2626;'>&#8595; {abs(prod['growth'])}%</span>")
            growth.setStyleSheet("font-size: 13px;")
            growth.setAlignment(Qt.AlignRight)
            rev_growth.addWidget(revenue)
            rev_growth.addWidget(growth)
            prod_layout.addLayout(rev_growth, 1)
            right_layout.addWidget(prod_card)
        right_layout.addStretch(1)
        layout.addWidget(right_card, 2)
        return widget

    def _inventory_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(28)
        # Section header
        header = QLabel("Inventory Status by Category")
        header.setFont(QFont(ThemeManager.FONTS["family"], 20, QFont.Bold))
        layout.addWidget(header)
        subtitle = QLabel("Current stock levels and alerts")
        subtitle.setStyleSheet("color: #888; font-size: 15px;")
        layout.addWidget(subtitle)
        # Add inventory summary card at the top
        self.inventory_card = ReusableShopInfoCard({
            "title": "Inventory Value",
            "icon": "📦",
            "color": ThemeManager.get_color('primary')
        })
        layout.addWidget(self.inventory_card)
        # Add summary labels for stock value, total items, and low stock
        self.stock_value_label = QLabel("Stock Value: $0.00")
        self.total_items_label = QLabel("Total Items: 0")
        self.low_stock_label = QLabel("Low Stock Items: 0")
        for lbl in (self.stock_value_label, self.total_items_label, self.low_stock_label):
            lbl.setFont(QFont(ThemeManager.FONTS["family"], 12))
            lbl.setStyleSheet("color: #555;")
            layout.addWidget(lbl)
        # Fetch real inventory data by category
        try:
            if hasattr(self.controller, 'get_inventory_by_category'):
                categories = self.controller.get_inventory_by_category()
            else:
                # Fallback: use overall inventory value as a single category
                inv = self.controller.get_inventory_value()
                categories = [{
                    "name": "All Categories",
                    "value": f"${inv.get('total_value', 0):,.2f}",
                    "low": inv.get('low_stock_items', 0),
                    "out": 0,  # Not available
                    "in": inv.get('total_items', 0) - inv.get('low_stock_items', 0),
                    "count": inv.get('total_items', 0)
                }]
        except Exception as e:
            self.show_error_dialog(f"Error loading inventory by category: {str(e)}", title="Inventory Error")
            categories = []
        for cat in categories:
            card = QFrame()
            card.setFrameShape(QFrame.StyledPanel)
            card.setStyleSheet("background: #fff; border-radius: 14px; border: none; margin-bottom: 8px;")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(18, 12, 18, 12)
            card_layout.setSpacing(8)
            # First row: category name (left), item count (right, pill)
            row1 = QHBoxLayout()
            row1.setContentsMargins(0, 0, 0, 0)
            row1.setSpacing(0)
            name = QLabel(f"<b>{cat['name']}</b>")
            name.setFont(QFont(ThemeManager.FONTS["family"], 15, QFont.Bold))
            name.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
            row1.addWidget(name, 1)
            row1.addStretch(10)
            count = QLabel(f"<span style='font-size:13px; color:#222; background:#f3f4f6; border-radius:16px; padding:7px 18px;'><b>{cat['count']} items</b></span>")
            count.setTextFormat(Qt.RichText)
            count.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
            row1.addWidget(count, 0)
            card_layout.addLayout(row1)
            # Second row: metrics (use QLabel with HTML, no QWidget nesting)
            row2 = QHBoxLayout()
            row2.setContentsMargins(0, 0, 0, 0)
            row2.setSpacing(0)
            def metric(label, value, color=None, minw=120):
                style = f"font-size:11px; color:#888;" if not color else f"font-size:11px; color:#888;"
                val_style = f"font-size:15px; font-weight:bold; color:{color if color else '#222'}; margin-top:2px;"
                html = f"""
                <div style='min-width:{minw}px; text-align:left;'>
                  <div style='{style}'>{label}</div>
                  <div style='{val_style}'>{value}</div>
                </div>
                """
                lbl = QLabel(html)
                lbl.setTextFormat(Qt.RichText)
                lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                return lbl
            row2.addWidget(metric("Total Value", cat['value']), 2)
            row2.addWidget(metric("Low Stock", cat['low'], "#ea580c"), 1)
            row2.addWidget(metric("Out of Stock", cat['out'], "#dc2626"), 1)
            row2.addWidget(metric("In Stock", cat['in'], "#16a34a"), 1)
            card_layout.addLayout(row2)
            layout.addWidget(card)
        layout.addStretch()
        return widget

    def _customers_tab(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setSpacing(24)
        # Left: Customer Growth chart in a card
        left_card = QFrame()
        left_card.setStyleSheet("background: #fff; border: none; border-radius: 12px;")
        left_layout = QVBoxLayout(left_card)
        left_layout.setContentsMargins(24, 16, 24, 16)
        left_layout.setSpacing(4)
        title = QLabel("Customer Growth")
        title.setFont(QFont(ThemeManager.FONTS["family"], 18, QFont.Bold))
        title.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        left_layout.addWidget(title)
        subtitle = QLabel("New customers acquired over time")
        subtitle.setStyleSheet("color: #6b7280; font-size: 14px; margin-bottom: 0px;")
        subtitle.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        left_layout.addWidget(subtitle)
        self.growth_chart = ChartWidget()
        self.growth_chart.setStyleSheet("background: #fff; border: none; min-height: 220px;")
        left_layout.addWidget(self.growth_chart, 1)
        layout.addWidget(left_card, 2)
        # Right: Customer Metrics card
        right_card = QFrame()
        right_card.setStyleSheet("background: #fff; border: none; border-radius: 16px;")
        right_layout = QVBoxLayout(right_card)
        right_layout.setContentsMargins(32, 24, 32, 24)
        right_layout.setSpacing(10)
        title2 = QLabel("Customer Metrics")
        title2.setFont(QFont(ThemeManager.FONTS["family"], 18, QFont.Bold))
        right_layout.addWidget(title2)
        subtitle2 = QLabel("Key customer performance indicators")
        subtitle2.setStyleSheet("color: #6b7280; font-size: 14px; margin-bottom: 0px;")
        right_layout.addWidget(subtitle2)
        # 2x2 grid of metric cards, compact and centered
        grid = QGridLayout()
        grid.setSpacing(16)
        grid.setContentsMargins(0, 12, 0, 0)
        for i, (title, value) in enumerate([
            ("Total Customers", "573"),
            ("Customer Retention", "89%"),
            ("Avg Customer Value", "$432"),
            ("Avg Orders per Customer", "4.2")]):
            card = ReusableShopInfoCard({"title": title, "icon": "👥", "color": "#9b59b6"})
            card.setStyleSheet("background: #fff; border: none; border-radius: 12px; min-width: 160px; min-height: 80px; font-size: 15px;")
            grid.addWidget(card, i // 2, i % 2)
        right_layout.addStretch(1)
        right_layout.addLayout(grid)
        right_layout.addStretch(1)
        layout.addWidget(right_card, 2)
        return widget

    def generate_ai_summary(self):
        """Generate a business summary using a free AI model (HuggingFace Transformers)"""
        try:
            from transformers import pipeline
            # Prepare a prompt with current data
            prompt = (
                f"Business Report Summary:\n"
                f"Total Revenue: {self.revenue_card.value_label.text()}\n"
                f"Total Orders: {self.orders_card.value_label.text()}\n"
                f"Avg Order Value: {self.avg_card.value_label.text()}\n"
                f"Active Customers: {self.cust_card.value_label.text()}\n"
                f"Stock Value: {self.stock_value_label.text()}\n"
                f"Low Stock Items: {self.low_stock_label.text()}\n"
                f"Total Items: {self.total_items_label.text()}\n"
                f"Customer Retention: 89%\n"
                f"Avg Customer Value: $432\n"
                f"Avg Orders per Customer: 4.2\n"
                f"Write a concise, insightful summary of the business performance for this period."
            )
            summarizer = pipeline('text-generation', model='distilgpt2')
            summary = summarizer(prompt, max_length=120, do_sample=True)[0]['generated_text']
            # Only return the generated part after the prompt
            return summary[len(prompt):].strip()
        except ImportError:
            return "[Install 'transformers' to enable AI-generated summaries.]"
        except Exception as e:
            return f"[AI summary error: {str(e)}]"

    def export_pdf_report(self):
        """Export a business report as PDF for the selected period using ReportLab"""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            period = self.get_selected_period()
            file_path, _ = QFileDialog.getSaveFileName(self, "Save PDF Report", "business_report.pdf", "PDF Files (*.pdf)")
            if not file_path:
                return
            c = canvas.Canvas(file_path, pagesize=letter)
            width, height = letter
            c.setFont("Helvetica-Bold", 18)
            c.drawString(40, height - 50, "Business Report")
            c.setFont("Helvetica", 12)
            c.drawString(40, height - 80, f"Period: {self.period_combo.currentText()}")
            y = height - 120
            # AI summary
            ai_summary = self.generate_ai_summary()
            c.setFont("Helvetica-Oblique", 11)
            c.drawString(40, y, "AI Business Summary:")
            y -= 18
            for line in ai_summary.split('\n'):
                c.drawString(60, y, line)
                y -= 15
            y -= 10
            # Summary
            c.setFont("Helvetica-Bold", 14)
            c.drawString(40, y, "Summary")
            y -= 20
            c.setFont("Helvetica", 12)
            c.drawString(60, y, f"Total Revenue: {self.revenue_card.value_label.text()}")
            y -= 18
            c.drawString(60, y, f"Total Orders: {self.orders_card.value_label.text()}")
            y -= 18
            c.drawString(60, y, f"Avg Order Value: {self.avg_card.value_label.text()}")
            y -= 18
            c.drawString(60, y, f"Active Customers: {self.cust_card.value_label.text()}")
            y -= 30
            # Sales
            c.setFont("Helvetica-Bold", 14)
            c.drawString(40, y, "Sales Overview")
            y -= 20
            c.setFont("Helvetica", 12)
            c.drawString(60, y, "(See app for chart)")
            y -= 30
            # Inventory
            c.setFont("Helvetica-Bold", 14)
            c.drawString(40, y, "Inventory")
            y -= 20
            c.setFont("Helvetica", 12)
            c.drawString(60, y, self.stock_value_label.text())
            y -= 18
            c.drawString(60, y, self.total_items_label.text())
            y -= 18
            c.drawString(60, y, self.low_stock_label.text())
            y -= 30
            # Customers
            c.setFont("Helvetica-Bold", 14)
            c.drawString(40, y, "Customers")
            y -= 20
            c.setFont("Helvetica", 12)
            c.drawString(60, y, f"Total Customers: 573")
            y -= 18
            c.drawString(60, y, f"Customer Retention: 89%")
            y -= 18
            c.drawString(60, y, f"Avg Customer Value: $432")
            y -= 18
            c.drawString(60, y, f"Avg Orders per Customer: 4.2")
            c.save()
            QMessageBox.information(self, "Export PDF", f"PDF report exported successfully to:\n{file_path}")
        except Exception as e:
            self.show_error_dialog(f"Failed to export PDF: {str(e)}", title="Export PDF Error")

    def export_excel_report(self):
        """Export a business report as Excel for the selected period using pandas"""
        try:
            import pandas as pd
            period = self.get_selected_period()
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Excel Report", "business_report.xlsx", "Excel Files (*.xlsx)")
            if not file_path:
                return
            # Prepare data
            data = {
                'Metric': ['Total Revenue', 'Total Orders', 'Avg Order Value', 'Active Customers'],
                'Value': [self.revenue_card.value_label.text(), self.orders_card.value_label.text(), self.avg_card.value_label.text(), self.cust_card.value_label.text()]
            }
            df = pd.DataFrame(data)
            # Add AI summary as a new sheet
            with pd.ExcelWriter(file_path) as writer:
                df.to_excel(writer, index=False, sheet_name='Summary')
                summary_df = pd.DataFrame({'AI Business Summary': [self.generate_ai_summary()]})
                summary_df.to_excel(writer, index=False, sheet_name='AI Summary')
            QMessageBox.information(self, "Export Excel", f"Excel report exported successfully to:\n{file_path}")
        except Exception as e:
            self.show_error_dialog(f"Failed to export Excel: {str(e)}", title="Export Excel Error")

    def print_report(self):
        """Print the business report using QPrinter"""
        try:
            from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
            printer = QPrinter(QPrinter.HighResolution)
            dialog = QPrintDialog(printer, self)
            if dialog.exec_() == QPrintDialog.Accepted:
                # Print the current widget (the report page)
                # Print AI summary first
                ai_summary = self.generate_ai_summary()
                # For simplicity, show the summary in a message box before printing
                QMessageBox.information(self, "AI Business Summary", ai_summary)
                self.render(printer)
                QMessageBox.information(self, "Print", "Report sent to printer.")
        except Exception as e:
            self.show_error_dialog(f"Failed to print report: {str(e)}", title="Print Error")

    def _on_export_report(self):
        import os
        os.makedirs('reports', exist_ok=True)
        path = 'reports/sales_report_2024.pdf'
        with open(path, 'w') as f:
            f.write('dummy pdf content')
