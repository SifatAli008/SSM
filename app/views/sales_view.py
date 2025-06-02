from datetime import datetime
import json
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame, 
    QPushButton, QLineEdit, QSizePolicy, QSpacerItem, QTableWidget, 
    QTableWidgetItem, QDialog, QFormLayout, QDateEdit, QDoubleSpinBox, 
    QComboBox, QMessageBox, QTabWidget, QHeaderView, QTextEdit, QDialogButtonBox,
    QListWidget, QListWidgetItem, QSpinBox, QGroupBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QFont, QColor, QIcon
from app.utils.theme_manager import ThemeManager
from app.views.widgets.components import Card, Button, TableComponent
from app.views.widgets.card_widget import CardWidget
from app.views.widgets.action_button import ActionButton
from app.core.sales import SalesManager

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
        self.controller = controller
        self.cart = []  # List of cart items
        self.products = [
            {"name": "iPhone 14 Pro", "price": 999.99, "stock": 15},
            {"name": "Samsung Galaxy S23", "price": 799.99, "stock": 3},
            {"name": "Nike Air Max 90", "price": 120.00, "stock": 25},
            {"name": "MacBook Pro 14\"", "price": 1999.99, "stock": 1},
        ]
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(24)

        # Left: Product Search & List
        left_panel = QVBoxLayout()
        left_panel.setSpacing(16)

        # Header
        header = QLabel("Point of Sale")
        header.setFont(QFont(ThemeManager.FONTS["family"], 28, QFont.Bold))
        left_panel.addWidget(header)
        subtitle = QLabel("Process customer transactions quickly and efficiently")
        subtitle.setStyleSheet("color: #888;")
        left_panel.addWidget(subtitle)

        # Product Search Card
        product_card = Card()
        product_card.layout.setSpacing(16)
        product_card.layout.setContentsMargins(16, 16, 16, 16)
        product_card.layout.addWidget(self._product_search_section())
        left_panel.addWidget(product_card)
        left_panel.addStretch()
        main_layout.addLayout(left_panel, 2)

        # Right: Cart & Order Summary
        right_panel = QVBoxLayout()
        right_panel.setSpacing(16)
        right_panel.addWidget(self._cart_section())
        right_panel.addWidget(self._order_summary_section())
        right_panel.addStretch()
        main_layout.addLayout(right_panel, 1)

    def _product_search_section(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        # Title
        title = QLabel("Product Search")
        title.setFont(QFont(ThemeManager.FONTS["family"], 18, QFont.Bold))
        layout.addWidget(title)
        
        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by product name or scan barcode...")
        self.search_input.textChanged.connect(self.refresh_products)
        layout.addWidget(self.search_input)

        # Product list
        self.product_list = QVBoxLayout()
        self._populate_product_list()
        layout.addLayout(self.product_list)
        return widget

    def _populate_product_list(self):
        # Clear previous
        while self.product_list.count():
            item = self.product_list.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        # Filter products
        search = self.search_input.text().lower() if hasattr(self, 'search_input') else ""
        for product in self.products:
            if search and search not in product["name"].lower():
                continue
            card = QFrame()
            card.setFrameShape(QFrame.StyledPanel)
            card.setStyleSheet("border: 1px solid #eee; border-radius: 8px;")
            card_layout = QHBoxLayout(card)
            card_layout.setContentsMargins(12, 8, 12, 8)
            # Name & stock
            name = QLabel(f"{product['name']}")
            name.setFont(QFont(ThemeManager.FONTS["family"], 14, QFont.Bold))
            card_layout.addWidget(name, 2)
            stock = QLabel(f"Stock: {product['stock']}")
            stock.setStyleSheet("color: #888;")
            card_layout.addWidget(stock, 1)
            # Price
            price = QLabel(f"${product['price']:.2f}")
            price.setFont(QFont(ThemeManager.FONTS["family"], 13, QFont.Bold))
            card_layout.addWidget(price, 1)
            # Add button
            add_btn = Button("+ Add", variant="primary")
            add_btn.clicked.connect(lambda _, p=product: self.add_to_cart(p))
            card_layout.addWidget(add_btn, 1)
            layout_item = QVBoxLayout()
            layout_item.addWidget(card)
            self.product_list.addWidget(card)

    def refresh_products(self):
        self._populate_product_list()

    def _cart_section(self):
        card = Card("Shopping Cart")
        card.layout.setSpacing(8)
        card.layout.setContentsMargins(16, 16, 16, 16)
        self.cart_list = QVBoxLayout()
        self.refresh_cart()
        card.layout.addLayout(self.cart_list)
        return card

    def refresh_cart(self):
        # Clear previous
        while self.cart_list.count():
            item = self.cart_list.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        # Add cart items
        for item in self.cart:
            row = QFrame()
            row.setFrameShape(QFrame.StyledPanel)
            row.setStyleSheet("border: 1px solid #eee; border-radius: 6px;")
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(8, 4, 8, 4)
            # Name
            name = QLabel(item['name'])
            name.setMinimumWidth(120)
            row_layout.addWidget(name, 2)
            # Price each
            price = QLabel(f"${item['price']:.2f} each")
            price.setStyleSheet("color: #888;")
            row_layout.addWidget(price, 1)
            # Quantity controls
            minus_btn = Button("-", variant="secondary")
            minus_btn.clicked.connect(lambda _, i=item: self.change_quantity(i, -1))
            row_layout.addWidget(minus_btn)
            qty = QLabel(str(item['qty']))
            qty.setMinimumWidth(24)
            qty.setAlignment(Qt.AlignCenter)
            row_layout.addWidget(qty)
            plus_btn = Button("+", variant="secondary")
            plus_btn.clicked.connect(lambda _, i=item: self.change_quantity(i, 1))
            row_layout.addWidget(plus_btn)
            # Total price
            total = QLabel(f"${item['price']*item['qty']:.2f}")
            total.setFont(QFont(ThemeManager.FONTS["family"], 12, QFont.Bold))
            row_layout.addWidget(total, 1)
            # Remove
            remove_btn = Button("🗑", variant="danger")
            remove_btn.clicked.connect(lambda _, i=item: self.remove_from_cart(i))
            row_layout.addWidget(remove_btn)
            self.cart_list.addWidget(row)

    def add_to_cart(self, product):
        for item in self.cart:
            if item['name'] == product['name']:
                if item['qty'] < product['stock']:
                    item['qty'] += 1
                self.refresh_cart()
                return
        self.cart.append({"name": product['name'], "price": product['price'], "qty": 1, "stock": product['stock']})
        self.refresh_cart()

    def change_quantity(self, item, delta):
        for cart_item in self.cart:
            if cart_item['name'] == item['name']:
                new_qty = cart_item['qty'] + delta
                if 1 <= new_qty <= cart_item['stock']:
                    cart_item['qty'] = new_qty
                elif new_qty < 1:
                    self.cart.remove(cart_item)
                self.refresh_cart()
                return

    def remove_from_cart(self, item):
        self.cart = [i for i in self.cart if i['name'] != item['name']]
        self.refresh_cart()

    def _order_summary_section(self):
        card = Card("Order Summary")
        card.layout.setSpacing(12)
        card.layout.setContentsMargins(16, 16, 16, 16)
        # Subtotal, tax, total
        self.subtotal_label = QLabel()
        self.tax_label = QLabel()
        self.total_label = QLabel()
        self.update_summary()
        card.layout.addWidget(self.subtotal_label)
        card.layout.addWidget(self.tax_label)
        card.layout.addWidget(self.total_label)
        # Discount
        discount_row = QHBoxLayout()
        discount_label = QLabel("Discount:")
        discount_label.setFont(QFont(ThemeManager.FONTS["family"], 12))
        self.discount_input = QDoubleSpinBox()
        self.discount_input.setMaximum(1e6)
        self.discount_input.setMinimum(0)
        self.discount_input.setValue(0)
        self.discount_input.setPrefix("$")
        self.discount_input.setMinimumHeight(32)
        self.discount_input.valueChanged.connect(self.update_summary)
        self.discount_input.valueChanged.connect(self._update_complete_btn_state)
        discount_row.addWidget(discount_label)
        discount_row.addWidget(self.discount_input)
        card.layout.addLayout(discount_row)
        # Payment method
        pm_label = QLabel("Payment Method")
        pm_label.setFont(QFont(ThemeManager.FONTS["family"], 12, QFont.Bold))
        card.layout.addWidget(pm_label)
        pm_row = QHBoxLayout()
        self.cash_btn = Button("\U0001F4B0 Cash", variant="primary")
        self.cash_btn.setCheckable(True)
        self.cash_btn.setChecked(True)
        self.cash_btn.clicked.connect(self._update_complete_btn_state)
        pm_row.addWidget(self.cash_btn)
        card.layout.addLayout(pm_row)
        # Amount paid
        self.amount_paid_input = QLineEdit()
        self.amount_paid_input.setPlaceholderText("Enter amount paid")
        self.amount_paid_input.textChanged.connect(self._update_complete_btn_state)
        card.layout.addWidget(self.amount_paid_input)
        # Complete sale
        self.complete_btn = Button("\U0001F4C4 Complete Sale", variant="primary")
        self.complete_btn.setEnabled(False)
        self.complete_btn.clicked.connect(self._on_complete_sale)
        card.layout.addWidget(self.complete_btn)
        # Print receipt
        self.print_btn = Button("\U0001F5B6 Print Receipt", variant="secondary")
        card.layout.addWidget(self.print_btn)
        return card

    def _update_complete_btn_state(self):
        try:
            total = self._get_total()
            paid = float(self.amount_paid_input.text()) if self.amount_paid_input.text() else 0
            enabled = self.cash_btn.isChecked() and total > 0 and paid >= total
            self.complete_btn.setEnabled(enabled)
        except Exception:
            self.complete_btn.setEnabled(False)

    def _get_total(self):
        subtotal = sum(item['price'] * item['qty'] for item in self.cart)
        tax = subtotal * 0.10
        discount = self.discount_input.value() if hasattr(self, 'discount_input') else 0
        return max(subtotal + tax - discount, 0)

    def _on_complete_sale(self):
        # Here you would trigger the sale completion logic
        QMessageBox.information(self, "Sale Completed", "The sale has been completed successfully!")

    def update_summary(self):
        subtotal = sum(item['price'] * item['qty'] for item in self.cart)
        tax = subtotal * 0.10
        discount = self.discount_input.value() if hasattr(self, 'discount_input') else 0
        total = max(subtotal + tax - discount, 0)
        self.subtotal_label.setText(f"Subtotal: <b>${subtotal:.2f}</b>")
        self.tax_label.setText(f"Tax (10%): <b>${tax:.2f}</b>")
        self.total_label.setText(f"Total: <span style='font-size:18px; color:#222;'><b>${total:.2f}</b></span>")

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

    def refresh_data(self):
        """Refresh all sales data to ensure real-time updates"""
        print("🔄 Refreshing sales data...")
        
        # Refresh the table data
        if hasattr(self, 'sales_table') and self.sales_table:
            self.load_sales_data()
            
        # Refresh any summary cards or statistics
        if hasattr(self, 'update_summary_cards'):
            self.update_summary_cards()
            
        return True

# NOTE: The code you provided was cut off at 'refresh_items_table'.
# Please provide the rest of the code for a full replacement if needed.
