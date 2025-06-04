from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTableWidget, QTableWidgetItem, QPushButton, QDialog, 
    QFormLayout, QMessageBox, QHeaderView, QComboBox, QFrame, QTabWidget, QTextEdit, QDateEdit, QCheckBox,
    QRadioButton, QButtonGroup, QSpinBox, QSplitter, QGroupBox, QGridLayout, QDoubleSpinBox, QStyledItemDelegate, QSizePolicy, QVBoxLayout,
    QAbstractItemView
)
from PyQt5.QtCore import Qt, QDate, QTime, QTimer
from PyQt5.QtGui import QFont, QColor, QIcon
from app.views.widgets.info_card import InfoCard
from app.views.widgets.action_button import ActionButton
from app.utils.ui_helpers import show_error
from app.views.widgets.components import TableComponent, Button
from app.views.widgets.reusable_shop_info_card import ReusableShopInfoCard, ShopCardPresets

class CustomerDialog(QDialog):
    def __init__(self, parent=None, customer=None):
        super().__init__(parent)
        self.setWindowTitle("Add/Edit Customer")
        self.setMinimumWidth(380)
        self.setMinimumHeight(320)
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
        self.setMinimumWidth(520)
        self.setMinimumHeight(400)
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

class CustomerDetailsDialog(QDialog):
    def __init__(self, customer):
        super().__init__()
        self.setWindowTitle("Customer Details")
        self.setMinimumWidth(600)
        layout = QVBoxLayout(self)
        tabs = QTabWidget()
        # --- Information Tab ---
        info_tab = QWidget()
        info_layout = QVBoxLayout(info_tab)
        # Info fields
        info_box = QFrame()
        info_box.setStyleSheet("border:1.5px solid #e5e7eb; border-radius:8px;")
        form = QFormLayout(info_box)
        form.addRow("Name", QLabel(customer["name"]))
        form.addRow("Email", QLabel(customer["email"]))
        form.addRow("Phone", QLabel(customer["phone"]))
        form.addRow("Address", QLabel(customer["address"]))
        status = QLabel(customer["status"])
        status.setStyleSheet("background:#e0f7ef; color:#16a34a; border-radius:8px; padding:2px 10px;")
        form.addRow("Status", status)
        info_layout.addWidget(info_box)
        # Summary cards
        cards = QHBoxLayout()
        for label, value in [
            ("Total Orders", customer["orders"]),
            ("Total Spent", f"${customer['spent']:.2f}"),
            ("Avg Order", f"${customer['spent']/customer['orders']:.2f}")
        ]:
            card = StatCard(label, value, "👥", "#222")
            cards.addWidget(card)
        info_layout.addLayout(cards)
        tabs.addTab(info_tab, "Information")
        # --- Purchase History Tab ---
        history_tab = QWidget()
        history_layout = QVBoxLayout(history_tab)
        # Example orders
        orders = [
            {"id": "ORD-001", "date": "1/15/2024", "items": 2, "total": 299.99},
            {"id": "ORD-002", "date": "1/10/2024", "items": 1, "total": 149.99},
            {"id": "ORD-003", "date": "1/5/2024", "items": 3, "total": 799.99},
        ]
        for o in orders:
            order_box = QFrame()
            order_box.setStyleSheet("border:1.5px solid #e5e7eb; border-radius:8px; margin-bottom:8px;")
            order_layout = QHBoxLayout(order_box)
            order_layout.addWidget(QLabel(f"{o['id']}\n{o['date']} • {o['items']} items"))
            order_layout.addStretch()
            total = QLabel(f"${o['total']:.2f}")
            total.setStyleSheet("font-weight:bold; font-size:18px;")
            order_layout.addWidget(total)
            history_layout.addWidget(order_box)
        tabs.addTab(history_tab, "Purchase History")
        layout.addWidget(tabs)

class StatCard(QFrame):
    def __init__(self, title, value, icon, color="#222"):
        super().__init__()
        self.setStyleSheet("""
            QFrame { 
                background: #fff;
                border-radius: 16px;
                border: 1px solid #eee;
                box-shadow: 0 2px 8px rgba(0,0,0,0.04);
            }
        """)
        layout = QHBoxLayout(self)
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"font-size: 32px; color: {color};")
        layout.addWidget(icon_label)
        text_layout = QVBoxLayout()
        label = QLabel(title)
        label.setStyleSheet("color:#888; font-size:15px;")
        value_label = QLabel(str(value))
        value_label.setStyleSheet(f"font-size:32px; font-weight:bold; color:{color};")
        text_layout.addWidget(label)
        text_layout.addWidget(value_label)
        layout.addLayout(text_layout)

class Badge(QLabel):
    def __init__(self, text, color):
        super().__init__(text)
        self.setStyleSheet(f"background:{color}; color:#fff; border-radius:8px; padding:2px 12px; font-weight:bold;")

class CustomerManagementView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:#f8fafc;")
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QLabel("Customer Management")
        header.setFont(QFont("Segoe UI", 24, QFont.Bold))
        subheader = QLabel("Manage your customer relationships and purchase history")
        subheader.setStyleSheet("color:#888; font-size:15px;")
        main_layout.addWidget(header)
        main_layout.addWidget(subheader)

        # --- Summary Cards Row (restored) ---
        self.card_labels = {}
        self.card_definitions = [
            {
                "title": "Total Customers",
                "default_value": "0",
                "description": "Updated just now",
                "color": "#2563eb",
                "key": "total",
                "icon": "👥"
            },
            {
                "title": "Active Customers",
                "default_value": "0",
                "description": "Currently active",
                "color": "#16a34a",
                "key": "active",
                "icon": "🟢"
            },
            {
                "title": "Total Revenue",
                "default_value": "$0",
                "description": "All-time revenue",
                "color": "#f59e42",
                "key": "revenue",
                "icon": "💰"
            },
            {
                "title": "Avg Order Value",
                "default_value": "$0",
                "description": "Average per order",
                "color": "#222",
                "key": "avg_order",
                "icon": "📦"
            }
        ]
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)
        for card in self.card_definitions:
            widget = ReusableShopInfoCard({
                "title": card["title"],
                "color": card["color"],
                "icon": card["icon"]
            })
            widget.value_label.setFont(QFont("Segoe UI", 36, QFont.Bold))
            widget.subtitle_label.setFont(QFont("Segoe UI", 13))
            widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            widget.value_label.setStyleSheet(f"color: {card['color']};")
            self.card_labels[card["key"]] = {
                "widget": widget,
                "value": widget.value_label,
                "desc": widget.subtitle_label
            }
            cards_layout.addWidget(widget)
        main_layout.addLayout(cards_layout)
        self.setup_auto_refresh()

        # --- Card container for search and table (Inventory style) ---
        table_card = QFrame()
        table_card.setObjectName("cardFrame")
        table_card.setStyleSheet('''
            QFrame#cardFrame {
                background: #fff;
                border-radius: 12px;
                border: 1.5px solid #e0e0e0;
                padding: 0;
            }
        ''')
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)

        # --- Search bar styled as customer sales page ---
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Search by name, email, or phone...')
        self.search_input.setMinimumHeight(36)
        self.search_input.setStyleSheet('''
            QLineEdit {
                background: #fff;
                border: 1.5px solid #e0e0e0;
                border-radius: 8px;
                font-size: 15px;
                padding: 8px 12px;
            }
            QLineEdit:focus {
                border: 1.5px solid #2563eb;
                outline: none;
            }
        ''')
        self.search_input.textChanged.connect(lambda: self.refresh_table())
        table_layout.addWidget(self.search_input)

        # --- Customer Table (Inventory style) ---
        self.customer_table_view = QTableWidget()
        self.customer_table_view.setColumnCount(7)
        self.customer_table_view.setHorizontalHeaderLabels([
            "Customer", "Contact", "Total Orders", "Total Spent", "Last Purchase", "Status", "Actions"
        ])
        self.customer_table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.customer_table_view.setAlternatingRowColors(True)
        self.customer_table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.customer_table_view.setSelectionMode(QAbstractItemView.MultiSelection)
        self.customer_table_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.customer_table_view.setStyleSheet('''
            QTableWidget {
                background: #fff;
                border-radius: 8px;
                border: 1.5px solid #e0e0e0;
                font-size: 14px;
                selection-background-color: #e3f2fd;
                selection-color: #1976d2;
                gridline-color: #e0e0e0;
                alternate-background-color: #f9f9f9;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 12px 8px;
                border: none;
                border-bottom: 2px solid #e0e0e0;
                font-weight: bold;
                color: #2c3e50;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            QTableWidget::item:hover {
                background-color: #f5f5f5;
            }
        ''')
        table_layout.addWidget(self.customer_table_view)

        # --- Only one action button below the table ---
        button_container = QFrame()
        button_container.setStyleSheet('''
            QFrame {
                background-color: #f8f9fa;
                border-top: 1px solid #e0e0e0;
                border-radius: 0 0 12px 12px;
            }
        ''')
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(15, 15, 15, 15)
        button_layout.setSpacing(10)
        self.view_history_button = Button("View Purchase History", variant="primary")
        button_layout.addStretch()
        button_layout.addWidget(self.view_history_button)
        button_layout.addStretch()
        table_layout.addWidget(button_container)
        main_layout.addWidget(table_card)

        # Remove all table action buttons (icons in the Actions column)
        # Remove all other action buttons (Add, Edit, Delete, Export, Refresh, Show All)
        # Only keep the 'View Purchase History' button below the table

    def show_customer_details(self, customer):
        dialog = CustomerDetailsDialog(customer)
        dialog.exec_()
        
    def refresh_table(self):
        self.customer_table_view.setRowCount(0)
        if not self.controller:
            return
        search = self.search_input.text()
        customers = self.controller.get_customers(search)
        self.customer_table_view.setRowCount(len(customers))
        for row, customer in enumerate(customers):
            # customer: (id, name, contact, address, history, created_at)
            name_item = QTableWidgetItem(str(customer[1]))
            name_item.setToolTip(str(customer[1]))
            name_item.setFont(QFont('Segoe UI', 15))
            name_item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
            self.customer_table_view.setItem(row, 0, name_item)
            contact_item = QTableWidgetItem(str(customer[2]))
            contact_item.setToolTip(str(customer[2]))
            contact_item.setFont(QFont("Consolas", 15))
            contact_item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
            self.customer_table_view.setItem(row, 1, contact_item)
            orders_item = QTableWidgetItem("-")
            orders_item.setToolTip("-")
            orders_item.setTextAlignment(Qt.AlignCenter)
            self.customer_table_view.setItem(row, 2, orders_item)
            spent_item = QTableWidgetItem("-")
            spent_item.setToolTip("-")
            spent_item.setTextAlignment(Qt.AlignCenter)
            self.customer_table_view.setItem(row, 3, spent_item)
            last_item = QTableWidgetItem("-")
            last_item.setToolTip("-")
            last_item.setTextAlignment(Qt.AlignCenter)
            self.customer_table_view.setItem(row, 4, last_item)
            # Status badge (default to active)
            status_widget = QWidget()
            status_layout = QHBoxLayout(status_widget)
            status_layout.setContentsMargins(0,0,0,0)
            badge_icon = "🟢"
            badge_color = "#16a34a"
            badge_bg = "#16a34a"
            badge = QLabel(f"<span style='font-size:18px;'>{badge_icon}</span> <b>Active</b>")
            badge.setStyleSheet(f"background:{badge_bg}; color:#fff; border-radius: 12px; padding: 4px 18px; font-weight:bold; font-size:15px;")
            status_layout.addWidget(badge)
            status_layout.addStretch()
            self.customer_table_view.setCellWidget(row, 5, status_widget)
            # Modern action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0,0,0,0)
            actions_layout.setSpacing(4)
            actions_widget.setMinimumHeight(32)
            actions_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            for icon, _, color in [
                ("👁", "View", "#2563eb"),
                ("✏️", "Edit", "#f39c12"),
                ("🗑", "Delete", "#e74c3c")
            ]:
                btn = QPushButton()
                btn.setFixedSize(24, 24)
                btn.setStyleSheet(f"background: {color}; border-radius: 12px; color: #fff; border: none; font-size:15px; padding:0;")
                btn.setText(icon)
                actions_layout.addWidget(btn)
            actions_layout.setAlignment(Qt.AlignCenter)
            self.customer_table_view.setCellWidget(row, 6, actions_widget)
        self.refresh_history_table()

    def on_table_clicked(self):
        self.selected_row = self.customer_table_view.currentRow()
        if self.selected_row >= 0:
            # Highlight the selected row with a distinctive color
            for row in range(self.customer_table_view.rowCount()):
                for col in range(self.customer_table_view.columnCount()):
                    item = self.customer_table_view.item(row, col)
                    if row == self.selected_row:
                        item.setBackground(QColor("#d4e6f1"))  # Light blue for selected row
                    else:
                        # Restore alternating colors
                        if row % 2 == 0:
                            item.setBackground(QColor("#f2f6fc"))
                        else:
                            item.setBackground(QColor("#ffffff"))
            
            # Fill invoice form with selected data
            self.invoice_name.setText(self.customer_table_view.item(self.selected_row, 1).text())
            self.invoice_total.setText(self.customer_table_view.item(self.selected_row, 4).text())
            
            # Set other fields to empty or default values
            current_date = QDate.currentDate().toString("yyyy-MM-dd")
            self.invoice_date.setText(current_date)
            self.invoice_address.setText("")
            self.invoice_order.setText("")
            self.invoice_contract.setText("")
            self.invoice_discount.setText("0.00")
            self.invoice_payment.setText("0.00")
            self.invoice_due.setText(self.customer_table_view.item(self.selected_row, 4).text())
            self.refresh_history_table()

    def add_customer(self):
        dialog = CustomerDialog(self)
        if dialog.exec_():
            data = dialog.get_data()
            self.controller.add_customer(
                name=data['name'],
                contact=data['contact'],
                address=data['address'],
                history=data.get('notes', ''),
                created_at=QDate.currentDate().toString("yyyy-MM-dd")
            )
            QMessageBox.information(self, "Customer Added", f"Customer {data['name']} added.")
            self.refresh_table()

    def edit_customer(self):
        if self.selected_row is None:
            show_error(self, "Select a customer to edit.", title="No Selection")
            return
        customer_id = int(self.customer_table_view.item(self.selected_row, 0).text())
        cust = {
            'name': self.customer_table_view.item(self.selected_row, 1).text(),
            'contact': self.customer_table_view.item(self.selected_row, 2).text(),
            'address': self.customer_table_view.item(self.selected_row, 3).text(),
            'notes': '',
            'type': 'Regular',
        }
        dialog = CustomerDialog(self, cust)
        if dialog.exec_():
            data = dialog.get_data()
            self.controller.update_customer(
                customer_id,
                name=data['name'],
                contact=data['contact'],
                address=data['address'],
                history=data.get('notes', '')
            )
            QMessageBox.information(self, "Customer Updated", f"Customer {data['name']} updated.")
            self.refresh_table()

    def delete_customer(self):
        if self.selected_row is None:
            show_error(self, "Select a customer to delete.", title="No Selection")
            return
        customer_id = int(self.customer_table_view.item(self.selected_row, 0).text())
        name = self.customer_table_view.item(self.selected_row, 1).text()
        if QMessageBox.question(self, "Delete Customer", f"Delete customer {name}?", 
                               QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
            self.controller.delete_customer(customer_id)
            QMessageBox.information(self, "Customer Deleted", f"Customer {name} deleted.")
            self.refresh_table()
    
    def add_billing(self):
        dialog = BillingDialog(self)
        if dialog.exec_():
            data = dialog.get_billing_data()
            # Save purchases to database
            if not self.purchases_controller or not self.controller:
                QMessageBox.warning(self, "Error", "Purchases controller or customer controller not set.")
                return
            customer = self.controller.get_customer_by_name(data['customer_name'])
            if not customer:
                QMessageBox.warning(self, "Error", f"Customer '{data['customer_name']}' not found.")
                return
            customer_id = customer[0]
            for product in data['products']:
                try:
                    quantity = int(product.get('quantity', '1'))
                except Exception:
                    quantity = 1
                try:
                    price = float(product.get('unit_price', '0'))
                except Exception:
                    price = 0.0
                try:
                    total = float(product.get('total_price', '0'))
                except Exception:
                    total = 0.0
                self.purchases_controller.add_purchase(
                    customer_id=customer_id,
                    product=product.get('product', ''),
                    quantity=quantity,
                    price=price,
                    total=total,
                    date=data['date']
                )
            QMessageBox.information(self, "Billing Added", f"Invoice {data['invoice_number']} added.")
            self.refresh_table()
    
    def edit_billing(self):
        if self.selected_row is None:
            show_error(self, "Select a billing record to edit.", title="No Selection")
            return
            
        # Create customer info dictionary from selected row
        customer = {
            'name': self.customer_table_view.item(self.selected_row, 1).text(),
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
            show_error(self, "Please fill in all required fields.", title="Incomplete Information")
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
        self.refresh_history_table()

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

    def set_purchases_controller(self, purchases_controller):
        self.purchases_controller = purchases_controller
        self.refresh_history_table()

    def refresh_history_table(self):
        self.history_table.setRowCount(0)
        if not self.purchases_controller:
            return
        # Filter by selected customer if any
        if self.selected_row is not None and self.customer_table_view.rowCount() > 0:
            customer_id = int(self.customer_table_view.item(self.selected_row, 0).text())
            purchases = self.purchases_controller.get_purchases_by_customer(customer_id)
        else:
            purchases = self.purchases_controller.get_all_purchases()
        self.history_table.setRowCount(len(purchases))
        for row, purchase in enumerate(purchases):
            # purchase: (id, customer_name, product, quantity, price, total, date)
            self.history_table.setItem(row, 0, QTableWidgetItem(str(purchase[0])))  # Order Number (id)
            self.history_table.setItem(row, 1, QTableWidgetItem(purchase[6]))       # Date
            self.history_table.setItem(row, 2, QTableWidgetItem(purchase[1]))       # Name
            self.history_table.setItem(row, 3, QTableWidgetItem(purchase[2]))       # Product (as Address placeholder)
            self.history_table.setItem(row, 4, QTableWidgetItem(str(purchase[3])))  # Contact (as Quantity placeholder) 

    def update_card_value(self, key, value=None, description=None):
        if key in self.card_labels:
            if value is not None:
                self.card_labels[key]["value"].setText(str(value))
            if description is not None:
                self.card_labels[key]["desc"].setText(description)

    def setup_auto_refresh(self):
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_card_data)
        self.refresh_timer.start(5000)  # every 5 seconds

    def refresh_card_data(self):
        # Replace with real data fetching logic
        from random import randint
        self.update_card_value("total", randint(100, 200), "Updated now")
        self.update_card_value("active", randint(2, 10))
        self.update_card_value("revenue", f"${randint(1000, 5000)}", "Live update")
        self.update_card_value("avg_order", f"${randint(50, 200)}", "Avg per order")

CustomerView = CustomerManagementView 