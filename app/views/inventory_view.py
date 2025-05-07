from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout,
    QGroupBox, QLineEdit, QSizePolicy, QDialog, QFormLayout, QMessageBox,
    QTableView, QHeaderView, QAbstractItemView, QComboBox, QFileDialog,
    QCheckBox, QSpacerItem, QFrame, QToolButton, QApplication, QStyledItemDelegate
)
from PyQt5.QtCore import Qt, QTimer, QDateTime, QSortFilterProxyModel, pyqtSlot, QSize
from PyQt5.QtGui import QFont, QIntValidator, QDoubleValidator, QIcon, QColor


class InventoryView(QWidget):
    def __init__(self, controller=None, user_role="Admin"):
        super().__init__()
        self.controller = controller
        self.user_role = user_role

        self.stock_count = 0
        self.low_stock_items = 0
        self.recent_items = 0
        self.card_labels = {}
        self.selected_row = -1
        self.selected_rows = []  # For multi-select functionality

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Smart Shop Manager - Inventory")
        self.setGeometry(100, 100, 1300, 900)
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI';
                font-size: 14px;
            }
            QGroupBox {
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                padding: 15px;
                background-color: #ffffff;
                margin-top: 10px;
            }
            QTableView {
                border: 1px solid #e0e0e0;
                alternate-background-color: #f9f9f9;
                gridline-color: #e0e0e0;
            }
            QTableView::item {
                padding: 5px;
            }
            QTableView::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 8px;
                border: 1px solid #e0e0e0;
                font-weight: bold;
            }
            QPushButton {
                border-radius: 6px;
                padding: 10px 16px;
                font-weight: bold;
                color: white;
            }
            QPushButton:hover {
                background-color: #333;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #888888;
            }
            QLineEdit, QComboBox {
                padding: 8px;
                border-radius: 6px;
                border: 1px solid #ccc;
            }
            QComboBox::drop-down {
                border: 0px;
            }
            QComboBox::down-arrow {
                width: 14px;
                height: 14px;
            }
            QFrame#cardFrame {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                padding: 15px;
            }
            QLabel#cardTitle {
                font-weight: bold;
                font-size: 16px;
                color: #2c3e50;
            }
            QLabel#cardValue {
                font-size: 22px;
                font-weight: bold;
                color: #3498db;
            }
            QLabel#cardDescription {
                font-size: 12px;
                color: #7f8c8d;
            }
        """)

        main_layout = QVBoxLayout()

        # Header
        main_layout.addLayout(self.build_header())

        # Cards Row - improved to match dashboard style
        self.create_info_cards(main_layout)
        
        # Table and Actions Area
        main_layout.addLayout(self.create_table_section())

        # Footer
        self.footer_label = QLabel()
        self.footer_label.setStyleSheet("background-color: #F7F7F7; padding: 6px; font-style: italic;")
        self.update_footer_time()
        main_layout.addWidget(self.footer_label)

        timer = QTimer(self)
        timer.timeout.connect(self.update_footer_time)
        timer.start(60000)  # Update every minute

        self.setLayout(main_layout)
        self.setup_model()
        self.refresh_from_controller()

    def build_header(self):
        header = QHBoxLayout()
        header.setSpacing(12)

        title_label = QLabel("Inventory Management")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50;")
        header.addWidget(title_label)
        
        header.addStretch()

        for text, color, icon in [("🔔 Notifications", "#3498db", "bell"), 
                                  ("👤 Admin", "#2ecc71", "user"), 
                                  ("🔴 Logout", "#e74c3c", "power")]:
            btn = QPushButton(text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                }}
                QPushButton:hover {{
                    background-color: #333;
                }}
            """)
            header.addWidget(btn)

        return header

    def create_info_cards(self, parent_layout):
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)
        
        # Create cards with improved styling
        card_data = [
            {"title": "📦 Total Stock", "value": "0", "description": "Updated just now", "color": "#3498db", "key": "stock"},
            {"title": "⚠️ Low Stock Items", "value": "0", "description": "Restock Suggested", "color": "#e74c3c", "key": "low"},
            {"title": "🆕 Recently Added", "value": "0", "description": "Last few minutes", "color": "#2ecc71", "key": "recent"},
            {"title": "💰 Inventory Value", "value": "$0", "description": "Total investment", "color": "#f39c12", "key": "value"}
        ]
        
        self.card_labels = {}
        
        for card in card_data:
            frame = QFrame()
            frame.setObjectName("cardFrame")
            layout = QVBoxLayout(frame)
            
            title = QLabel(card["title"])
            title.setObjectName("cardTitle")
            
            value = QLabel(card["value"])
            value.setObjectName("cardValue")
            value.setStyleSheet(f"color: {card['color']};")
            
            desc = QLabel(card["description"])
            desc.setObjectName("cardDescription")
            
            layout.addWidget(title)
            layout.addWidget(value)
            layout.addWidget(desc)
            
            cards_layout.addWidget(frame)
            self.card_labels[card["key"]] = {"widget": frame, "value": value, "desc": desc}
        
        parent_layout.addLayout(cards_layout)

    def create_table_section(self):
        table_section = QVBoxLayout()
        
        # Search and filter bar - enhanced
        search_frame = QFrame()
        search_frame.setObjectName("cardFrame")
        search_layout = QVBoxLayout(search_frame)
        
        search_title = QLabel("Search & Filter Products")
        search_title.setObjectName("cardTitle")
        search_layout.addWidget(search_title)
        
        search_controls = QHBoxLayout()
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍 Search by product name or details...")
        self.search_bar.textChanged.connect(self.filter_inventory)
        
        self.category_filter = QComboBox()
        self.category_filter.addItems(["All Categories", "Electronics", "Food", "Clothing", "Other"])
        self.category_filter.currentIndexChanged.connect(self.filter_inventory)
        
        self.price_range = QComboBox()
        self.price_range.addItems(["All Prices", "Under $10", "$10-$50", "$50-$100", "Over $100"])
        self.price_range.currentIndexChanged.connect(self.filter_inventory)
        
        search_controls.addWidget(QLabel("Search:"))
        search_controls.addWidget(self.search_bar, 3)
        search_controls.addWidget(QLabel("Category:"))
        search_controls.addWidget(self.category_filter, 1)
        search_controls.addWidget(QLabel("Price:"))
        search_controls.addWidget(self.price_range, 1)
        
        search_layout.addLayout(search_controls)
        table_section.addWidget(search_frame)
        
        # Inventory Table - now with multi-select
        table_frame = QFrame()
        table_frame.setObjectName("cardFrame")
        table_layout = QVBoxLayout(table_frame)
        
        table_header = QHBoxLayout()
        table_title = QLabel("Product Inventory")
        table_title.setObjectName("cardTitle")
        table_header.addWidget(table_title)
        
        self.item_count_label = QLabel("0 items")
        self.item_count_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        table_header.addWidget(self.item_count_label, 1)
        
        table_layout.addLayout(table_header)
        
        # Create the table
        self.table_view = QTableView()
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_view.setSelectionMode(QAbstractItemView.ExtendedSelection)  # Allow multi-select
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSortingEnabled(True)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_view.setShowGrid(True)
        self.table_view.clicked.connect(self.on_table_clicked)
        
        table_layout.addWidget(self.table_view)
        
        # Action Buttons
        buttons_layout = QHBoxLayout()
        
        self.add_button = QPushButton("➕ Add Product")
        self.add_button.setStyleSheet("background-color: #27ae60;")
        
        self.edit_button = QPushButton("✏️ Edit Product")
        self.edit_button.setStyleSheet("background-color: #3498db;")
        
        self.delete_button = QPushButton("🗑️ Delete Selected")
        self.delete_button.setStyleSheet("background-color: #e74c3c;")
        
        self.upload_button = QPushButton("📥 Bulk Upload")
        self.upload_button.setStyleSheet("background-color: #9b59b6;")
        
        self.export_button = QPushButton("📤 Export CSV")
        self.export_button.setStyleSheet("background-color: #f39c12;")
        
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.edit_button)
        buttons_layout.addWidget(self.delete_button)
        buttons_layout.addWidget(self.upload_button)
        buttons_layout.addWidget(self.export_button)
        
        # Connect buttons to actions
        self.add_button.clicked.connect(self.show_add_dialog)
        self.edit_button.clicked.connect(self.show_edit_dialog)
        self.delete_button.clicked.connect(self.delete_products)
        self.upload_button.clicked.connect(self.show_upload_dialog)
        self.export_button.clicked.connect(self.export_to_csv)
        
        # Initially disable edit/delete buttons until row is selected
        self.edit_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        
        table_layout.addLayout(buttons_layout)
        table_section.addWidget(table_frame)
        
        return table_section

    def update_footer_time(self):
        self.footer_label.setText(f"Last synced: {QDateTime.currentDateTime().toString('hh:mm ap - dd MMM yyyy')}")

    def update_stock_info(self, stock, low_stock, recent, total_value=0):
        self.card_labels["stock"]["value"].setText(f"{stock:,}")
        self.card_labels["low"]["value"].setText(f"{low_stock}")
        self.card_labels["recent"]["value"].setText(f"{recent}")
        self.card_labels["value"]["value"].setText(f"${total_value:,.2f}")
        
        # Update item count label
        row_count = self.table_view.model().rowCount() if self.table_view.model() else 0
        self.item_count_label.setText(f"{row_count} items in inventory")

    def setup_model(self):
        if self.controller and hasattr(self.controller, 'model'):
            # Clear any filters
            self.controller.model.setFilter("")
            # Create a proxy model for advanced filtering
            self.proxy_model = QSortFilterProxyModel()
            self.proxy_model.setSourceModel(self.controller.model)
            self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
            self.proxy_model.setFilterKeyColumn(-1)  # Filter on all columns
            
            self.table_view.setModel(self.proxy_model)
            
            # Hide only the ID column
            self.table_view.hideColumn(0)
            for col in range(1, 7):
                self.table_view.showColumn(col)
            # Set column headers for clarity
            headers = [
                "Product Name", "Product Details", "Category", "Quantity", "Buying Price ($)", "Selling Price ($)"
            ]
            for i, header in enumerate(headers, start=1):
                self.table_view.model().setHeaderData(i, Qt.Horizontal, header)
            # Set better column widths and minimum widths
            self.table_view.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # Product Name
            self.table_view.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)  # Product Details
            self.table_view.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Category
            self.table_view.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Quantity
            self.table_view.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Buying Price
            self.table_view.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Selling Price
            # Set minimum widths for readability
            self.table_view.setColumnWidth(1, 180)  # Product Name
            self.table_view.setColumnWidth(2, 220)  # Product Details
            self.table_view.setColumnWidth(3, 120)  # Category
            self.table_view.setColumnWidth(4, 100)  # Quantity
            self.table_view.setColumnWidth(5, 120)  # Buying Price
            self.table_view.setColumnWidth(6, 120)  # Selling Price
            self.table_view.horizontalHeader().setDefaultSectionSize(120)
            # Connect selection model signals after model is set up
            self.table_view.selectionModel().selectionChanged.connect(self.on_selection_changed)
            # Refresh model and proxy to ensure data is shown
            self.controller.model.select()
            self.proxy_model.invalidate()

    def refresh_from_controller(self):
        if self.controller:
            self.controller.refresh_data()
            stock = self.controller.count_total_stock()
            low = self.controller.count_low_stock()
            recent = self.controller.count_recent_items()
            total_value = self.controller.calculate_inventory_value()
            self.update_stock_info(stock, low, recent, total_value)

    def on_table_clicked(self, index):
        self.selected_row = self.proxy_model.mapToSource(index).row()
        self.edit_button.setEnabled(True)
        self.delete_button.setEnabled(True)

    def on_selection_changed(self, selected, deselected):
        self.selected_rows = []
        for index in self.table_view.selectionModel().selectedRows():
            source_row = self.proxy_model.mapToSource(index).row()
            self.selected_rows.append(source_row)
        
        # Enable or disable buttons based on selection
        has_selection = len(self.selected_rows) > 0
        self.delete_button.setEnabled(has_selection)
        
        # Edit button is only enabled when exactly one row is selected
        self.edit_button.setEnabled(len(self.selected_rows) == 1)
        if len(self.selected_rows) == 1:
            self.selected_row = self.selected_rows[0]

    def filter_inventory(self):
        search_text = self.search_bar.text().lower()
        category = self.category_filter.currentText()
        price_range = self.price_range.currentText()
        
        # Create a filter for the proxy model
        self.proxy_model.setFilterFixedString(search_text)
        
        # Apply additional filters through the controller
        filter_query = ""
        
        # Category filter
        if category != "All Categories":
            filter_query += f" AND category = '{category}'"
        
        # Price range filter
        if price_range == "Under $10":
            filter_query += " AND selling_price < 10"
        elif price_range == "$10-$50":
            filter_query += " AND selling_price >= 10 AND selling_price <= 50"
        elif price_range == "$50-$100":
            filter_query += " AND selling_price > 50 AND selling_price <= 100" 
        elif price_range == "Over $100":
            filter_query += " AND selling_price > 100"
        
        # Apply filter to the source model
        if filter_query:
            if search_text:
                # Combine text search with other filters
                self.controller.model.setFilter(f"LOWER(name) LIKE '%{search_text}%'{filter_query}")
            else:
                # Just apply the other filters
                self.controller.model.setFilter(filter_query.lstrip(" AND"))
        else:
            # Reset to just text search or no filter
            if search_text:
                self.controller.model.setFilter(f"LOWER(name) LIKE '%{search_text}%'")
            else:
                self.controller.model.setFilter("")
        
        self.controller.model.select()
        
        # Update the item count
        row_count = self.table_view.model().rowCount()
        self.item_count_label.setText(f"{row_count} items in inventory")

    def show_add_dialog(self):
        dialog = ProductDialog(self, "Add New Product")
        if dialog.exec_():
            name = dialog.name_input.text()
            details = dialog.details_input.toPlainText()
            category = dialog.category_input.currentText()
            stock = int(dialog.qty_input.text())
            buying_price = float(dialog.buying_price_input.text())
            selling_price = float(dialog.selling_price_input.text())
            
            if self.controller:
                # Add the product with all details
                self.controller.add_product(
                    name, 
                    stock, 
                    buying_price, 
                    selling_price, 
                    details=details, 
                    category=category
                )
                self.refresh_from_controller()
                QMessageBox.information(self, "Success", f"Product '{name}' added successfully!")

    def show_edit_dialog(self):
        if not self.selected_rows or len(self.selected_rows) != 1:
            QMessageBox.warning(self, "No Selection", "Please select a single product to edit.")
            return
            
        # Get current values from the model
        name = self.controller.model.data(self.controller.model.index(self.selected_row, 1))
        stock = self.controller.model.data(self.controller.model.index(self.selected_row, 4))
        buying_price = self.controller.model.data(self.controller.model.index(self.selected_row, 5))
        selling_price = self.controller.model.data(self.controller.model.index(self.selected_row, 6))
        
        # Get additional fields if they exist in your database
        details = self.controller.get_product_details(self.selected_row)
        category = self.controller.get_product_category(self.selected_row)
        
        dialog = ProductDialog(
            self, 
            "Edit Product", 
            name, 
            stock, 
            buying_price, 
            selling_price,
            details,
            category
        )
        
        if dialog.exec_():
            # Prepare updated data
            updated_data = {
                1: dialog.name_input.text(),
                4: int(dialog.qty_input.text()),
                5: float(dialog.buying_price_input.text()),
                6: float(dialog.selling_price_input.text())
            }
            
            # Add additional fields to the update
            additional_data = {
                "details": dialog.details_input.toPlainText(),
                "category": dialog.category_input.currentText()
            }
            
            # Update the product
            self.controller.update_item(self.selected_row, updated_data, additional_data)
            self.refresh_from_controller()
            QMessageBox.information(self, "Success", f"Product updated successfully!")

    def delete_products(self):
        if not self.selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select at least one product to delete.")
            return
        
        # Get product names for confirmation message
        product_names = []
        for row in self.selected_rows:
            name = self.controller.model.data(self.controller.model.index(row, 1))
            product_names.append(name)
        
        product_list = "\n".join(product_names[:5])
        if len(product_names) > 5:
            product_list += f"\n... and {len(product_names) - 5} more"
        
        # Ask for confirmation
        confirm = QMessageBox.question(
            self, 
            "Confirm Deletion", 
            f"Are you sure you want to delete the following products?\n\n{product_list}",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            deleted_count = self.controller.delete_multiple_items(self.selected_rows)
            self.selected_row = -1
            self.selected_rows = []
            self.edit_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            self.refresh_from_controller()
            QMessageBox.information(self, "Success", f"{deleted_count} products deleted successfully!")

    def show_upload_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select CSV File for Bulk Upload", 
            "", 
            "CSV Files (*.csv)"
        )
        
        if file_path:
            confirm = QMessageBox.question(
                self,
                "Confirm Upload",
                f"Are you sure you want to upload data from:\n{file_path}?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if confirm == QMessageBox.Yes:
                try:
                    success, added, errors = self.controller.upload_bulk_stock(file_path)
                    self.refresh_from_controller()
                    QMessageBox.information(self, "Success", f"Bulk upload completed successfully!\n{added} products added, {errors} errors encountered.")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Upload failed: {str(e)}")

    def export_to_csv(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Inventory to CSV",
            "inventory_export.csv",
            "CSV Files (*.csv)"
        )
        
        if file_path:
            try:
                success, count = self.controller.export_inventory_to_csv(file_path)
                if success:
                    QMessageBox.information(self, "Success", f"Exported {count} products to CSV successfully!")
                else:
                    QMessageBox.warning(self, "Export Failed", "Failed to export inventory to CSV.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Export failed: {str(e)}")


class ProductDialog(QDialog):
    def __init__(self, parent=None, title="Product", name="", qty=0, buying_price=0.0, selling_price=0.0, details="", category="Electronics"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(600, 500)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_label = QLabel(title)
        header_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        header_label.setStyleSheet("color: #2c3e50;")
        layout.addWidget(header_label)
        
        # Create a form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        # Create input fields
        self.name_input = QLineEdit(str(name))
        self.name_input.setPlaceholderText("Enter product name")
        
        from PyQt5.QtWidgets import QTextEdit
        self.details_input = QTextEdit()
        self.details_input.setPlaceholderText("Enter product description and details")
        self.details_input.setText(str(details) if details is not None else "")
        self.details_input.setMaximumHeight(100)
        
        self.category_input = QComboBox()
        self.category_input.addItems(["Electronics", "Food", "Clothing", "Other"])
        if category is not None:
            index = self.category_input.findText(str(category))
            if index >= 0:
                self.category_input.setCurrentIndex(index)
        
        self.qty_input = QLineEdit(str(qty))
        self.qty_input.setValidator(QIntValidator(0, 999999))
        
        self.buying_price_input = QLineEdit(str(buying_price))
        self.buying_price_input.setValidator(QDoubleValidator(0.0, 999999.99, 2))
        
        self.selling_price_input = QLineEdit(str(selling_price))
        self.selling_price_input.setValidator(QDoubleValidator(0.0, 999999.99, 2))
        
        # Add fields to form
        form_layout.addRow("Product Name:", self.name_input)
        form_layout.addRow("Product Details:", self.details_input)
        form_layout.addRow("Category:", self.category_input)
        form_layout.addRow("Quantity:", self.qty_input)
        form_layout.addRow("Buying Price ($):", self.buying_price_input)
        form_layout.addRow("Selling Price ($):", self.selling_price_input)
        
        layout.addLayout(form_layout)
        
        # Add suggested markup calculation
        markup_layout = QHBoxLayout()
        markup_info = QLabel("Suggested: Cost + 20% = $0.00")
        markup_info.setStyleSheet("color: #7f8c8d; font-style: italic;")
        markup_layout.addStretch()
        markup_layout.addWidget(markup_info)
        layout.addLayout(markup_layout)
        
        # Connect buying price to auto-calculate markup
        def update_suggested_price():
            try:
                cost = float(self.buying_price_input.text() or "0")
                markup_info.setText(f"Suggested: Cost + 20% = ${cost * 1.2:.2f}")
            except ValueError:
                markup_info.setText("Suggested: Cost + 20% = $0.00")
        
        self.buying_price_input.textChanged.connect(update_suggested_price)
        update_suggested_price()  # Initial calculation
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        
        self.save_btn = QPushButton("Save")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)
        
        buttons_layout.addWidget(self.cancel_btn)
        buttons_layout.addWidget(self.save_btn)
        
        layout.addStretch()
        layout.addLayout(buttons_layout)
        
        # Connect signals
        self.save_btn.clicked.connect(self.validate_and_accept)
        self.cancel_btn.clicked.connect(self.reject)
        
    def validate_and_accept(self):
        # Basic validation
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Product name cannot be empty!")
            return
            
        qty_text = self.qty_input.text()
        try:
            qty_val = int(float(qty_text))
            if qty_val < 0:
                raise ValueError
        except Exception:
            QMessageBox.warning(self, "Validation Error", "Quantity must be a positive integer!")
            return
            
        if not self.buying_price_input.text() or self.buying_price_input.text().lower() == 'none':
            QMessageBox.warning(self, "Validation Error", "Buying price must be a positive number!")
            return
        try:
            buying_price_val = float(self.buying_price_input.text())
            if buying_price_val < 0:
                raise ValueError
        except Exception:
            QMessageBox.warning(self, "Validation Error", "Buying price must be a positive number!")
            return
            
        if not self.selling_price_input.text() or self.selling_price_input.text().lower() == 'none':
            QMessageBox.warning(self, "Validation Error", "Selling price must be a positive number!")
            return
        try:
            selling_price_val = float(self.selling_price_input.text())
            if selling_price_val < 0:
                raise ValueError
        except Exception:
            QMessageBox.warning(self, "Validation Error", "Selling price must be a positive number!")
            return
            
        self.accept()