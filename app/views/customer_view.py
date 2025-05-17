from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTableWidget, QTableWidgetItem, QPushButton, QDialog, 
    QFormLayout, QMessageBox, QHeaderView, QComboBox, QFrame, QTabWidget, QTextEdit, QDateEdit, QCheckBox,
    QRadioButton, QButtonGroup, QSpinBox, QSplitter, QGroupBox, QGridLayout, QDoubleSpinBox
)
from PyQt5.QtCore import Qt, QDate, QTime
from PyQt5.QtGui import QFont, QColor, QIcon
from app.views.widgets.card_widget import CardWidget
from app.views.widgets.action_button import ActionButton

class CustomerDialog(QDialog):
    def __init__(self, parent=None, customer=None):
        super().__init__(parent)
        self.setWindowTitle("Add/Edit Customer")
        self.setMinimumWidth(500)
        self.setMinimumHeight(450)
        self.customer = customer
        
        main_layout = QVBoxLayout(self)
        
        # Tabs for better organization
        tab_widget = QTabWidget()
        basic_tab = QWidget()
        contact_tab = QWidget()
        preferences_tab = QWidget()
        
        # Basic Info Tab
        basic_layout = QFormLayout(basic_tab)
        self.name = QLineEdit()
        self.customer_type = QComboBox()
        self.customer_type.addItems(["Regular", "VIP", "Wholesale", "New"])
        
        basic_layout.addRow("Full Name:", self.name)
        basic_layout.addRow("Customer Type:", self.customer_type)
        
        # Contact Tab
        contact_layout = QFormLayout(contact_tab)
        self.phone = QLineEdit()
        self.email = QLineEdit()
        self.address = QLineEdit()
        self.city = QLineEdit()
        self.country = QComboBox()
        self.country.addItems(["USA", "Canada", "UK", "Australia", "Other"])
        
        contact_layout.addRow("Phone:", self.phone)
        contact_layout.addRow("Email:", self.email)
        contact_layout.addRow("Address:", self.address)
        contact_layout.addRow("City:", self.city)
        contact_layout.addRow("Country:", self.country)
        
        # Preferences Tab
        pref_layout = QFormLayout(preferences_tab)
        self.preferred_contact = QComboBox()
        self.preferred_contact.addItems(["Phone", "Email", "Mail"])
        self.notes = QTextEdit()
        self.marketing_opt_in = QCheckBox("Receive marketing emails")
        self.marketing_opt_in.setChecked(True)
        
        pref_layout.addRow("Contact Method:", self.preferred_contact)
        pref_layout.addRow("Marketing:", self.marketing_opt_in)
        pref_layout.addRow("Notes:", self.notes)
        
        # Add tabs to widget
        tab_widget.addTab(basic_tab, "Basic Info")
        tab_widget.addTab(contact_tab, "Contact")
        tab_widget.addTab(preferences_tab, "Preferences")
        
        main_layout.addWidget(tab_widget)
        
        # Buttons
        btns = QHBoxLayout()
        save = QPushButton("Save")
        save.setStyleSheet("""
            QPushButton {
                background-color: #27ae60; 
                color: white; 
                border-radius: 4px; 
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #219653; }
        """)
        save.clicked.connect(self.accept)
        
        cancel = QPushButton("Cancel")
        cancel.setStyleSheet("""
            QPushButton {
                background-color: #7f8c8d; 
                color: white; 
                border-radius: 4px; 
                padding: 8px 16px;
            }
            QPushButton:hover { background-color: #95a5a6; }
        """)
        cancel.clicked.connect(self.reject)
        
        btns.addStretch()
        btns.addWidget(cancel)
        btns.addWidget(save)
        main_layout.addLayout(btns)
        
        # Populate if editing
        if customer:
            self.name.setText(customer.get('name', ''))
            self.phone.setText(customer.get('contact', ''))
            self.address.setText(customer.get('address', ''))
            self.notes.setText(customer.get('notes', ''))
            self.email.setText(customer.get('email', ''))
            
            # Set combo boxes if values exist
            customer_type = customer.get('type', 'Regular')
            index = self.customer_type.findText(customer_type)
            if index >= 0:
                self.customer_type.setCurrentIndex(index)

    def get_data(self):
        """Get all customer data from dialog fields"""
        return {
            'name': self.name.text(),
            'contact': self.phone.text(),
            'email': self.email.text(),
            'address': self.address.text(),
            'city': self.city.text(),
            'country': self.country.currentText(),
            'notes': self.notes.toPlainText(),
            'type': self.customer_type.currentText(),
            'preferred_contact': self.preferred_contact.currentText(),
            'marketing_opt_in': self.marketing_opt_in.isChecked()
        }

class BillingDialog(QDialog):
    def __init__(self, parent=None, customer=None):
        super().__init__(parent)
        self.setWindowTitle("Customer Billing")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        self.customer = customer
        
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # Top section - Invoice header
        invoice_group = QGroupBox("Invoice Details")
        invoice_layout = QGridLayout(invoice_group)
        
        # Left column
        self.invoice_number_label = QLabel("Invoice Number:")
        self.invoice_number = QLineEdit()
        self.invoice_number.setPlaceholderText("Auto-generated")
        self.invoice_number.setReadOnly(True)
        
        self.date_label = QLabel("Date:")
        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        
        self.name_label = QLabel("Name:")
        self.name_input = QLineEdit()
        if self.customer:
            self.name_input.setText(self.customer.get('name', ''))
        
        self.contract_label = QLabel("Contract:")
        self.contract_input = QLineEdit()
        
        self.address_label = QLabel("Address:")
        self.address_input = QLineEdit()
        if self.customer:
            self.address_input.setText(self.customer.get('address', ''))
        
        # Right column
        self.order_number_label = QLabel("Order Number:")
        self.order_number = QLineEdit()
        
        self.total_price_label = QLabel("Total Price:")
        self.total_price_input = QLineEdit()
        self.total_price_input.setReadOnly(True)
        
        self.discount_label = QLabel("After Discount:")
        self.discount_input = QDoubleSpinBox()
        self.discount_input.setMaximum(999999.99)
        self.discount_input.setMinimum(0)
        self.discount_input.valueChanged.connect(self.calculate_due)
        
        self.payment_label = QLabel("Payment:")
        self.payment_input = QDoubleSpinBox()
        self.payment_input.setMaximum(999999.99)
        self.payment_input.setMinimum(0)
        self.payment_input.valueChanged.connect(self.calculate_due)
        
        self.due_label = QLabel("Due:")
        self.due_input = QLineEdit()
        self.due_input.setReadOnly(True)
        
        # Layout items
        # Left column
        invoice_layout.addWidget(self.invoice_number_label, 0, 0)
        invoice_layout.addWidget(self.invoice_number, 0, 1)
        invoice_layout.addWidget(self.date_label, 1, 0)
        invoice_layout.addWidget(self.date_input, 1, 1)
        invoice_layout.addWidget(self.name_label, 2, 0)
        invoice_layout.addWidget(self.name_input, 2, 1)
        invoice_layout.addWidget(self.contract_label, 3, 0)
        invoice_layout.addWidget(self.contract_input, 3, 1)
        invoice_layout.addWidget(self.address_label, 4, 0)
        invoice_layout.addWidget(self.address_input, 4, 1)
        
        # Right column
        invoice_layout.addWidget(self.order_number_label, 0, 2)
        invoice_layout.addWidget(self.order_number, 0, 3)
        invoice_layout.addWidget(self.total_price_label, 1, 2)
        invoice_layout.addWidget(self.total_price_input, 1, 3)
        invoice_layout.addWidget(self.discount_label, 2, 2)
        invoice_layout.addWidget(self.discount_input, 2, 3)
        invoice_layout.addWidget(self.payment_label, 3, 2)
        invoice_layout.addWidget(self.payment_input, 3, 3)
        invoice_layout.addWidget(self.due_label, 4, 2)
        invoice_layout.addWidget(self.due_input, 4, 3)
        
        main_layout.addWidget(invoice_group)
        
        # Product table
        product_group = QGroupBox("Product Details")
        product_layout = QVBoxLayout(product_group)
        
        self.product_table = QTableWidget(0, 6)
        self.product_table.setHorizontalHeaderLabels([
            "Serial", "Customer Name", "Product Name", "Product Quantity", 
            "Product Price", "Total Price"
        ])
        self.product_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Add table actions
        table_actions = QHBoxLayout()
        table_actions.addStretch()
        
        self.add_product_btn = QPushButton("Add")
        self.add_product_btn.setStyleSheet("""
            background-color: #3498db; 
            color: white; 
            border-radius: 4px; 
            padding: 8px 16px;
        """)
        self.add_product_btn.clicked.connect(self.add_product_row)
        
        self.update_product_btn = QPushButton("Update")
        self.update_product_btn.setStyleSheet("""
            background-color: #f39c12; 
            color: white; 
            border-radius: 4px; 
            padding: 8px 16px;
        """)
        
        self.delete_product_btn = QPushButton("Delete")
        self.delete_product_btn.setStyleSheet("""
            background-color: #e74c3c; 
            color: white; 
            border-radius: 4px; 
            padding: 8px 16px;
        """)
        self.delete_product_btn.clicked.connect(self.delete_product_row)
        
        table_actions.addWidget(self.add_product_btn)
        table_actions.addWidget(self.update_product_btn)
        table_actions.addWidget(self.delete_product_btn)
        
        product_layout.addWidget(self.product_table)
        product_layout.addLayout(table_actions)
        main_layout.addWidget(product_group)
        
        # Bottom buttons
        bottom_buttons = QHBoxLayout()
        bottom_buttons.addStretch()
        
        self.save_btn = QPushButton("Save")
        self.save_btn.setStyleSheet("""
            background-color: #2ecc71; 
            color: white; 
            border-radius: 4px; 
            padding: 8px 24px;
            font-weight: bold;
        """)
        self.save_btn.clicked.connect(self.accept)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("""
            background-color: #e74c3c; 
            color: white; 
            border-radius: 4px; 
            padding: 8px 24px;
            font-weight: bold;
        """)
        self.cancel_btn.clicked.connect(self.reject)
        
        bottom_buttons.addWidget(self.cancel_btn)
        bottom_buttons.addWidget(self.save_btn)
        
        main_layout.addLayout(bottom_buttons)
        
        # Initialize with a blank row
        self.add_product_row()
        
    def add_product_row(self):
        row = self.product_table.rowCount()
        self.product_table.insertRow(row)
        
        # Add serial number
        self.product_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
        
        # Add customer name from main form
        self.product_table.setItem(row, 1, QTableWidgetItem(self.name_input.text()))
        
        # Auto-update customer name in table when changed in main form
        self.name_input.textChanged.connect(lambda text: self.update_customer_name_in_table(text))
    
    def update_customer_name_in_table(self, text):
        for row in range(self.product_table.rowCount()):
            self.product_table.setItem(row, 1, QTableWidgetItem(text))
    
    def delete_product_row(self):
        selected_rows = self.product_table.selectedItems()
        if not selected_rows:
            return
            
        row = selected_rows[0].row()
        self.product_table.removeRow(row)
        
        # Update serial numbers
        for r in range(self.product_table.rowCount()):
            self.product_table.setItem(r, 0, QTableWidgetItem(str(r + 1)))
        
        self.calculate_total()
    
    def calculate_total(self):
        total = 0
        for row in range(self.product_table.rowCount()):
            total_price_item = self.product_table.item(row, 5)
            if total_price_item and total_price_item.text():
                try:
                    total += float(total_price_item.text())
                except ValueError:
                    pass
        
        self.total_price_input.setText(f"{total:.2f}")
        self.calculate_due()
    
    def calculate_due(self):
        try:
            total = float(self.total_price_input.text() or 0)
            discount = self.discount_input.value()
            payment = self.payment_input.value()
            
            due = total - discount - payment
            self.due_input.setText(f"{max(0, due):.2f}")
        except ValueError:
            self.due_input.setText("0.00")
    
    def get_billing_data(self):
        products = []
        for row in range(self.product_table.rowCount()):
            product = {}
            for col, field in enumerate(["serial", "customer", "product", "quantity", "unit_price", "total_price"]):
                item = self.product_table.item(row, col)
                product[field] = item.text() if item else ""
            products.append(product)
                
        return {
            "invoice_number": self.invoice_number.text(),
            "date": self.date_input.date().toString("yyyy-MM-dd"),
            "customer_name": self.name_input.text(),
            "contract": self.contract_input.text(),
            "address": self.address_input.text(),
            "order_number": self.order_number.text(),
            "total_price": self.total_price_input.text(),
            "discount": self.discount_input.value(),
            "payment": self.payment_input.value(),
            "due": self.due_input.text(),
            "products": products
        }

class CustomerView(QWidget):
    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.selected_row = None
        self.init_ui()
        self.refresh_table()

    def init_ui(self):
        self.setStyleSheet('''
            QWidget { 
                background-color: #f5f6fa; 
                color: #2c3e50; 
                font-family: 'Segoe UI', Arial, sans-serif; 
            }
            QFrame { 
                border-radius: 8px; 
                background-color: white; 
                border: 1px solid #e0e0e0; 
            }
            QPushButton.action { 
                background-color: #3498db; 
                color: white; 
                border-radius: 4px; 
                padding: 8px 16px; 
                font-size: 13px; 
                font-weight: bold; 
            }
            QPushButton.action:hover { 
                background-color: #2980b9; 
            }
            QLabel.title { 
                color: #2c3e50; 
                font-size: 18px; 
                font-weight: bold; 
                padding: 10px 0; 
            }
            QTableWidget { 
                border: none; 
                background-color: white; 
                gridline-color: #ecf0f1;
            }
            QTableWidget::item { 
                padding: 4px; 
                border-bottom: 1px solid #ecf0f1;
            }
            QTableWidget::item:selected { 
                background-color: #d5e8f8; 
                color: #2c3e50; 
            }
            QHeaderView::section { 
                background-color: #f8f9fa; 
                color: #2c3e50; 
                padding: 8px 4px; 
                border: none; 
                border-bottom: 1px solid #ddd; 
                font-weight: bold; 
            }
            QLineEdit { 
                padding: 8px; 
                border-radius: 4px; 
                border: 1px solid #dcdde1; 
                background-color: white; 
            }
            QLineEdit:focus { 
                border: 1px solid #3498db; 
            }
            QPushButton#perch { 
                background-color: #2ecc71; 
                color: white; 
                border-radius: 4px; 
                padding: 10px 24px; 
                font-weight: bold; 
            }
            QPushButton#cancel { 
                background-color: #e74c3c; 
                color: white; 
                border-radius: 4px; 
                padding: 10px 24px; 
                font-weight: bold; 
            }
            QPushButton#back {
                background-color: #3498db;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
        ''')
        
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Top section - Customer traffic and purchase history
        top_section = QHBoxLayout()
        top_section.setSpacing(15)
        
        # Customer Traffic Card - Simple version
        traffic_frame = QFrame()
        traffic_layout = QVBoxLayout(traffic_frame)
        
        traffic_title = QLabel("Customer Traffic")
        traffic_title.setFont(QFont('Segoe UI', 13))
        traffic_title.setStyleSheet("color: #34495e;")
        traffic_layout.addWidget(traffic_title)
        
        traffic_count = QLabel("320")
        traffic_count.setFont(QFont('Segoe UI', 32, QFont.Bold))
        traffic_count.setStyleSheet("color: #3498db;")
        traffic_layout.addWidget(traffic_count)
        
        traffic_peak = QLabel("Peak Hour: 5-6 PM")
        traffic_peak.setStyleSheet("color: #7f8c8d;")
        traffic_layout.addWidget(traffic_peak)
        
        top_section.addWidget(traffic_frame, 1)
        
        # Purchase History section
        history_frame = QFrame()
        history_layout = QVBoxLayout(history_frame)
        
        history_title = QLabel("Purchase History")
        history_title.setFont(QFont('Segoe UI', 16, QFont.Bold))
        history_layout.addWidget(history_title)
        
        self.history_table = QTableWidget(0, 5)
        self.history_table.setHorizontalHeaderLabels([
            "Order Number", "Time/Date", "Name", "Address", "Contact"
        ])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history_table.setAlternatingRowColors(True)
        self.history_table.verticalHeader().setVisible(True)  # Show row numbers
        
        history_layout.addWidget(self.history_table)
        
        top_section.addWidget(history_frame, 3)
        
        main_layout.addLayout(top_section)
        
        # Main customer management section
        management_frame = QFrame()
        management_layout = QVBoxLayout(management_frame)
        management_layout.setContentsMargins(15, 15, 15, 15)
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search Bar")
        self.search_input.textChanged.connect(self.refresh_table)
        self.search_input.setStyleSheet("margin-bottom: 15px;")
        search_layout.addWidget(self.search_input)
        
        management_layout.addLayout(search_layout)
        
        # Customer table
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "Serial", "Customer Name", "Product name", "Product Quantity", 
            "ProductPrice", "Total Price"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.clicked.connect(self.on_table_clicked)
        self.table.verticalHeader().setVisible(True)  # Show row numbers
        
        management_layout.addWidget(self.table)
        
        # Pagination
        pagination = QHBoxLayout()
        pagination.addStretch()
        pagination_label = QLabel("< 1 - 3 >")
        pagination_label.setStyleSheet("color: #7f8c8d;")
        pagination.addWidget(pagination_label)
        pagination.addStretch()
        management_layout.addLayout(pagination)
        
        # Table action buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Use cleaner, more modern button styling
        self.add_btn = QPushButton("Add")
        self.add_btn.setStyleSheet("""
            background-color: #3498db; 
            color: white; 
            border-radius: 4px; 
            padding: 8px 20px;
        """)
        self.add_btn.clicked.connect(self.add_billing)
        
        self.edit_btn = QPushButton("Update")
        self.edit_btn.setStyleSheet("""
            background-color: #f39c12; 
            color: white; 
            border-radius: 4px; 
            padding: 8px 20px;
        """)
        self.edit_btn.clicked.connect(self.edit_billing)
        
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setStyleSheet("""
            background-color: #e74c3c; 
            color: white; 
            border-radius: 4px; 
            padding: 8px 20px;
        """)
        self.delete_btn.clicked.connect(self.delete_customer)
        
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        
        management_layout.addLayout(button_layout)
        management_layout.addSpacing(20)
        
        # Invoice forms section - Improved layout
        invoice_title = QLabel("Invoices Number:")
        invoice_title.setFont(QFont('Segoe UI', 13))
        management_layout.addWidget(invoice_title)
        
        invoice_layout = QHBoxLayout()
        invoice_layout.setSpacing(20)
        
        # Left column - Invoice info - Match reference UI
        left_form = QVBoxLayout()
        left_form.setSpacing(10)
        
        self.invoice_date = QLineEdit()
        self.invoice_date.setPlaceholderText("Date")
        left_form.addWidget(self.invoice_date)
        
        self.invoice_name = QLineEdit()
        self.invoice_name.setPlaceholderText("Name")
        left_form.addWidget(self.invoice_name)
        
        self.invoice_address = QLineEdit()
        self.invoice_address.setPlaceholderText("Address")
        left_form.addWidget(self.invoice_address)
        
        invoice_layout.addLayout(left_form, 1)
        
        # Center column
        center_form = QVBoxLayout()
        center_form.setSpacing(10)
        
        self.invoice_order = QLineEdit()
        self.invoice_order.setPlaceholderText("Order Number")
        center_form.addWidget(self.invoice_order)
        
        self.invoice_contract = QLineEdit()
        self.invoice_contract.setPlaceholderText("Contract")
        center_form.addWidget(self.invoice_contract)
        
        # Add empty space to match reference UI's 3-field vertical alignment
        center_form.addStretch()
        
        invoice_layout.addLayout(center_form, 1)
        
        # Right column - Price info - Match reference UI
        right_form = QVBoxLayout()
        right_form.setSpacing(10)
        
        self.invoice_total = QLineEdit()
        self.invoice_total.setPlaceholderText("Total Price")
        right_form.addWidget(self.invoice_total)
        
        self.invoice_discount = QLineEdit()
        self.invoice_discount.setPlaceholderText("After Discount")
        self.invoice_discount.setText("0.00")
        right_form.addWidget(self.invoice_discount)
        
        self.invoice_payment = QLineEdit()
        self.invoice_payment.setPlaceholderText("Payment")
        self.invoice_payment.setText("0.00") 
        right_form.addWidget(self.invoice_payment)
        
        self.invoice_due = QLineEdit()
        self.invoice_due.setPlaceholderText("Due")
        right_form.addWidget(self.invoice_due)
        
        invoice_layout.addLayout(right_form, 1)
        
        management_layout.addLayout(invoice_layout)
        
        # Invoice action buttons - Align to right as in reference
        invoice_buttons = QHBoxLayout()
        invoice_buttons.addStretch()
        
        self.perch_btn = QPushButton("Perch")
        self.perch_btn.setObjectName("perch")
        self.perch_btn.clicked.connect(self.perch_invoice)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancel")
        self.cancel_btn.clicked.connect(self.clear_invoice_forms)
        
        invoice_buttons.addWidget(self.perch_btn)
        invoice_buttons.addWidget(self.cancel_btn)
        
        management_layout.addLayout(invoice_buttons)
        
        main_layout.addWidget(management_frame)
        
    def refresh_table(self):
        # Clear existing data
        self.table.setRowCount(0)
        
        # Dummy data for the main product table
        products = [
            {"serial": "1", "customer": "John Doe", "product": "Laptop", "quantity": "1", 
             "price": "1200.00", "total": "1200.00"},
            {"serial": "2", "customer": "Jane Smith", "product": "Phone", "quantity": "2", 
             "price": "800.00", "total": "1600.00"},
            {"serial": "3", "customer": "Bob Johnson", "product": "Keyboard", "quantity": "3", 
             "price": "50.00", "total": "150.00"},
        ]
        
        # Filter based on search
        search = self.search_input.text().lower()
        if search:
            filtered = [p for p in products if search in p["customer"].lower() or 
                                              search in p["product"].lower()]
        else:
            filtered = products
        
        # Update table
        self.table.setRowCount(len(filtered))
        for row, product in enumerate(filtered):
            # Apply alternating row colors
            if row % 2 == 0:
                row_color = QColor("#f2f6fc")  # Light blue for even rows
            else:
                row_color = QColor("#ffffff")  # White for odd rows
                
            self.table.setItem(row, 0, QTableWidgetItem(product["serial"]))
            self.table.setItem(row, 1, QTableWidgetItem(product["customer"]))
            self.table.setItem(row, 2, QTableWidgetItem(product["product"]))
            self.table.setItem(row, 3, QTableWidgetItem(product["quantity"]))
            self.table.setItem(row, 4, QTableWidgetItem(product["price"]))
            self.table.setItem(row, 5, QTableWidgetItem(product["total"]))
            
            # Apply the row color
            for col in range(6):
                item = self.table.item(row, col)
                if item:
                    item.setBackground(row_color)
        
        # Refresh history table
        self.refresh_history_table()
    
    def refresh_history_table(self):
        # Clear existing data
        self.history_table.setRowCount(0)
        
        # Dummy history data - match reference UI
        history = [
            {"order": "ORD-001", "date": "2024-06-01 10:15", "name": "John Doe", 
             "address": "123 Main St", "contact": "555-1234"},
            {"order": "ORD-002", "date": "2024-06-02 14:30", "name": "Jane Smith", 
             "address": "456 Oak Ave", "contact": "555-5678"},
        ]
        
        self.history_table.setRowCount(len(history))
        for row, order in enumerate(history):
            # Apply alternating row colors for better readability
            if row % 2 == 0:
                row_color = QColor("#ebf5fb")  # Light blue
            else:
                row_color = QColor("#ffffff")  # White
                
            self.history_table.setItem(row, 0, QTableWidgetItem(order["order"]))
            self.history_table.setItem(row, 1, QTableWidgetItem(order["date"]))
            self.history_table.setItem(row, 2, QTableWidgetItem(order["name"]))
            self.history_table.setItem(row, 3, QTableWidgetItem(order["address"]))
            self.history_table.setItem(row, 4, QTableWidgetItem(order["contact"]))
            
            # Apply the row color
            for col in range(5):
                item = self.history_table.item(row, col)
                if item:
                    item.setBackground(row_color)

    def on_table_clicked(self):
        self.selected_row = self.table.currentRow()
        if self.selected_row >= 0:
            # Highlight the selected row with a distinctive color
            for row in range(self.table.rowCount()):
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if row == self.selected_row:
                        item.setBackground(QColor("#d4e6f1"))  # Light blue for selected row
                    else:
                        # Restore alternating colors
                        if row % 2 == 0:
                            item.setBackground(QColor("#f2f6fc"))
                        else:
                            item.setBackground(QColor("#ffffff"))
            
            # Fill invoice form with selected data
            self.invoice_name.setText(self.table.item(self.selected_row, 1).text())
            self.invoice_total.setText(self.table.item(self.selected_row, 5).text())
            
            # Set other fields to empty or default values
            current_date = QDate.currentDate().toString("yyyy-MM-dd")
            self.invoice_date.setText(current_date)
            self.invoice_address.setText("")
            self.invoice_order.setText("")
            self.invoice_contract.setText("")
            self.invoice_discount.setText("0.00")
            self.invoice_payment.setText("0.00")
            self.invoice_due.setText(self.table.item(self.selected_row, 5).text())

    def add_customer(self):
        dialog = CustomerDialog(self)
        if dialog.exec_():
            data = dialog.get_data()
            # TODO: Save to model/controller
            QMessageBox.information(self, "Customer Added", f"Customer {data['name']} added.")
            self.refresh_table()

    def edit_customer(self):
        if self.selected_row is None:
            QMessageBox.warning(self, "No Selection", "Select a customer to edit.")
            return
            
        # Get data from table
        cust = {
            'name': self.table.item(self.selected_row, 1).text(),
            'type': 'Regular',  # Default
            'notes': ''  # Default
        }
        
        dialog = CustomerDialog(self, cust)
        if dialog.exec_():
            data = dialog.get_data()
            # TODO: Update in model/controller
            QMessageBox.information(self, "Customer Updated", f"Customer {data['name']} updated.")
            self.refresh_table()

    def delete_customer(self):
        if self.selected_row is None:
            QMessageBox.warning(self, "No Selection", "Select a customer to delete.")
            return
            
        name = self.table.item(self.selected_row, 1).text()
        if QMessageBox.question(self, "Delete Customer", f"Delete customer {name}?", 
                               QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
            # TODO: Delete from model/controller
            QMessageBox.information(self, "Customer Deleted", f"Customer {name} deleted.")
            self.refresh_table()
    
    def add_billing(self):
        dialog = BillingDialog(self)
        if dialog.exec_():
            data = dialog.get_billing_data()
            # TODO: Save to model/controller
            QMessageBox.information(self, "Billing Added", f"Invoice {data['invoice_number']} added.")
            self.refresh_table()
    
    def edit_billing(self):
        if self.selected_row is None:
            QMessageBox.warning(self, "No Selection", "Select a billing record to edit.")
            return
            
        # Create customer info dictionary from selected row
        customer = {
            'name': self.table.item(self.selected_row, 1).text(),
            'address': ''  # We don't have this in the table, would come from database
        }
        
        dialog = BillingDialog(self, customer)
        if dialog.exec_():
            data = dialog.get_billing_data()
            # TODO: Update in model/controller
            QMessageBox.information(self, "Billing Updated", f"Invoice {data['invoice_number']} updated.")
            self.refresh_table()
    
    def perch_invoice(self):
        # Check if fields are filled
        if not self.invoice_name.text() or not self.invoice_total.text():
            QMessageBox.warning(self, "Incomplete Information", "Please fill in all required fields.")
            return
            
        # Create invoice data
        invoice_data = {
            "date": self.invoice_date.text(),
            "name": self.invoice_name.text(),
            "address": self.invoice_address.text(),
            "order_number": self.invoice_order.text(),
            "contract": self.invoice_contract.text(),
            "total_price": self.invoice_total.text(),
            "discount": self.invoice_discount.text(),
            "payment": self.invoice_payment.text(),
            "due": self.invoice_due.text()
        }
        
        # TODO: Save to model/controller
        QMessageBox.information(self, "Invoice Saved", "Invoice has been saved successfully!")
        self.clear_invoice_forms()
        self.refresh_table()
    
    def clear_invoice_forms(self):
        self.invoice_date.clear()
        self.invoice_name.clear()
        self.invoice_address.clear()
        self.invoice_order.clear()
        self.invoice_contract.clear()
        self.invoice_total.clear()
        self.invoice_discount.clear()
        self.invoice_payment.clear()
        self.invoice_due.clear()
        self.selected_row = None

    def refresh_data(self):
        """Refresh all customer data to ensure real-time updates"""
        print("🔄 Refreshing customer data...")
        
        # Refresh the customer table
        if hasattr(self, 'customer_model') and self.customer_model:
            self.load_customers()
            
        # Refresh any summary cards or statistics
        if hasattr(self, 'update_summary_cards'):
            self.update_summary_cards()
            
        return True 