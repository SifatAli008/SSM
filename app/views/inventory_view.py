from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout,
    QGroupBox, QLineEdit, QSizePolicy, QDialog, QFormLayout, QMessageBox,
    QTableView, QHeaderView, QAbstractItemView, QComboBox, QFileDialog,
    QCheckBox, QSpacerItem, QFrame, QToolButton, QApplication, QStyledItemDelegate,
    QItemDelegate
)
from PyQt5.QtCore import Qt, QTimer, QDateTime, QSortFilterProxyModel, pyqtSlot, QSize
from PyQt5.QtGui import QFont, QIntValidator, QDoubleValidator, QIcon, QColor
from app.views.widgets.components import Button  # Import our standardized Button component

# Custom delegate for displaying checkboxes in the table
class CheckBoxDelegate(QItemDelegate):
    def createEditor(self, parent, option, index):
        checkbox = QCheckBox(parent)
        checkbox.setStyleSheet("QCheckBox { margin-left: 15px; }")
        return checkbox
    
    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.EditRole)
        if value:
            editor.setChecked(True)
        else:
            editor.setChecked(False)
    
    def setModelData(self, editor, model, index):
        model.setData(index, editor.isChecked(), Qt.EditRole)
    
    def paint(self, painter, option, index):
        # Draw a checkbox
        checked = index.model().data(index, Qt.DisplayRole)
        checkbox = QCheckBox()
        if checked:
            checkbox.setChecked(True)
        
        # Center the checkbox in the cell
        checkbox.setGeometry(option.rect)
        if option.state & QItemDelegate.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())
            
        # Calculate position for checkbox
        x = option.rect.x() + (option.rect.width() - checkbox.sizeHint().width()) // 2
        y = option.rect.y() + (option.rect.height() - checkbox.sizeHint().height()) // 2
        
        # Save painter state
        painter.save()
        # Move painter to the position
        painter.translate(x, y)
        # Draw the checkbox
        checkbox.render(painter)
        # Restore painter state
        painter.restore()

# Custom delegate for the Product Details column with text field
class DetailsDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        editor.setStyleSheet("""
            QLineEdit {
                border: 1px solid #bbb;
                border-radius: 3px;
                padding: 5px;
                background-color: white;
            }
        """)
        return editor
    
    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.EditRole)
        if value:
            editor.setText(str(value))
    
    def setModelData(self, editor, model, index):
        model.setData(index, editor.text(), Qt.EditRole)
    
    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

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
        self.setStyleSheet('''
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
            QPushButton#add {
                background-color: #3498db;
            }
            QPushButton#add:hover {
                background-color: #2980b9;
            }
            QPushButton#update {
                background-color: #f39c12;
            }
            QPushButton#update:hover {
                background-color: #e67e22;
            }
            QPushButton#delete {
                background-color: #e74c3c;
            }
            QPushButton#delete:hover {
                background-color: #c0392b;
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
        ''')

        main_layout = QVBoxLayout()

        # Cards Row - improved to match dashboard style
        self.create_info_cards(main_layout)
        
        # Table and Actions Area
        main_layout.addLayout(self.create_table_section())

        self.setLayout(main_layout)
        self.setup_model()
        self.refresh_from_controller()

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
        table_section.setContentsMargins(10, 10, 10, 10)
        
        # Main container frame with clean white background
        table_frame = QFrame()
        table_frame.setObjectName("cardFrame")
        table_frame.setStyleSheet("""
            #cardFrame {
                background-color: white;
                border: 1px solid #dcdcdc;
                border-radius: 6px;
            }
        """)
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(0, 0, 0, 0)  # Remove internal padding

        # Search and Filter Row
        search_filter_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search Bar")
        self.search_input.textChanged.connect(self.apply_filters)
        search_filter_layout.addWidget(self.search_input)

        self.category_filter = QComboBox()
        self.category_filter.addItems(["All", "Electronics", "Food", "Clothing", "Other"])
        self.category_filter.currentIndexChanged.connect(self.apply_filters)
        search_filter_layout.addWidget(self.category_filter)

        self.price_filter = QLineEdit()
        self.price_filter.setPlaceholderText("Price Filter")
        self.price_filter.setValidator(QDoubleValidator(0.0, 999999.99, 2))
        self.price_filter.textChanged.connect(self.apply_filters)
        search_filter_layout.addWidget(self.price_filter)

        table_layout.addLayout(search_filter_layout)

        # Create the table with improved styling
        self.table_view = QTableView()
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setShowGrid(True)
        self.table_view.setGridStyle(Qt.SolidLine)
        self.table_view.verticalHeader().setVisible(True)  # Show row numbers
        self.table_view.verticalHeader().setDefaultSectionSize(40)  # Set row height
        
        # Style the vertical header (row numbers) to match reference
        self.table_view.verticalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 5px;
                border: 1px solid #dcdcdc;
                font-size: 12px;
            }
        """)
        
        self.table_view.clicked.connect(self.on_table_clicked)
        self.table_view.setStyleSheet("""
            QTableView {
                border: none;
                background-color: white;
                alternate-background-color: #f8f8f8;
                gridline-color: #e0e0e0;
            }
            QTableView::item {
                border-bottom: 1px solid #e0e0e0;
                padding: 5px;
                font-size: 14px;
            }
            QTableView::item:selected {
                background-color: #e7f4ff;
                color: #2c3e50;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                color: #333;
                font-weight: bold;
                padding: 10px 5px;
                border: 1px solid #dcdcdc;
                border-top: 0px;
                border-left: 0px;
                border-right: 1px solid #dcdcdc;
                font-size: 14px;
            }
            QHeaderView::section:first {
                border-left: 1px solid #dcdcdc;
            }
            QHeaderView {
                background-color: #f0f0f0;
            }
            QHeaderView::down-arrow, QHeaderView::up-arrow {
                subcontrol-position: center right;
            }
            QTableView QLineEdit {
                border: 1px solid #bbb;
                padding: 5px;
                background-color: white;
            }
        """)
        
        table_layout.addWidget(self.table_view)
        
        # Bottom action buttons container
        button_container = QFrame()
        button_container.setStyleSheet("""
            background-color: #f5f5f5;
            border-top: 1px solid #dcdcdc;
        """)
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(15, 15, 15, 15)
        
        # Add button
        self.add_button = Button("Add", variant="primary")
        
        # Edit and Delete buttons
        self.edit_button = Button("Update", variant="warning")
        
        self.delete_button = Button("Delete", variant="danger")
        
        # Export button
        self.export_button = Button("Export CSV", variant="primary")
        
        # Layout the buttons exactly as in the reference
        button_layout.addWidget(self.add_button)
        button_layout.addSpacerItem(QSpacerItem(30, 10, QSizePolicy.Fixed, QSizePolicy.Minimum))
        
        # Add action buttons in the center
        button_layout.addWidget(self.edit_button)
        button_layout.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Fixed, QSizePolicy.Minimum))
        button_layout.addWidget(self.delete_button)
        button_layout.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Fixed, QSizePolicy.Minimum))
        
        # Add export button to layout
        button_layout.addWidget(self.export_button)
        
        # Push refresh button to the right
        button_layout.addStretch(1)
        
        # Connect buttons to actions
        self.add_button.clicked.connect(self.show_add_dialog)
        self.edit_button.clicked.connect(self.show_edit_dialog)
        self.delete_button.clicked.connect(self.delete_products)
        self.export_button.clicked.connect(self.export_to_csv)
        
        # Initially disable edit/delete buttons until row is selected
        self.edit_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        
        table_layout.addWidget(button_container)
        table_section.addWidget(table_frame)
        
        return table_section

    def update_stock_info(self, stock, low_stock, recent, total_value=0):
        # Update card values if they exist
        if hasattr(self, 'card_labels') and self.card_labels:
            if 'stock' in self.card_labels:
                self.card_labels["stock"]["value"].setText(f"{stock:,}")
            if 'low' in self.card_labels:
                self.card_labels["low"]["value"].setText(f"{low_stock}")
            if 'recent' in self.card_labels:
                self.card_labels["recent"]["value"].setText(f"{recent}")
            if 'value' in self.card_labels:
                self.card_labels["value"]["value"].setText(f"${total_value:,.2f}")
        
        # Refresh the table view
        if hasattr(self, 'table_view') and self.table_view.model():
            self.table_view.model().layoutChanged.emit()

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
            
            # Hide ID column and other unnecessary columns, keep only what's in the reference
            for col in range(self.table_view.model().columnCount()):
                self.table_view.hideColumn(col)
            
            # Show only relevant columns
            column_mapping = {
                0: 0,  # Vertical header will be used for row numbers
                1: 0,  # ID/Serial Number 
                2: 1,  # Product Name
                3: 2,  # Product Details
                4: 3,  # Product Quantity
            }
            
            # Show the necessary columns
            for model_col, view_col in column_mapping.items():
                if model_col < self.table_view.model().columnCount():
                    self.table_view.showColumn(model_col)
            
            # Set column headers to match reference image
            headers = ["Serial Number", "Product Name", "Product Details", "Product Quantity"]
            for i, header in enumerate(headers):
                self.table_view.model().setHeaderData(i+1, Qt.Horizontal, header)
            
            # Make the "Product Details" column editable with custom delegate
            details_delegate = DetailsDelegate(self.table_view)
            self.table_view.setItemDelegateForColumn(3, details_delegate)  # Index 3 is Product Details
            
            # Enable editing mode for the table
            self.table_view.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
            
            # Set column widths to match reference image
            self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
            self.table_view.setColumnWidth(1, 180)  # Serial Number
            self.table_view.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)  # Product Name
            self.table_view.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)  # Product Details
            self.table_view.setColumnWidth(4, 150)  # Product Quantity
            
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
            
            # Reset any proxy model filtering 
            if hasattr(self, 'proxy_model'):
                self.proxy_model.setFilterFixedString("")

    def on_table_clicked(self, index):
        self.selected_row = self.proxy_model.mapToSource(index).row()
        self.edit_button.setEnabled(True)
        self.delete_button.setEnabled(True)

    def on_selection_changed(self, selected, deselected):
        indices = self.table_view.selectionModel().selectedRows()
        if indices:
            # Get the selected row's source model index
            index = self.proxy_model.mapToSource(indices[0])
            self.selected_row = index.row()
            self.edit_button.setEnabled(True)
            self.delete_button.setEnabled(True)
        else:
            self.selected_row = -1
            self.edit_button.setEnabled(False)
            self.delete_button.setEnabled(False)

    def show_add_dialog(self):
        dialog = ProductDialog(self, "Add New Product")
        if dialog.exec_():
            name = dialog.name_input.text()
            details = dialog.details_input.toPlainText()
            category = dialog.category_input.currentText()
            
            try:
                stock = int(dialog.qty_input.text())
                buying_price = float(dialog.buying_price_input.text())
                selling_price = float(dialog.selling_price_input.text())
            except ValueError:
                QMessageBox.warning(self, "Invalid Input", "Please enter valid numbers for quantity and prices.")
                return
            
            if self.controller and hasattr(self.controller, 'add_product'):
                # Add the product with all details
                success = self.controller.add_product(
                    name, 
                    stock, 
                    buying_price, 
                    selling_price, 
                    details=details, 
                    category=category
                )
                
                if success:
                    self.refresh_from_controller()
                    QMessageBox.information(self, "Success", f"Product '{name}' added successfully!")
                else:
                    QMessageBox.critical(self, "Error", "Failed to add product. Please try again.")
            else:
                QMessageBox.warning(self, "Not Implemented", "Add functionality is not available.")

    def show_edit_dialog(self):
        if self.selected_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a product to edit.")
            return
            
        # Get current values from the model using the updated column mapping
        id_col = 1  # Serial Number (ID column)
        name_col = 2  # Product Name
        details_col = 3  # Product Details
        stock_col = 4  # Product Quantity
        
        # Get data from model
        product_id = self.controller.model.data(self.controller.model.index(self.selected_row, id_col))
        name = self.controller.model.data(self.controller.model.index(self.selected_row, name_col))
        details = self.controller.model.data(self.controller.model.index(self.selected_row, details_col))
        stock = self.controller.model.data(self.controller.model.index(self.selected_row, stock_col))
        
        # Get additional fields if they exist in the database
        # The controller methods return the actual values, not dictionaries
        buying_price = 0.0
        selling_price = 0.0
        category = "Other"
        
        # Get buying price from column 5 (if available)
        if self.controller.model.columnCount() > 5:
            buying_price_val = self.controller.model.data(self.controller.model.index(self.selected_row, 5))
            if buying_price_val is not None:
                try:
                    buying_price = float(buying_price_val)
                except (ValueError, TypeError):
                    pass
        
        # Get selling price from column 6 (if available)
        if self.controller.model.columnCount() > 6:
            selling_price_val = self.controller.model.data(self.controller.model.index(self.selected_row, 6))
            if selling_price_val is not None:
                try:
                    selling_price = float(selling_price_val)
                except (ValueError, TypeError):
                    pass
        
        # Get category from column 3 (category field)
        if self.controller.model.columnCount() > 3:
            category_val = self.controller.model.data(self.controller.model.index(self.selected_row, 3))
            if category_val is not None:
                category = str(category_val)
        
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
            # Prepare updated data with correct column indices
            updated_data = {
                name_col: dialog.name_input.text(),
                details_col: dialog.details_input.toPlainText(),
                stock_col: int(dialog.qty_input.text())
            }
            
            # Add additional fields to the update
            additional_data = {
                "buying_price": float(dialog.buying_price_input.text()),
                "selling_price": float(dialog.selling_price_input.text()),
                "category": dialog.category_input.currentText()
            }
            
            # Update the product
            if hasattr(self.controller, 'update_item'):
                success = self.controller.update_item(self.selected_row, updated_data, additional_data)
                if success:
                    self.refresh_from_controller()
                    QMessageBox.information(self, "Success", f"Product updated successfully!")
                else:
                    QMessageBox.critical(self, "Error", "Failed to update product. Please try again.")
            else:
                QMessageBox.warning(self, "Not Implemented", "Update functionality is not available.")

    def delete_products(self):
        if self.selected_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a product to delete.")
            return
        
        # Get product name for confirmation message
        product_name = self.controller.model.data(self.controller.model.index(self.selected_row, 2))
        
        # Ask for confirmation
        confirm = QMessageBox.question(
            self, 
            "Confirm Deletion", 
            f"Are you sure you want to delete product '{product_name}'?",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            success = self.controller.delete_item(self.selected_row)
            if success:
                self.selected_row = -1
                self.edit_button.setEnabled(False)
                self.delete_button.setEnabled(False)
                self.refresh_from_controller()
                QMessageBox.information(self, "Success", f"Product '{product_name}' deleted successfully!")
            else:
                QMessageBox.critical(self, "Error", "Failed to delete product. Please try again.")

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

    def apply_filters(self):
        search_text = self.search_input.text().lower()
        category = self.category_filter.currentText()
        price_text = self.price_filter.text()
        price = float(price_text) if price_text else None

        filter_string = ""

        if search_text:
            filter_string += f"name LIKE '%{search_text}%'"

        if category != "All":
            if filter_string:
                filter_string += " AND "
            filter_string += f"category = '{category}'"

        if price is not None:
            if filter_string:
                filter_string += " AND "
            filter_string += f"selling_price <= {price}"

        self.proxy_model.setFilterFixedString(filter_string)

    def refresh_data(self):
        """Refresh all inventory data to ensure real-time updates"""
        print("🔄 Refreshing inventory data...")
        if self.controller:
            # Refresh the model data
            self.controller.model.select()
            
            # Update summary cards
            self.refresh_from_controller()
            
            # If a filter is active, reapply it
            if hasattr(self, 'filter_text') and self.filter_text.text():
                self.apply_filters()
        else:
            print("⚠️ No controller available for refresh")
            
        return True

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
        
        # Get all categories and add "Add New Category" option
        self.category_input = QComboBox()
        categories = ["Electronics", "Food", "Clothing", "Other", "--- Add New Category ---"]
        self.category_input.addItems(categories)
        self.category_input.currentIndexChanged.connect(self.handle_category_change)
        
        # Set current category if provided
        if category is not None and category.strip():
            # Check if category exists in dropdown
            index = self.category_input.findText(str(category))
            if index >= 0:
                self.category_input.setCurrentIndex(index)
            else:
                # If it's a custom category not in the list, add it
                self.category_input.insertItem(len(categories) - 1, category)
                self.category_input.setCurrentText(category)
        
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
        
        self.cancel_btn = Button("Cancel", variant="secondary")
        self.save_btn = Button("Save", variant="success")
        
        buttons_layout.addWidget(self.cancel_btn)
        buttons_layout.addWidget(self.save_btn)
        
        layout.addStretch()
        layout.addLayout(buttons_layout)
        
        # Connect signals
        self.save_btn.clicked.connect(self.validate_and_accept)
        self.cancel_btn.clicked.connect(self.reject)
    
    def handle_category_change(self, index):
        """Handle selection of 'Add New Category' option"""
        if self.category_input.currentText() == "--- Add New Category ---":
            # Prompt user to enter new category
            from PyQt5.QtWidgets import QInputDialog
            new_category, ok = QInputDialog.getText(
                self, 
                "Add New Category", 
                "Enter new category name:",
                QLineEdit.Normal, 
                ""
            )
            
            if ok and new_category.strip():
                # Add the new category before the "Add New Category" option
                self.category_input.insertItem(self.category_input.count() - 1, new_category)
                # Select the new category
                self.category_input.setCurrentText(new_category)
            else:
                # User canceled or entered empty text, revert to first category
                self.category_input.setCurrentIndex(0)
        
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
            
        # Check if "Add New Category" is selected
        if self.category_input.currentText() == "--- Add New Category ---":
            QMessageBox.warning(self, "Validation Error", "Please select a valid category or add a new one!")
            return
            
        self.accept()