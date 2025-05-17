import sqlite3
from datetime import datetime
import json
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame, 
    QPushButton, QLineEdit, QSizePolicy, QSpacerItem, QTableWidget, 
    QTableWidgetItem, QDialog, QFormLayout, QDateEdit, QDoubleSpinBox, 
    QComboBox, QMessageBox, QTabWidget, QHeaderView, QTextEdit, QDialogButtonBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QFont, QColor, QIcon
from app.utils.theme_manager import ThemeManager
from app.views.widgets.components import Card, Button, TableComponent
from app.views.widgets.card_widget import CardWidget
from app.views.widgets.action_button import ActionButton

class SaleDialog(QDialog):
    def __init__(self, parent=None, sale=None):
        super().__init__(parent)
        self.setWindowTitle("Add/Edit Sale")
        self.setMinimumWidth(400)
        self.sale = sale
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        form = QFormLayout()
        form.setSpacing(10)
        
        self.customer = QLineEdit()
        self.customer.setMinimumHeight(36)
        
        self.date = QDateEdit(QDate.currentDate())
        self.date.setCalendarPopup(True)
        self.date.setMinimumHeight(36)
        
        self.total = QDoubleSpinBox()
        self.total.setMaximum(1e6)
        self.total.setMinimumHeight(36)
        
        self.payment = QDoubleSpinBox()
        self.payment.setMaximum(1e6)
        self.payment.setMinimumHeight(36)
        
        self.discount = QDoubleSpinBox()
        self.discount.setMaximum(1e6)
        self.discount.setMinimumHeight(36)
        
        self.status = QComboBox()
        self.status.addItems(["Completed", "Pending", "Cancelled"])
        self.status.setMinimumHeight(36)
        
        form.addRow("Customer:", self.customer)
        form.addRow("Date:", self.date)
        form.addRow("Total:", self.total)
        form.addRow("Payment:", self.payment)
        form.addRow("Discount:", self.discount)
        form.addRow("Status:", self.status)
        
        layout.addLayout(form)
        
        btns = QHBoxLayout()
        save = Button("Save", variant="primary")
        save.clicked.connect(self.accept)
        
        cancel = Button("Cancel")
        cancel.clicked.connect(self.reject)
        
        btns.addStretch()
        btns.addWidget(cancel)
        btns.addWidget(save)
        
        layout.addLayout(btns)
        
        if sale:
            self.customer.setText(sale['customer'])
            self.date.setDate(QDate.fromString(sale['date'], 'yyyy-MM-dd'))
            self.total.setValue(float(sale['total']))
            self.payment.setValue(float(sale['payment']))
            self.discount.setValue(float(sale['discount']))
            self.status.setCurrentText(sale['status'])
    
    def get_data(self):
        return {
            'customer': self.customer.text(),
            'date': self.date.date().toString('yyyy-MM-dd'),
            'total': self.total.value(),
            'payment': self.payment.value(),
            'discount': self.discount.value(),
            'status': self.status.currentText()
        }

class SalesView(QWidget):
    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller  # Pass your controller here
        self.selected_row = None
        self.init_ui()
        self.refresh_table()

    def init_ui(self):
        # Use the app's main theme instead of custom styling
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Page header
        header = QLabel("Sales Dashboard")
        header.setObjectName("page-title")
        header.setFont(QFont(ThemeManager.FONTS["family"], ThemeManager.FONTS["size_xxlarge"], QFont.Bold))
        main_layout.addWidget(header)
        
        # Quick actions bar
        actions_card = Card("Quick Actions")
        actions_layout = QHBoxLayout()
        
        self.add_sale_btn = Button('Add Sale', variant="primary")
        self.add_sale_btn.clicked.connect(self.add_sale)
        actions_layout.addWidget(self.add_sale_btn)
        
        self.edit_sale_btn = Button('Edit Sale')
        self.edit_sale_btn.clicked.connect(self.edit_sale)
        actions_layout.addWidget(self.edit_sale_btn)
        
        self.delete_sale_btn = Button('Delete Sale', variant="danger")
        self.delete_sale_btn.clicked.connect(self.delete_sale)
        actions_layout.addWidget(self.delete_sale_btn)
        
        self.view_sale_btn = Button('View Sale')
        self.view_sale_btn.clicked.connect(self.view_sale)
        actions_layout.addWidget(self.view_sale_btn)
        
        actions_layout.addStretch()
        actions_card.layout.addLayout(actions_layout)
        main_layout.addWidget(actions_card)

        # Dashboard cards section
        dashboard_layout = QGridLayout()
        dashboard_layout.setSpacing(16)
        
        # Row 1
        self.card_pending = Card("Pending Invoices")
        pending_layout = QVBoxLayout()
        pending_value = QLabel("3")
        pending_value.setFont(QFont(ThemeManager.FONTS["family"], 24, QFont.Bold))
        pending_value.setStyleSheet(f"color: {ThemeManager.get_color('primary')};")
        pending_subtitle = QLabel("Due Soon: 2")
        pending_subtitle.setStyleSheet(f"color: {ThemeManager.get_color('text_secondary')};")
        pending_layout.addWidget(pending_value)
        pending_layout.addWidget(pending_subtitle)
        self.card_pending.layout.addLayout(pending_layout)
        dashboard_layout.addWidget(self.card_pending, 0, 0)
        
        self.card_recent = Card("Recent Sales")
        recent_layout = QVBoxLayout()
        recent_value = QLabel("10 min ago")
        recent_value.setFont(QFont(ThemeManager.FONTS["family"], 18))
        recent_value.setStyleSheet(f"color: {ThemeManager.get_color('primary')};")
        recent_subtitle = QLabel("Total Sales: 150")
        recent_subtitle.setStyleSheet(f"color: {ThemeManager.get_color('text_secondary')};")
        recent_layout.addWidget(recent_value)
        recent_layout.addWidget(recent_subtitle)
        self.card_recent.layout.addLayout(recent_layout)
        dashboard_layout.addWidget(self.card_recent, 0, 1)
        
        self.card_top = Card("Top Customers")
        top_layout = QVBoxLayout()
        top_customer1 = QLabel("John Doe: $5,000")
        top_customer1.setStyleSheet(f"color: {ThemeManager.get_color('primary')};")
        top_customer2 = QLabel("Alice Smith: $4,200")
        top_customer2.setStyleSheet(f"color: {ThemeManager.get_color('text_secondary')};")
        top_layout.addWidget(top_customer1)
        top_layout.addWidget(top_customer2)
        self.card_top.layout.addLayout(top_layout)
        dashboard_layout.addWidget(self.card_top, 0, 2)
        
        # Row 2
        self.card_status = Card("Order Status")
        status_layout = QVBoxLayout()
        completed = QLabel("Completed: 45")
        completed.setStyleSheet(f"color: {ThemeManager.get_color('success')};")
        deliveries = QLabel("Deliveries Today: 8")
        canceled = QLabel("Canceled: 2")
        canceled.setStyleSheet(f"color: {ThemeManager.get_color('danger')};")
        status_layout.addWidget(completed)
        status_layout.addWidget(deliveries)
        status_layout.addWidget(canceled)
        self.card_status.layout.addLayout(status_layout)
        dashboard_layout.addWidget(self.card_status, 1, 0)
        
        main_layout.addLayout(dashboard_layout)

        # --- Sales Table Section ---
        table_card = Card("Sales Records")
        table_layout = QVBoxLayout()
        
        # Search bar
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by customer or invoice...")
        self.search_input.textChanged.connect(self.refresh_table)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        table_layout.addLayout(search_layout)
        
        # Table
        self.table = TableComponent()
        self.table.setup_columns(["Invoice", "Date", "Customer", "Total", "Payment", "Status"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.clicked.connect(self.on_table_clicked)
        table_layout.addWidget(self.table)
        
        table_card.layout.addLayout(table_layout)
        main_layout.addWidget(table_card)

    def refresh_table(self):
        # Dummy data for demonstration; replace with controller/model call
        sales = [
            {"invoice": "INV-001", "date": "2024-06-01", "customer": "John Doe", "total": 100.0, "payment": 100.0, "status": "Completed"},
            {"invoice": "INV-002", "date": "2024-06-02", "customer": "Alice Smith", "total": 200.0, "payment": 150.0, "status": "Pending"},
            {"invoice": "INV-003", "date": "2024-06-03", "customer": "Bob Johnson", "total": 150.0, "payment": 150.0, "status": "Completed"},
            {"invoice": "INV-004", "date": "2024-06-04", "customer": "Emily Wilson", "total": 300.0, "payment": 150.0, "status": "Pending"},
            {"invoice": "INV-005", "date": "2024-06-05", "customer": "Michael Brown", "total": 75.50, "payment": 75.50, "status": "Completed"},
        ]
        
        # Filter based on search text
        search = self.search_input.text().lower()
        filtered = [s for s in sales if search in s["customer"].lower() or search in s["invoice"].lower()]
        
        # Clear the table
        self.table.setRowCount(0)
        
        # Add rows to the table
        for sale in filtered:
            formatted_total = f"${sale['total']:.2f}"
            formatted_payment = f"${sale['payment']:.2f}"
            
            row_data = [
                sale["invoice"],
                sale["date"],
                sale["customer"],
                formatted_total,
                formatted_payment,
                sale["status"]
            ]
            
            self.table.add_row(row_data)
        
        self.selected_row = None

    def on_table_clicked(self):
        self.selected_row = self.table.currentRow()

    def add_sale(self):
        """Process a new sale with a detailed dialog"""
        dialog = SaleDialog(self)
        
        # Set default values for new sale
        dialog.date.setDate(QDate.currentDate())
        dialog.total.setValue(0)
        dialog.payment.setValue(0)
        dialog.discount.setValue(0)
        dialog.status.setCurrentText("Completed")
        
        if dialog.exec_():
            try:
                data = dialog.get_data()
                
                # Calculate any due amount
                due_amount = data['total'] - data['payment'] - data['discount']
                if due_amount > 0:
                    data['status'] = "Pending"
                
                # Show confirmation with complete details
                confirmation = QMessageBox()
                confirmation.setWindowTitle("Sale Confirmation")
                confirmation.setIcon(QMessageBox.Information)
                confirmation.setText(f"<b>Sale Processed Successfully</b>")
                
                details = (
                    f"<table style='margin-top:10px'>"
                    f"<tr><td>Customer:</td><td>{data['customer']}</td></tr>"
                    f"<tr><td>Date:</td><td>{data['date']}</td></tr>"
                    f"<tr><td>Total Amount:</td><td>${data['total']:.2f}</td></tr>"
                    f"<tr><td>Payment:</td><td>${data['payment']:.2f}</td></tr>"
                    f"<tr><td>Discount:</td><td>${data['discount']:.2f}</td></tr>"
                    f"<tr><td>Due Amount:</td><td>${due_amount:.2f}</td></tr>"
                    f"<tr><td>Status:</td><td>{data['status']}</td></tr>"
                    f"</table>"
                )
                confirmation.setInformativeText(details)
                
                # Print receipt button
                print_btn = confirmation.addButton("Print Receipt", QMessageBox.ActionRole)
                confirmation.addButton(QMessageBox.Ok)
                confirmation.setDefaultButton(QMessageBox.Ok)
                
                result = confirmation.exec_()
                
                # Handle print button click
                if confirmation.clickedButton() == print_btn:
                    self.print_receipt(data)
                
                # Refresh the table with the new data
                self.refresh_table()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to process sale: {str(e)}")
    
    def print_receipt(self, sale_data):
        """Print or preview a receipt"""
        QMessageBox.information(self, "Print Receipt", 
            "Receipt printing will be implemented in a future update.\n\n"
            f"Sale details for {sale_data['customer']} on {sale_data['date']} "
            f"with total ${sale_data['total']:.2f} would be printed."
        )

    def edit_sale(self):
        if self.selected_row is None:
            QMessageBox.warning(self, "No Selection", "Select a sale to edit.")
            return
        sale = {
            'customer': self.table.item(self.selected_row, 2).text(),
            'date': self.table.item(self.selected_row, 1).text(),
            'total': self.table.item(self.selected_row, 3).text().replace('$',''),
            'payment': self.table.item(self.selected_row, 4).text().replace('$',''),
            'discount': 0,
            'status': self.table.item(self.selected_row, 5).text()
        }
        dialog = SaleDialog(self, sale)
        if dialog.exec_():
            data = dialog.get_data()
            # TODO: Update in model/controller
            QMessageBox.information(self, "Sale Updated", f"Sale for {data['customer']} updated.")
            self.refresh_table()

    def delete_sale(self):
        if self.selected_row is None:
            QMessageBox.warning(self, "No Selection", "Select a sale to delete.")
            return
        customer = self.table.item(self.selected_row, 2).text()
        if QMessageBox.question(self, "Delete Sale", f"Delete sale for {customer}?", QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
            # TODO: Delete from model/controller
            QMessageBox.information(self, "Sale Deleted", f"Sale for {customer} deleted.")
            self.refresh_table()

    def view_sale(self):
        if self.selected_row is None:
            QMessageBox.warning(self, "No Selection", "Please select a sale to view.")
            return
            
        invoice = self.table.item(self.selected_row, 0).text()
        customer = self.table.item(self.selected_row, 2).text()
        
        # Create a detail dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Sale Details - {invoice}")
        dialog.setMinimumWidth(500)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Create details card
        details_form = QFormLayout()
        details_form.setVerticalSpacing(10)
        
        invoice_label = QLabel(f"<b>{invoice}</b>")
        invoice_label.setStyleSheet(f"font-size: 18px; color: {ThemeManager.get_color('primary')};")
        
        date = self.table.item(self.selected_row, 1).text()
        customer_label = QLabel(customer)
        customer_label.setStyleSheet(f"font-weight: bold; color: {ThemeManager.get_color('text_primary')};")
        
        date_label = QLabel(date)
        
        # Get financial details
        total = self.table.item(self.selected_row, 3).text()
        payment = self.table.item(self.selected_row, 4).text()
        status = self.table.item(self.selected_row, 5).text()
        
        # Set colors based on status
        status_label = QLabel(status)
        if status == "Completed":
            status_label.setStyleSheet(f"color: {ThemeManager.get_color('success')}; font-weight: bold;")
        elif status == "Pending":
            status_label.setStyleSheet(f"color: {ThemeManager.get_color('warning')}; font-weight: bold;")
        else:
            status_label.setStyleSheet(f"color: {ThemeManager.get_color('danger')}; font-weight: bold;")
        
        # Add all fields to form
        details_form.addRow(QLabel("<b>Invoice:</b>"), invoice_label)
        details_form.addRow(QLabel("<b>Customer:</b>"), customer_label)
        details_form.addRow(QLabel("<b>Date:</b>"), date_label)
        details_form.addRow(QLabel("<b>Total:</b>"), QLabel(total))
        details_form.addRow(QLabel("<b>Payment:</b>"), QLabel(payment))
        details_form.addRow(QLabel("<b>Status:</b>"), status_label)
        
        layout.addLayout(details_form)
        
        # Add notes section
        notes_label = QLabel("Notes:")
        notes_label.setStyleSheet(f"font-weight: bold; color: {ThemeManager.get_color('text_primary')};")
        layout.addWidget(notes_label)
        
        notes_edit = QTextEdit()
        notes_edit.setPlaceholderText("No notes for this sale.")
        notes_edit.setReadOnly(True)
        layout.addWidget(notes_edit)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(dialog.accept)
        layout.addWidget(button_box)
        
        dialog.exec_()

    def card_clicked(self, card_name):
        print(f'Card clicked: {card_name}')
        # TODO: Implement card click actions

# NOTE: The code you provided was cut off at 'refresh_items_table'.
# Please provide the rest of the code for a full replacement if needed.
