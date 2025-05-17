from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, 
    QFrame, QGridLayout, QSizePolicy, QSpacerItem, QFileDialog, QMessageBox, QComboBox,
    QScrollArea
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon, QColor
from PyQt5.QtWidgets import QApplication

from app.controllers.reports_controller import ReportsController
from app.utils.logger import logger
from app.utils.theme_manager import ThemeManager
from app.views.widgets.components import Card, Button
import os

class ReportCard(Card):
    """A styled card for displaying report information"""
    def __init__(self, title, value=None, icon=None, color=None):
        super().__init__(title)
        self.setMinimumHeight(140)  # Increased for better spacing
        
        # Set responsive size policy
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Create a layout for the content
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 10, 0, 0)
        content_layout.setSpacing(8)
        
        # Add icon and value if provided
        if icon:
            title_with_icon = f"{icon} {title}"
            self.title_label.setText(title_with_icon)
            self.title_label.setFont(QFont(ThemeManager.FONTS["family"], 14, QFont.Bold))
        
        # Value display
        if value:
            self.value_label = QLabel(value)
            self.value_label.setStyleSheet(f"color: {color if color else ThemeManager.get_color('primary')}; background-color: transparent; font-weight: bold;")
            self.value_label.setFont(QFont(ThemeManager.FONTS["family"], 24, QFont.Bold))
            self.value_label.setAlignment(Qt.AlignLeft)
        else:
            self.value_label = QLabel()
            self.value_label.setStyleSheet(f"color: {color if color else ThemeManager.get_color('primary')}; background-color: transparent; font-weight: bold;")
            self.value_label.setFont(QFont(ThemeManager.FONTS["family"], 24, QFont.Bold))
            self.value_label.setAlignment(Qt.AlignLeft)
        
        content_layout.addWidget(self.value_label)
        self.layout.addLayout(content_layout)
    
    def update_value(self, value):
        """Update the value displayed in the card"""
        self.value_label.setText(value)

class DetailCard(Card):
    """A responsive card for detailed metrics"""
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumHeight(160)  # Consistent height
        
        # Improve title styling
        self.title_label.setFont(QFont(ThemeManager.FONTS["family"], 14, QFont.Bold))
        
        # Box shadow and hover effect
        self.setStyleSheet(self.styleSheet() + f"""
            QFrame#card:hover {{
                border: 1px solid {ThemeManager.get_color('primary')};
            }}
        """)

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
        self.init_ui()
        self.connect_signals()
        self.load_data()
    
    def init_ui(self):
        self.setWindowTitle("Reports & Analytics")
        
        # Create scrollable area for responsiveness
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        # Container widget for the scroll area
        scroll_content = QWidget()
        
        # Main layout
        main_layout = QVBoxLayout(scroll_content)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(25)  # Increased spacing
        
        # Page title and time period selector
        title_layout = QHBoxLayout()
        
        # Page title
        page_title = QLabel("Reports & Analytics Dashboard")
        page_title.setObjectName("page-title")
        page_title.setFont(QFont(ThemeManager.FONTS["family"], 24, QFont.Bold))  # Fixed size
        title_layout.addWidget(page_title)
        
        title_layout.addStretch()
        
        # Period selector
        period_layout = QHBoxLayout()
        period_layout.setSpacing(10)
        
        period_label = QLabel("Time Period:")
        period_label.setFont(QFont(ThemeManager.FONTS["family"], 13))
        period_label.setStyleSheet("color: #333333;")
        
        self.period_combo = QComboBox()
        self.period_combo.addItems(["Today", "Last 7 Days", "Last 30 Days", "This Month", "This Year"])
        self.period_combo.setCurrentIndex(2)  # Default to Last 30 Days
        self.period_combo.setFixedWidth(150)
        self.period_combo.setMinimumHeight(38)
        self.period_combo.setFont(QFont(ThemeManager.FONTS["family"], 12))
        
        # Refresh button
        self.refresh_btn = Button("Refresh", variant="success")
        self.refresh_btn.setFont(QFont(ThemeManager.FONTS["family"], 12))
        
        period_layout.addWidget(period_label)
        period_layout.addWidget(self.period_combo)
        period_layout.addWidget(self.refresh_btn)
        
        title_layout.addLayout(period_layout)
        main_layout.addLayout(title_layout)
        
        # Summary metrics
        summary_layout = QGridLayout()
        summary_layout.setHorizontalSpacing(20)  # Increased spacing
        summary_layout.setVerticalSpacing(20)
        
        # Create summary cards
        self.sales_card = ReportCard("Total Sales", "$0", "💰", ThemeManager.get_color('warning'))
        self.inventory_card = ReportCard("Inventory Value", "$0", "📦", ThemeManager.get_color('primary'))
        self.profit_card = ReportCard("Net Profit", "$0", "📈", ThemeManager.get_color('success'))
        self.expenses_card = ReportCard("Total Expenses", "$0", "📉", ThemeManager.get_color('danger'))
        
        # Set column stretching for responsiveness
        summary_layout.setColumnStretch(0, 1)
        summary_layout.setColumnStretch(1, 1)
        
        summary_layout.addWidget(self.sales_card, 0, 0)
        summary_layout.addWidget(self.inventory_card, 0, 1)
        summary_layout.addWidget(self.profit_card, 1, 0)
        summary_layout.addWidget(self.expenses_card, 1, 1)
        
        main_layout.addLayout(summary_layout)
        
        # Sales Reports Section
        sales_header = SectionHeader("SALES REPORTS", "📊")
        sales_header.print_btn.clicked.connect(self.generate_sales_report)
        main_layout.addWidget(sales_header)
        
        sales_grid = QGridLayout()
        sales_grid.setHorizontalSpacing(20)
        
        # Configure column stretching
        sales_grid.setColumnStretch(0, 1)
        sales_grid.setColumnStretch(1, 1)
        sales_grid.setColumnStretch(2, 1)
        
        # Sales summary card
        self.sales_summary = DetailCard("💰 Sales Summary")
        sales_summary_layout = QVBoxLayout()
        sales_summary_layout.setSpacing(12)  # Increased spacing
        
        self.total_sales_label = QLabel("Total Sales: $0")
        self.total_sales_label.setStyleSheet("color: #333333; background-color: transparent; font-weight: bold;")
        self.total_sales_label.setFont(QFont(ThemeManager.FONTS["family"], 14))
        
        self.avg_order_label = QLabel("Avg Order: $0")
        self.avg_order_label.setStyleSheet("color: #333333; background-color: transparent;")
        self.avg_order_label.setFont(QFont(ThemeManager.FONTS["family"], 13))
        
        self.orders_label = QLabel("Orders: 0")
        self.orders_label.setStyleSheet("color: #333333; background-color: transparent;")
        self.orders_label.setFont(QFont(ThemeManager.FONTS["family"], 13))
        
        sales_summary_layout.addWidget(self.total_sales_label)
        sales_summary_layout.addWidget(self.avg_order_label)
        sales_summary_layout.addWidget(self.orders_label)
        sales_summary_layout.addStretch()
        
        self.sales_summary.layout.addLayout(sales_summary_layout)
        
        # Growth card
        growth = DetailCard("Growth")
        growth_layout = QVBoxLayout()
        growth_layout.setSpacing(12)
        
        growth_value = QLabel("↗ +12%")
        growth_value.setStyleSheet(f"color: {ThemeManager.get_color('success')}; font-weight: bold; background-color: transparent;")
        growth_value.setFont(QFont(ThemeManager.FONTS["family"], 20, QFont.Bold))
        
        growth_weekly = QLabel("Weekly & Monthly Growth: ↗")
        growth_weekly.setStyleSheet("color: #333333; background-color: transparent;")
        growth_weekly.setFont(QFont(ThemeManager.FONTS["family"], 13))
        
        growth_peak = QLabel("Peak Sales Hours: 5 to 3 pm")
        growth_peak.setStyleSheet("color: #333333; background-color: transparent;")
        growth_peak.setFont(QFont(ThemeManager.FONTS["family"], 13))
        
        growth_layout.addWidget(growth_value)
        growth_layout.addWidget(growth_weekly)
        growth_layout.addWidget(growth_peak)
        growth_layout.addStretch()
        
        growth.layout.addLayout(growth_layout)
        
        # Best-selling items card
        best_selling = DetailCard("🌟 Best-Selling Items")
        best_selling_layout = QVBoxLayout()
        best_selling_layout.setSpacing(12)
        
        top_seller = QLabel("Top Seller: 📱P-X")
        top_seller.setStyleSheet("color: #3366CC; font-weight: bold; background-color: transparent;")
        top_seller.setFont(QFont(ThemeManager.FONTS["family"], 14))
        
        sales_inc = QLabel("Sales inc: ↗ +8%")
        sales_inc.setStyleSheet("color: #33AA33; background-color: transparent;")
        sales_inc.setFont(QFont(ThemeManager.FONTS["family"], 13))
        
        category = QLabel("Category-Wise Sales")
        category.setStyleSheet("color: #333333; background-color: transparent;")
        category.setFont(QFont(ThemeManager.FONTS["family"], 13))
        
        best_selling_layout.addWidget(top_seller)
        best_selling_layout.addWidget(sales_inc)
        best_selling_layout.addWidget(category)
        best_selling_layout.addStretch()
        
        best_selling.layout.addLayout(best_selling_layout)
        
        sales_grid.addWidget(self.sales_summary, 0, 0)
        sales_grid.addWidget(growth, 0, 1)
        sales_grid.addWidget(best_selling, 0, 2)
        
        main_layout.addLayout(sales_grid)
        
        # Inventory Reports Section
        inventory_header = SectionHeader("INVENTORY REPORTS", "📦")
        inventory_header.print_btn.clicked.connect(self.generate_inventory_report)
        main_layout.addWidget(inventory_header)
        
        inventory_grid = QGridLayout()
        inventory_grid.setHorizontalSpacing(20)
        
        # Configure column stretching
        inventory_grid.setColumnStretch(0, 1)
        inventory_grid.setColumnStretch(1, 1)
        inventory_grid.setColumnStretch(2, 1)
        
        # Inventory overview card
        self.inventory_overview = DetailCard("📦 Inventory Overview")
        inventory_layout = QVBoxLayout()
        inventory_layout.setSpacing(12)
        
        self.stock_value_label = QLabel("Stock Value: $0")
        self.stock_value_label.setStyleSheet("color: #333333; background-color: transparent; font-weight: bold;")
        self.stock_value_label.setFont(QFont(ThemeManager.FONTS["family"], 14))
        
        self.total_items_label = QLabel("Total Items: 0")
        self.total_items_label.setStyleSheet("color: #333333; background-color: transparent;")
        self.total_items_label.setFont(QFont(ThemeManager.FONTS["family"], 13))
        
        total_cartons = QLabel("Total cartons: 18")
        total_cartons.setStyleSheet("color: #333333; background-color: transparent;")
        total_cartons.setFont(QFont(ThemeManager.FONTS["family"], 13))
        
        inventory_layout.addWidget(self.stock_value_label)
        inventory_layout.addWidget(self.total_items_label)
        inventory_layout.addWidget(total_cartons)
        inventory_layout.addStretch()
        
        self.inventory_overview.layout.addLayout(inventory_layout)
        
        # Low stock alerts card
        self.low_stock = DetailCard("🔴 Low Stock Alerts")
        low_stock_layout = QVBoxLayout()
        low_stock_layout.setSpacing(12)
        
        self.low_stock_label = QLabel("Low Stock: 0 items")
        self.low_stock_label.setStyleSheet("color: #FF3333; font-weight: bold; background-color: transparent;")
        self.low_stock_label.setFont(QFont(ThemeManager.FONTS["family"], 14))
        
        expiring = QLabel("Expiring: 🔔 3 items")
        expiring.setStyleSheet("color: #FF9900; background-color: transparent;")
        expiring.setFont(QFont(ThemeManager.FONTS["family"], 13))
        
        low_stock_layout.addWidget(self.low_stock_label)
        low_stock_layout.addWidget(expiring)
        low_stock_layout.addStretch()
        
        self.low_stock.layout.addLayout(low_stock_layout)
        
        # Stock movement card
        stock_movement = DetailCard("📊 Stock Movement")
        stock_layout = QVBoxLayout()
        stock_layout.setSpacing(12)
        
        incoming = QLabel("Incoming ↗ Soon")
        incoming.setStyleSheet("color: #3366CC; font-weight: bold; background-color: transparent;")
        incoming.setFont(QFont(ThemeManager.FONTS["family"], 14))
        
        turnover = QLabel("Stock Turnover +15%")
        turnover.setStyleSheet("color: #33AA33; background-color: transparent;")
        turnover.setFont(QFont(ThemeManager.FONTS["family"], 13))
        
        stock_layout.addWidget(incoming)
        stock_layout.addWidget(turnover)
        stock_layout.addStretch()
        
        stock_movement.layout.addLayout(stock_layout)
        
        inventory_grid.addWidget(self.inventory_overview, 0, 0)
        inventory_grid.addWidget(self.low_stock, 0, 1)
        inventory_grid.addWidget(stock_movement, 0, 2)
        
        main_layout.addLayout(inventory_grid)
        
        # Financial Reports Section
        financial_header = SectionHeader("FINANCIAL REPORTS", "💹")
        financial_header.print_btn.clicked.connect(self.generate_financial_report)
        main_layout.addWidget(financial_header)
        
        financial_grid = QGridLayout()
        financial_grid.setHorizontalSpacing(20)
        
        # Configure column stretching
        financial_grid.setColumnStretch(0, 1)
        financial_grid.setColumnStretch(1, 1)
        financial_grid.setColumnStretch(2, 1)
        
        # Expenses overview card
        self.expenses_overview = DetailCard("📉 Expenses Overview")
        expenses_layout = QVBoxLayout()
        expenses_layout.setSpacing(12)
        
        self.total_expenses_label = QLabel("Total Exp: $0")
        self.total_expenses_label.setStyleSheet("color: #FF3333; font-weight: bold; background-color: transparent;")
        self.total_expenses_label.setFont(QFont(ThemeManager.FONTS["family"], 14))
        
        operational = QLabel("Operational: $10K")
        operational.setStyleSheet("color: #333333; background-color: transparent;")
        operational.setFont(QFont(ThemeManager.FONTS["family"], 13))
        
        marketing = QLabel("Marketing: $5K")
        marketing.setStyleSheet("color: #333333; background-color: transparent;")
        marketing.setFont(QFont(ThemeManager.FONTS["family"], 13))
        
        expenses_layout.addWidget(self.total_expenses_label)
        expenses_layout.addWidget(operational)
        expenses_layout.addWidget(marketing)
        expenses_layout.addStretch()
        
        self.expenses_overview.layout.addLayout(expenses_layout)
        
        # Profit/Loss card
        self.profit_loss = DetailCard("📊 Profit/Loss Report")
        profit_layout = QVBoxLayout()
        profit_layout.setSpacing(12)
        
        self.profit_margin_label = QLabel("Profit Margin: 0%")
        self.profit_margin_label.setStyleSheet("color: #33AA33; font-weight: bold; background-color: transparent;")
        self.profit_margin_label.setFont(QFont(ThemeManager.FONTS["family"], 14))
        
        profit_category = QLabel("Profit by Category")
        profit_category.setStyleSheet("color: #333333; background-color: transparent;")
        profit_category.setFont(QFont(ThemeManager.FONTS["family"], 13))
        
        profit_layout.addWidget(self.profit_margin_label)
        profit_layout.addWidget(profit_category)
        profit_layout.addStretch()
        
        self.profit_loss.layout.addLayout(profit_layout)
        
        # Sales vs Expenses card
        sales_vs_expenses = DetailCard("📊 Sales vs Expenses")
        sales_exp_layout = QVBoxLayout()
        sales_exp_layout.setSpacing(12)
        
        monthly = QLabel("Monthly Breakdown")
        monthly.setStyleSheet("color: #333333; font-weight: bold; background-color: transparent;")
        monthly.setFont(QFont(ThemeManager.FONTS["family"], 14))
        
        trend = QLabel("Trend Analysis")
        trend.setStyleSheet("color: #333333; background-color: transparent;")
        trend.setFont(QFont(ThemeManager.FONTS["family"], 13))
        
        breakeven = QLabel("Break-even Point...")
        breakeven.setStyleSheet("color: #333333; background-color: transparent;")
        breakeven.setFont(QFont(ThemeManager.FONTS["family"], 13))
        
        sales_exp_layout.addWidget(monthly)
        sales_exp_layout.addWidget(trend)
        sales_exp_layout.addWidget(breakeven)
        sales_exp_layout.addStretch()
        
        sales_vs_expenses.layout.addLayout(sales_exp_layout)
        
        financial_grid.addWidget(self.expenses_overview, 0, 0)
        financial_grid.addWidget(self.profit_loss, 0, 1)
        financial_grid.addWidget(sales_vs_expenses, 0, 2)
        
        main_layout.addLayout(financial_grid)
        
        # Customer Reports Section
        customer_header = SectionHeader("CUSTOMER REPORTS", "👥")
        customer_header.print_btn.clicked.connect(self.generate_customer_report)
        main_layout.addWidget(customer_header)
        
        customer_grid = QGridLayout()
        customer_grid.setHorizontalSpacing(20)
        
        # Configure column stretching
        customer_grid.setColumnStretch(0, 1)
        customer_grid.setColumnStretch(1, 1)
        
        # Customer insights card
        customer_insights = DetailCard("👥 Customer Insights")
        customer_layout = QVBoxLayout()
        customer_layout.setSpacing(12)
        
        top_customers = QLabel("Top Customers: 10")
        top_customers.setStyleSheet("color: #3366CC; font-weight: bold; background-color: transparent;")
        top_customers.setFont(QFont(ThemeManager.FONTS["family"], 14))
        
        loyalty = QLabel("Loyalty Score: 85%")
        loyalty.setStyleSheet("color: #33AA33; background-color: transparent;")
        loyalty.setFont(QFont(ThemeManager.FONTS["family"], 13))
        
        retention = QLabel("Retention: High")
        retention.setStyleSheet("color: #333333; background-color: transparent;")
        retention.setFont(QFont(ThemeManager.FONTS["family"], 13))
        
        customer_layout.addWidget(top_customers)
        customer_layout.addWidget(loyalty)
        customer_layout.addWidget(retention)
        customer_layout.addStretch()
        
        customer_insights.layout.addLayout(customer_layout)
        
        # Outstanding payments card
        outstanding_payments = DetailCard("💵 Outstanding Payments")
        payments_layout = QVBoxLayout()
        payments_layout.setSpacing(12)
        
        pending = QLabel("Pending: 💵 $5K")
        pending.setStyleSheet("color: #FF9900; font-weight: bold; background-color: transparent;")
        pending.setFont(QFont(ThemeManager.FONTS["family"], 14))
        
        due_soon = QLabel("Due Soon: ⏰ 3 invoices")
        due_soon.setStyleSheet("color: #FF3333; background-color: transparent;")
        due_soon.setFont(QFont(ThemeManager.FONTS["family"], 13))
        
        late = QLabel("Late Payments: Trend ↘")
        late.setStyleSheet("color: #333333; background-color: transparent;")
        late.setFont(QFont(ThemeManager.FONTS["family"], 13))
        
        payments_layout.addWidget(pending)
        payments_layout.addWidget(due_soon)
        payments_layout.addWidget(late)
        payments_layout.addStretch()
        
        outstanding_payments.layout.addLayout(payments_layout)
        
        customer_grid.addWidget(customer_insights, 0, 0)
        customer_grid.addWidget(outstanding_payments, 0, 1)
        
        main_layout.addLayout(customer_grid)
        
        scroll_area.setWidget(scroll_content)
        
        # Set the scroll area as this widget's main layout
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(scroll_area)
    
    def connect_signals(self):
        """Connect widget signals to handlers"""
        self.period_combo.currentIndexChanged.connect(self.load_data)
        self.refresh_btn.clicked.connect(self.refresh_data)
    
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
            
            # Get sales data
            sales_data = self.controller.get_sales_summary(period)
            self.sales_card.update_value(f"${sales_data.get('total_sales', 0):,.2f}")
            self.total_sales_label.setText(f"Total Sales: ${sales_data.get('total_sales', 0):,.2f}")
            self.avg_order_label.setText(f"Avg Order: ${sales_data.get('average_order', 0):,.2f}")
            self.orders_label.setText(f"Total Orders: {sales_data.get('total_orders', 0):,}")
            
            # Get inventory data
            inventory_data = self.controller.get_inventory_value()
            self.inventory_card.update_value(f"${inventory_data.get('total_value', 0):,.2f}")
            self.stock_value_label.setText(f"Stock Value: ${inventory_data.get('total_value', 0):,.2f}")
            self.total_items_label.setText(f"Total Items: {inventory_data.get('total_items', 0):,}")
            self.low_stock_label.setText(f"Low Stock Items: {inventory_data.get('low_stock_items', 0):,}")
            
            # Get profit data
            profit_data = self.controller.get_profit_summary(period)
            self.profit_card.update_value(f"${profit_data.get('net_profit', 0):,.2f}")
            self.expenses_card.update_value(f"${profit_data.get('total_expenses', 0):,.2f}")
            
            self.total_expenses_label.setText(f"Total Expenses: ${profit_data.get('total_expenses', 0):,.2f}")
            self.profit_margin_label.setText(f"Profit Margin: {profit_data.get('profit_margin', 0):.1f}%")
            
        except Exception as e:
            logger.error(f"Error loading report data: {str(e)}")
            QMessageBox.warning(self, "Data Error", f"Failed to load some report data: {str(e)}")
    
    def refresh_data(self):
        """Refresh data with visual feedback"""
        try:
            # Show a waiting cursor
            QApplication.setOverrideCursor(Qt.WaitCursor)
            
            # Load the data
            self.load_data()
            
            # Restore the cursor
            QApplication.restoreOverrideCursor()
            
            # Show success message
            self.show_refresh_success()
        except Exception as e:
            # Restore the cursor in case of error
            QApplication.restoreOverrideCursor()
            logger.error(f"Error refreshing data: {str(e)}")
            QMessageBox.warning(self, "Refresh Error", f"Failed to refresh data: {str(e)}")
    
    def show_refresh_success(self):
        """Show a brief success message for data refresh"""
        msg = QMessageBox()
        msg.setWindowTitle("Data Refreshed")
        msg.setText("Report data has been refreshed successfully.")
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setDefaultButton(QMessageBox.Ok)
        msg.exec_()
    
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
                QMessageBox.warning(self, "Report Error", "Failed to generate sales report. Please try again later.")
                
        except Exception as e:
            logger.error(f"Error generating sales report: {str(e)}")
            QMessageBox.critical(self, "Report Error", f"Error generating report: {str(e)}")
    
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
                QMessageBox.warning(self, "Report Error", "Failed to generate inventory report. No inventory items found or an error occurred.")
                
        except Exception as e:
            logger.error(f"Error generating inventory report: {str(e)}")
            QMessageBox.critical(self, "Report Error", f"Error generating report: {str(e)}")
    
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
