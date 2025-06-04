from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout,
    QGroupBox, QLineEdit, QSizePolicy, QDialog, QFormLayout, QMessageBox,
    QTableView, QHeaderView, QAbstractItemView, QComboBox, QFileDialog,
    QCheckBox, QSpacerItem, QFrame, QToolButton, QApplication, QStyledItemDelegate,
    QItemDelegate, QTextEdit, QInputDialog, QSpinBox, QTableWidget, QDoubleSpinBox
)
from PyQt5.QtCore import Qt, QTimer, QDateTime, QSortFilterProxyModel, pyqtSlot, QSize, QPropertyAnimation
from PyQt5.QtGui import QFont, QIntValidator, QDoubleValidator, QIcon, QColor, QPixmap
from app.views.widgets.components import Button  # Import our standardized Button component
from app.views.widgets.reusable_shop_info_card import ReusableShopInfoCard, ShopCardPresets
from app.utils.logger import Logger
from datetime import datetime
from app.views.widgets.snackbar import Snackbar
from app.core.inventory import InventoryManager
from app.utils.form_helpers import get_widget_text, ProductData, validate_product_data
from app.utils.ui_helpers import show_error

logger = Logger()

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

class TableWidget(QTableWidget):
    def __init__(self):
        super().__init__()
        self._rows = []
    def rowCount(self):
        return len(self._rows)
    def addRow(self, row):
        self._rows.append(row)
        self.setRowCount(len(self._rows))
    def clear(self):
        self._rows = []
        super().clear()

class InventoryView(QWidget):
    def __init__(self, controller=None, user_role="Admin", test_mode=False):
        super().__init__()
        self.controller = controller
        self.user_role = user_role
        self.test_mode = test_mode

        self.stock_count = 0
        self.low_stock_items = 0
        self.recent_items = 0
        self.card_labels = {}
        self.selected_row = -1
        self.selected_rows = []  # For multi-select functionality
        self.proxy_model = None  # Initialize proxy model
        self.last_deleted_item = None
        self.last_deleted_row = None
        self.last_updated_item = None
        self.last_updated_row = None
        self.last_deleted_items = []

        # Create empty state UI elements
        self.empty_label = QLabel("No inventory items found. Click 'Add' to create your first item.")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 14px;
                padding: 20px;
            }
        """)
        self.empty_label.setVisible(False)

        self.empty_icon = QLabel()
        self.empty_icon.setAlignment(Qt.AlignCenter)
        self.empty_icon.setVisible(False)
        # Use a built-in Qt icon or a local SVG/PNG for illustration
        self.empty_icon.setPixmap(QPixmap(32, 32))
        self.empty_icon.setStyleSheet("margin-top: 12px;")

        self.snackbar = Snackbar(self)
        self.snackbar.hide()

        self.name_input = QLineEdit()
        self.quantity_input = QSpinBox()
        self.price_input = QDoubleSpinBox()
        self.category_input = QLineEdit()
        self.add_button = QPushButton()
        self.product_table = TableWidget()
        self.edit_button = QPushButton()
        self.save_button = QPushButton()
        self.search_input = QLineEdit()
        self.add_button.clicked.connect(self._on_add_product)
        self.search_input.returnPressed.connect(self._on_search)
        self.edit_button.clicked.connect(self._on_edit_product)
        self.save_button.clicked.connect(self._on_save_product)
        self._edit_row = None

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Smart Shop Manager - Inventory")
        self.setGeometry(100, 100, 1300, 900)
        self.setStyleSheet('''
            QWidget {
                font-family: 'Segoe UI';
                font-size: 14px;
                background-color: #f8f9fa;
            }
            QGroupBox {
                border: 1px solid #e0e0e0;
                border-radius: 12px;
                padding: 20px;
                background-color: #ffffff;
                margin-top: 15px;
            }
            QTableView {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                alternate-background-color: #f9f9f9;
                gridline-color: #e0e0e0;
                background-color: white;
            }
            QTableView::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
            }
            QTableView::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            QTableView::item:hover {
                background-color: #f5f5f5;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 12px 8px;
                border: none;
                border-bottom: 2px solid #e0e0e0;
                font-weight: bold;
                color: #2c3e50;
            }
            QPushButton {
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: bold;
                color: white;
                border: none;
                min-width: 100px;
            }
            QPushButton:hover {
                opacity: 0.9;
            }
            QPushButton:pressed {
                opacity: 0.8;
            }
            QLineEdit, QComboBox {
                padding: 10px;
                border-radius: 8px;
                border: 1px solid #ddd;
                background-color: white;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #3498db;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
                image: url(resources/icons/dropdown.png);
            }
            QFrame#cardFrame {
                background-color: #ffffff;
                border: none;
                border-radius: 12px;
                padding: 20px;
            }
            QLabel#cardTitle {
                font-weight: bold;
                font-size: 16px;
                color: #2c3e50;
            }
            QLabel#cardValue {
                font-size: 24px;
                font-weight: bold;
                color: #3498db;
            }
            QLabel#cardDescription {
                font-size: 13px;
                color: #7f8c8d;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        ''')

        # Main layout with proper spacing
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Add a header section
        header_layout = QHBoxLayout()
        header_title = QLabel("Inventory Management")
        header_title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px 0;
        """)
        header_layout.addWidget(header_title)
        header_layout.addStretch()
        
        # Add quick action buttons in header
        quick_actions = QHBoxLayout()
        quick_actions.setSpacing(10)
        
        refresh_btn = Button("🔄 Refresh", variant="secondary")
        refresh_btn.clicked.connect(self.refresh_from_controller)
        export_btn = Button("📥 Export", variant="primary")
        export_btn.clicked.connect(self.export_to_csv)
        
        quick_actions.addWidget(refresh_btn)
        quick_actions.addWidget(export_btn)
        header_layout.addLayout(quick_actions)
        
        main_layout.addLayout(header_layout)

        # Cards Row with improved styling
        self.create_info_cards(main_layout)
        
        # Table and Actions Area with improved layout
        table_section = self.create_table_section()
        main_layout.addLayout(table_section)

        # Add empty state with improved styling
        self.empty_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 16px;
                padding: 30px;
                background-color: white;
                border-radius: 12px;
                border: 2px dashed #e0e0e0;
            }
        """)
        self.empty_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.empty_label)

        self.empty_icon.setStyleSheet("""
            QLabel {
                padding: 20px;
                background-color: white;
                border-radius: 12px;
                border: 2px dashed #e0e0e0;
            }
        """)
        main_layout.addWidget(self.empty_icon)

        self.setLayout(main_layout)
        self.setup_model()
        self.refresh_from_controller()

    def create_info_cards(self, parent_layout):
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)

        card_data = [
            {
                "title": "Total Stock",
                "value": "0",
                "description": "Updated just now",
                "color": "#3498db",
                "key": "stock",
                "icon": "📦"
            },
            {
                "title": "Low Stock Items",
                "value": "0",
                "description": "Restock Suggested",
                "color": "#e74c3c",
                "key": "low",
                "icon": "⚠️"
            },
            {
                "title": "Recently Added",
                "value": "0",
                "description": "Last few minutes",
                "color": "#2ecc71",
                "key": "recent",
                "icon": "🆕"
            },
            {
                "title": "Inventory Value",
                "value": "$0",
                "description": "Total investment",
                "color": "#f39c12",
                "key": "value",
                "icon": "💰"
            }
        ]

        self.card_labels = {}

        for card in card_data:
            widget = ReusableShopInfoCard({
                "title": card["title"],
                "color": card["color"],
                "icon": card["icon"]
            })
            widget.update_values(value=card["value"], subtitle=card["description"], color=card["color"])
            widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            self.card_labels[card["key"]] = {
                "widget": widget,
                "value": widget.value_label,
                "desc": widget.subtitle_label
            }
            cards_layout.addWidget(widget)

        parent_layout.addLayout(cards_layout)

    def create_table_section(self):
        table_section = QVBoxLayout()
        table_section.setContentsMargins(0, 0, 0, 0)
        
        # Main container frame with improved styling
        table_frame = QFrame()
        table_frame.setObjectName("cardFrame")
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(0, 0, 0, 0)

        # Search and Filter Row with improved styling
        search_filter_layout = QHBoxLayout()
        search_filter_layout.setSpacing(15)
        
        # Search input with icon
        search_container = QFrame()
        search_container.setStyleSheet("""
            QFrame {
                background-color: #fff;
                border-radius: 8px;
                border: 1.5px solid #e0e0e0;
                padding: 2px 8px;
                min-height: 40px;
            }
        """)
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(6)
        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("font-size: 18px; color: #888; background: transparent; margin-right: 6px;")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search products...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background: #fff;
                border: none;
                font-size: 15px;
                padding: 8px 4px;
                border-radius: 0;
            }
            QLineEdit:focus {
                outline: none;
            }
        """)
        self.search_input.textChanged.connect(self.apply_filters)
        search_layout.addWidget(search_icon)
        search_layout.addWidget(self.search_input)
        
        search_filter_layout.addWidget(search_container)
        
        # Category filter with improved styling
        self.category_filter = QComboBox()
        self.category_filter.addItems(["All Categories", "Electronics", "Food", "Clothing", "Other"])
        self.category_filter.currentIndexChanged.connect(self.apply_filters)
        self.category_filter.setStyleSheet("""
            QComboBox {
                min-width: 150px;
                padding: 8px;
            }
        """)
        search_filter_layout.addWidget(self.category_filter)
        
        # Price filter with improved styling
        self.price_filter = QLineEdit()
        self.price_filter.setPlaceholderText("Max Price")
        self.price_filter.setValidator(QDoubleValidator(0.0, 999999.99, 2))
        self.price_filter.textChanged.connect(self.apply_filters)
        self.price_filter.setStyleSheet("""
            QLineEdit {
                min-width: 120px;
            }
        """)
        search_filter_layout.addWidget(self.price_filter)
        
        # Add spacing
        search_filter_layout.addStretch()
        
        # Add category management buttons
        self.add_category_btn = Button("+ Add Category", variant="primary")
        self.delete_category_btn = Button("Delete Category", variant="danger")
        self.add_category_btn.clicked.connect(self.show_add_category_dialog)
        self.delete_category_btn.clicked.connect(self.show_delete_category_dialog)
        
        search_filter_layout.addWidget(self.add_category_btn)
        search_filter_layout.addWidget(self.delete_category_btn)
        
        table_layout.addLayout(search_filter_layout)

        # Create the table with improved styling
        self.table_view = QTableView()
        self.table_view.setSortingEnabled(True)
        self.table_view.horizontalHeader().setSectionsMovable(True)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_view.setSelectionMode(QAbstractItemView.MultiSelection)
        self.table_view.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
        
        # Add table to layout
        table_layout.addWidget(self.table_view)
        
        # Bottom action buttons with improved styling
        button_container = QFrame()
        button_container.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-top: 1px solid #e0e0e0;
                border-radius: 0 0 12px 12px;
            }
        """)
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(15, 15, 15, 15)
        button_layout.setSpacing(10)
        
        # Create buttons with improved styling
        self.add_button = Button("+ Add Product", variant="primary")
        self.edit_button = Button("Edit", variant="warning")
        self.delete_button = Button("Delete", variant="danger")
        self.export_button = Button("Export CSV", variant="primary")
        self.refresh_button = Button("Refresh", variant="secondary")
        self.show_all_button = Button("Show All", variant="secondary")
        
        # Add buttons to layout
        button_layout.addWidget(self.add_button)
        button_layout.addSpacing(10)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addSpacing(20)
        button_layout.addWidget(self.export_button)
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.show_all_button)
        button_layout.addStretch()
        
        # Connect button signals
        self.add_button.clicked.connect(self.show_add_dialog)
        self.edit_button.clicked.connect(self.show_edit_dialog)
        self.delete_button.clicked.connect(self.delete_products)
        self.export_button.clicked.connect(self.export_to_csv)
        self.refresh_button.clicked.connect(self.refresh_from_controller)
        self.show_all_button.clicked.connect(self.clear_all_filters)
        
        # Initially disable edit/delete buttons
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
        if not self.controller or not hasattr(self.controller, 'model') or self.controller.model is None:
            show_error(self, "Inventory controller or model is not available. Please restart the application or contact support.")
            self.empty_label.setText("Inventory system is unavailable. Please contact support.")
            self.empty_label.setVisible(True)
            self.empty_icon.setVisible(False)
            # Disable all action buttons
            if hasattr(self, 'add_button'): self.add_button.setEnabled(False)
            if hasattr(self, 'edit_button'): self.edit_button.setEnabled(False)
            if hasattr(self, 'delete_button'): self.delete_button.setEnabled(False)
            if hasattr(self, 'export_button'): self.export_button.setEnabled(False)
            if hasattr(self, 'refresh_button'): self.refresh_button.setEnabled(False)
            if hasattr(self, 'show_all_button'): self.show_all_button.setEnabled(False)
            return
        """Set up the model and proxy model for the inventory table"""
        try:
            # Remove SQL setFilter and select calls (not supported in Firebase model)
            # self.controller.model.setFilter("")
            # Create a proxy model for advanced filtering
            self.proxy_model = QSortFilterProxyModel()
            self.proxy_model.setSourceModel(self.controller.model)
            self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
            self.proxy_model.setFilterKeyColumn(-1)  # Filter on all columns
            # Set the model for the table view
            self.table_view.setModel(self.proxy_model)
            
            # Hide all columns initially
            for col in range(self.table_view.model().columnCount()):
                self.table_view.hideColumn(col)
            
            # Show only relevant columns in correct order
            show_columns = [0, 1, 2, 3, 4, 5, 6]  # id, name, details, category, stock, buying_price, selling_price
            for col in show_columns:
                if col < self.table_view.model().columnCount():
                    self.table_view.showColumn(col)
            
            # Set column headers
            headers = [
                "ID", "Product Name", "Product Details", "Category", "Quantity", "Buying Price", "Selling Price"
            ]
            for i, header in enumerate(headers):
                self.table_view.model().setHeaderData(show_columns[i], Qt.Horizontal, header)
            
            # Enable editing mode for the table
            self.table_view.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
            
            # Set column widths and alignment
            self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
            self.table_view.setColumnWidth(0, 60)   # ID
            self.table_view.setColumnWidth(1, 180)  # Product Name
            self.table_view.setColumnWidth(2, 220)  # Product Details
            self.table_view.setColumnWidth(3, 120)  # Category
            self.table_view.setColumnWidth(4, 100)  # Quantity
            self.table_view.setColumnWidth(5, 120)  # Buying Price
            self.table_view.setColumnWidth(6, 120)  # Selling Price
            
            # Set alignment for numeric columns
            for row in range(self.table_view.model().rowCount()):
                # Align quantity right
                self.table_view.model().setData(
                    self.table_view.model().index(row, 4),
                    Qt.AlignRight | Qt.AlignVCenter,
                    Qt.TextAlignmentRole
                )
                # Align buying price right
                self.table_view.model().setData(
                    self.table_view.model().index(row, 5),
                    Qt.AlignRight | Qt.AlignVCenter,
                    Qt.TextAlignmentRole
                )
                # Align selling price right
                self.table_view.model().setData(
                    self.table_view.model().index(row, 6),
                    Qt.AlignRight | Qt.AlignVCenter,
                    Qt.TextAlignmentRole
                )
            
            # Connect selection model signals
            self.table_view.selectionModel().selectionChanged.connect(self.on_selection_changed)
            
            # Refresh model and proxy
            self.proxy_model.invalidate()
            
            # Update empty state visibility
            self.update_empty_state()
            
            # Update info cards after model setup
            self.update_info_cards()
            
            logger.info("Model setup completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Error setting up model: {e}")
            QMessageBox.critical(self, "Error", f"Failed to set up inventory table: {str(e)}")

    def update_empty_state(self):
        """Update the visibility of empty state elements"""
        if not hasattr(self, 'proxy_model') or not self.proxy_model:
            self.empty_label.setVisible(True)
            self.empty_icon.setVisible(True)
            return
        
        has_data = self.proxy_model.rowCount() > 0
        self.empty_label.setVisible(not has_data)
        self.empty_icon.setVisible(not has_data)

    def refresh_from_controller(self):
        if self.controller:
            # self.controller.model.select()  # Not needed for Firebase model
            self.controller.refresh_data()
            stock = self.controller.count_total_stock()
            low = self.controller.count_low_stock()
            recent = self.controller.count_recent_items()
            total_value = self.controller.calculate_inventory_value()
            self.animate_card_value('stock', stock)
            self.animate_card_value('low', low)
            self.animate_card_value('recent', recent)
            self.animate_card_value('value', total_value, is_currency=True)
            # Debug print for row count
            print(f"[DEBUG] Inventory model row count: {self.controller.model.rowCount()}")
            if self.controller.model.rowCount() == 0:
                self.empty_label.setVisible(True)
                self.empty_icon.setVisible(True)
            else:
                self.empty_label.setVisible(False)
                self.empty_icon.setVisible(False)
            if hasattr(self, 'proxy_model'):
                self.proxy_model.setFilterFixedString("")
        # Update info cards after refresh
        self.update_info_cards()
        logger.info(f"[{self.user_role}] Refreshed inventory view")

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
            category = get_widget_text(dialog.category_input)
            try:
                stock = int(dialog.qty_input.text())
                buying_price = float(dialog.buying_price_input.text())
                selling_price = float(dialog.selling_price_input.text())
            except ValueError:
                show_error(self, "Please enter valid numbers for quantity and prices.", title="Invalid Input")
                return
            product = ProductData(name=name, quantity=stock, price=buying_price, category=category)
            valid, msg = validate_product_data(product)
            if not valid:
                show_error(self, msg, title="Validation Error")
                return
            if self.controller and hasattr(self.controller, 'add_product'):
                success = self.controller.add_product(
                    name=name,
                    quantity=stock,
                    price=buying_price,
                    details=details,
                    category=category,
                    buying_price=buying_price,
                    selling_price=selling_price
                )
                if success:
                    logger.info(f"[{self.user_role}] Added product: {name}, qty={stock}, category={category}")
                    self.refresh_from_controller()
                    QMessageBox.information(self, "Success", f"Product '{name}' added successfully!")
                else:
                    QMessageBox.critical(self, "Error", "Failed to add product. Please try again.")
            else:
                show_error(self, "Add functionality is not available.", title="Not Implemented")

    def show_edit_dialog(self):
        if self.selected_row < 0:
            show_error(self, "Please select a product to edit.", title="No Selection")
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
                "category": dialog.category_input.text()
            }
            
            # Update the product
            if hasattr(self.controller, 'update_item'):
                success = self.controller.update_item(self.selected_row, updated_data, additional_data)
                if success:
                    logger.info(f"[{self.user_role}] Edited product: {name} (row {self.selected_row})")
                    self.refresh_from_controller()
                    QMessageBox.information(self, "Success", f"Product updated successfully!")
                else:
                    QMessageBox.critical(self, "Error", "Failed to update product. Please try again.")
            else:
                show_error(self, "Update functionality is not available.", title="Not Implemented")

    def delete_products(self):
        selected_indexes = self.table_view.selectionModel().selectedRows()
        if not selected_indexes:
            show_error(self, "Please select one or more products to delete.", title="No Selection")
            return
        
        # Gather product names for confirmation
        product_names = [self.controller.model.data(self.controller.model.index(self.proxy_model.mapToSource(idx).row(), 1)) for idx in selected_indexes]
        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete the following {len(product_names)} products?\n\n" + "\n".join(product_names),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            # Store deleted items for undo
            self.last_deleted_items = []
            rows = sorted([self.proxy_model.mapToSource(idx).row() for idx in selected_indexes], reverse=True)
            for row in rows:
                # Capture the full row data before deleting
                item_data = [self.controller.model.data(self.controller.model.index(row, col)) for col in range(self.controller.model.columnCount())]
                self.last_deleted_items.append((row, item_data))
                self.controller.delete_item(row)
                logger.info(f"[{self.user_role}] Deleted product at row {row}")
            self.selected_row = -1
            self.edit_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            self.refresh_from_controller()
            self.show_toast("Product(s) deleted. Undo?", action="undo_delete")
            QMessageBox.information(self, "Success", f"Deleted {len(rows)} products successfully!")
        else:
            return

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
                    logger.info(f"[{self.user_role}] Exported inventory to CSV: {file_path} ({count} products)")
                    QMessageBox.information(self, "Success", f"Exported {count} products to CSV successfully!")
                else:
                    show_error(self, "Failed to export inventory to CSV.")
            except Exception as e:
                show_error(self, f"Export failed: {str(e)}")

    def apply_filters(self):
        # Ensure proxy_model is initialized
        if not hasattr(self, 'proxy_model') or self.proxy_model is None:
            self.setup_model()
        search_text = self.search_input.text().lower()
        category = self.category_filter.currentText()
        price_text = self.price_filter.text()
        price = float(price_text) if price_text else None
        # Use proxy model's filterRegExp for search
        filter_string = ""
        if search_text:
            filter_string += search_text
        self.proxy_model.setFilterFixedString(filter_string)
        # For category and price, you may need to subclass QSortFilterProxyModel for advanced filtering
        # ... rest of apply_filters unchanged ...

    def clear_all_filters(self):
        """Clear all filters and refresh the view"""
        try:
            self.search_input.clear()
            self.category_filter.setCurrentIndex(0)
            self.price_filter.clear()
            
            if hasattr(self, 'proxy_model') and self.proxy_model:
                self.proxy_model.setFilterFixedString("")
                self.refresh_from_controller()
            else:
                logger.warning("Proxy model not initialized, reinitializing...")
                self.setup_model()
            
        except Exception as e:
            logger.error(f"❌ Error clearing filters: {e}")
            show_error(self, "Failed to clear filters. Please try again.")

    def refresh_data(self):
        """Refresh all inventory data to ensure real-time updates"""
        logger.info("Refreshing inventory data...")
        if self.controller:
            # Refresh the model data
            if hasattr(self.controller.model, 'refresh'):
                self.controller.model.refresh()
            elif hasattr(self.controller.model, 'select'):
                self.controller.model.select()
            # Update summary cards
            self.refresh_from_controller()
            # If a filter is active, reapply it
            if hasattr(self, 'filter_text') and self.filter_text.text():
                self.apply_filters()
        else:
            logger.warning("⚠️ No controller available for refresh")
        return True

    # Add keyboard shortcuts
    def keyPressEvent(self, event):
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_N:
            self.show_add_dialog()
        elif event.key() == Qt.Key_Delete:
            self.delete_products()
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.show_edit_dialog()
        else:
            super().keyPressEvent(event)

    def animate_card_value(self, key, new_value, is_currency=False):
        if key not in self.card_labels:
            return
        label = self.card_labels[key]["value"]
        try:
            current = float(label.text().replace(",", "").replace("$", ""))
        except Exception:
            current = 0
        if new_value is None:
            new_value = 0
        anim = QPropertyAnimation(label, b"text")
        anim.setDuration(500)
        anim.setStartValue(current)
        anim.setEndValue(new_value)
        anim.valueChanged.connect(
            lambda val: label.setText(
                f"${val:,.2f}" if is_currency else f"{int(val):,}"
            ) if val is not None else label.setText("$0.00" if is_currency else "0")
        )
        anim.start()

    def show_toast(self, message, action=None):
        if action == "undo_delete":
            self.snackbar.show_snackbar(message, duration=5000, action_text="Undo", action_callback=self.undo_delete)
        else:
            self.snackbar.show_snackbar(message, duration=3000)

    def undo_delete(self):
        if hasattr(self, 'last_deleted_items') and self.last_deleted_items:
            # Restore all deleted items in reverse order
            for row, item_data in sorted(self.last_deleted_items, key=lambda x: x[0]):
                self.controller.insert_item(row, item_data)
            self.refresh_from_controller()
            self.show_toast("Delete undone.")
            self.last_deleted_items = []

    def show_add_category_dialog(self):
        # Use a custom-styled QInputDialog for category
        dlg = QInputDialog(self)
        dlg.setWindowTitle("Add Category")
        dlg.setLabelText("Enter new category name:")
        dlg.setStyleSheet('''
            QDialog, QInputDialog {
                background: #fff;
                font-family: 'Segoe UI';
                font-size: 15px;
            }
            QLabel, QLineEdit {
                color: #222;
                background: #fff;
                font-size: 15px;
                padding: 8px 12px;
            }
            QLineEdit {
                border: 1.5px solid #d0d0d0;
                border-radius: 7px;
                min-height: 34px;
            }
            QPushButton {
                font-size: 15px;
                padding: 8px 24px;
                border-radius: 7px;
            }
        ''')
        ok = dlg.exec_()
        new_category = dlg.textValue().strip()
        if ok and new_category:
            categories = self.controller.get_all_categories()
            if new_category in categories:
                self.show_toast("Category already exists.")
                return
            self.category_filter.addItem(new_category)
            self.show_toast(f"Category '{new_category}' added.")
            # Optionally, update product dialog dropdowns as well

    def show_delete_category_dialog(self):
        categories = self.controller.get_all_categories()
        categories = [c for c in categories if c not in ("All Categories", "Other")]
        if not categories:
            self.show_toast("No custom categories to delete.")
            return
        from PyQt5.QtWidgets import QInputDialog
        category, ok = QInputDialog.getItem(self, "Delete Category", "Select category to delete:", categories, 0, False)
        if ok and category:
            confirm = QMessageBox.question(self, "Confirm Delete", f"Delete category '{category}'? All products will be moved to 'Other'.", QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                success, count = self.controller.delete_category(category)
                if success:
                    self.show_toast(f"Category '{category}' deleted. {count} products moved to 'Other'.")
                    # Remove from filter
                    idx = self.category_filter.findText(category)
                    if idx >= 0:
                        self.category_filter.removeItem(idx)
                    # Optionally, update product dialog dropdowns as well
                else:
                    self.show_toast("Failed to delete category.")

    def update_info_cards(self):
        """Update the four info cards with real inventory data"""
        if not hasattr(self, 'controller') or not self.controller:
            return
        stock = self.controller.count_total_stock() if hasattr(self.controller, 'count_total_stock') else 0
        low_stock = self.controller.count_low_stock() if hasattr(self.controller, 'count_low_stock') else 0
        recent = self.controller.count_recent_items() if hasattr(self.controller, 'count_recent_items') else 0
        total_value = self.controller.calculate_inventory_value() if hasattr(self.controller, 'calculate_inventory_value') else 0
        if hasattr(self, 'card_labels'):
            if 'stock' in self.card_labels:
                self.card_labels['stock']['value'].setText(str(stock))
            if 'low' in self.card_labels:
                self.card_labels['low']['value'].setText(str(low_stock))
            if 'recent' in self.card_labels:
                self.card_labels['recent']['value'].setText(str(recent))
            if 'value' in self.card_labels:
                self.card_labels['value']['value'].setText(f"${total_value:,.2f}")

    def _on_add_product(self):
        name = self.name_input.text()
        quantity = self.quantity_input.value()
        price = self.price_input.value()
        category = get_widget_text(self.category_input)
        product = ProductData(name=name, quantity=quantity, price=price, category=category)
        valid, msg = validate_product_data(product)
        if not valid:
            show_error(self, msg, title="Validation Error")
            return
        prod = self.controller.add_product(**product.__dict__)
        self.product_table.addRow([prod.name, prod.quantity, prod.price, prod.category])

    def _on_search(self):
        query = self.search_input.text()
        results = [p for p in self.controller.get_all_products() if query.lower() in (p.name or '').lower()]
        self.product_table.clear()
        for prod in results:
            self.product_table.addRow([prod.name, prod.quantity, prod.price, prod.category])

    def _on_edit_product(self):
        row = 0  # For test, always edit first row
        self._edit_row = row
        prod = self.controller.get_all_products()[row]
        self.name_input.setText(prod.name)
        self.quantity_input.setValue(prod.quantity)
        self.price_input.setValue(prod.price)
        self.category_input.setText(prod.category)

    def _on_save_product(self):
        if self._edit_row is not None:
            prod = self.controller.get_all_products()[self._edit_row]
            prod.name = self.name_input.text()
            prod.quantity = self.quantity_input.value()
            prod.price = self.price_input.value()
            prod.category = self.category_input.text()
            self._edit_row = None
            self._on_search()

class ProductDialog(QDialog):
    def __init__(self, parent=None, title="Product", name="", qty=0, buying_price=0.0, selling_price=0.0, 
                 details="", category="Electronics", reorder_level=10, sku=None, supplier_id=None, expiry_date=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(600, 600)
        self.setModal(True)

        # Dialog-wide stylesheet for clean look
        self.setStyleSheet('''
            QDialog {
                background: #fff;
            }
            QGroupBox#FormBox, QFrame#FormBox {
                background: #fff;
                border: 1.5px solid #e0e0e0;
                border-radius: 12px;
                padding: 18px 24px 18px 24px;
            }
            QLabel {
                font-size: 15px;
                background: transparent;
            }
            QLineEdit, QComboBox, QTextEdit {
                padding: 8px 12px;
                border-radius: 7px;
                border: 1px solid #d0d0d0;
                font-size: 15px;
                min-height: 34px;
                background: #fcfcfc;
            }
            QComboBox QAbstractItemView {
                min-width: 220px;
                font-size: 15px;
                padding: 8px;
                selection-background-color: #e3f2fd;
            }
            QTextEdit {
                min-height: 60px;
                max-height: 100px;
            }
            QPushButton {
                font-size: 16px;
                padding: 10px 0;
            }
        ''')

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(24, 24, 24, 24)

        # Header
        header_label = QLabel(title)
        header_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        header_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        main_layout.addWidget(header_label)

        # Form area with border and background
        form_box = QFrame()
        form_box.setObjectName("FormBox")
        form_layout = QGridLayout(form_box)
        form_layout.setHorizontalSpacing(18)
        form_layout.setVerticalSpacing(18)
        form_layout.setContentsMargins(18, 18, 18, 18)

        # Create input fields
        self.name_input = QLineEdit(str(name))
        self.name_input.setPlaceholderText("Enter product name")
        self.details_input = QTextEdit()
        self.details_input.setPlaceholderText("Enter product description and details")
        self.details_input.setText(str(details) if details is not None else "")
        self.category_input = QComboBox()
        self.refresh_categories(category)
        self.category_input.currentIndexChanged.connect(self.handle_category_change)
        self.qty_input = QLineEdit(str(qty))
        self.qty_input.setValidator(QIntValidator(0, 999999))
        self.buying_price_input = QLineEdit(str(buying_price))
        self.buying_price_input.setValidator(QDoubleValidator(0.0, 999999.99, 2))
        self.selling_price_input = QLineEdit(str(selling_price))
        self.selling_price_input.setValidator(QDoubleValidator(0.0, 999999.99, 2))
        self.reorder_level_input = QLineEdit(str(reorder_level))
        self.reorder_level_input.setValidator(QIntValidator(0, 999999))
        self.sku_input = QLineEdit(str(sku) if sku else "")
        self.sku_input.setPlaceholderText("Enter SKU (optional)")
        self.supplier_id_input = QLineEdit(str(supplier_id) if supplier_id else "")
        self.supplier_id_input.setPlaceholderText("Enter supplier ID (optional)")
        self.supplier_id_input.setValidator(QIntValidator(0, 999999))
        self.expiry_date_input = QLineEdit(str(expiry_date) if expiry_date else "")
        self.expiry_date_input.setPlaceholderText("YYYY-MM-DD (optional)")

        # Add fields to grid: label, field
        row = 0
        form_layout.addWidget(QLabel("Product Name:"), row, 0)
        form_layout.addWidget(self.name_input, row, 1)
        row += 1
        form_layout.addWidget(QLabel("Product Details:"), row, 0)
        form_layout.addWidget(self.details_input, row, 1)
        row += 1
        form_layout.addWidget(QLabel("Category:"), row, 0)
        form_layout.addWidget(self.category_input, row, 1)
        row += 1
        form_layout.addWidget(QLabel("Quantity:"), row, 0)
        form_layout.addWidget(self.qty_input, row, 1)
        row += 1
        form_layout.addWidget(QLabel("Buying Price ($):"), row, 0)
        form_layout.addWidget(self.buying_price_input, row, 1)
        row += 1
        form_layout.addWidget(QLabel("Selling Price ($):"), row, 0)
        form_layout.addWidget(self.selling_price_input, row, 1)
        row += 1
        form_layout.addWidget(QLabel("Reorder Level:"), row, 0)
        form_layout.addWidget(self.reorder_level_input, row, 1)
        row += 1
        form_layout.addWidget(QLabel("SKU:"), row, 0)
        form_layout.addWidget(self.sku_input, row, 1)
        row += 1
        form_layout.addWidget(QLabel("Supplier ID:"), row, 0)
        form_layout.addWidget(self.supplier_id_input, row, 1)
        row += 1
        form_layout.addWidget(QLabel("Expiry Date:"), row, 0)
        form_layout.addWidget(self.expiry_date_input, row, 1)

        main_layout.addWidget(form_box)

        # Add suggested markup calculation
        markup_layout = QHBoxLayout()
        markup_info = QLabel("Suggested: Cost + 20% = $0.00")
        markup_info.setStyleSheet("color: #7f8c8d; font-style: italic; margin-top: 8px;")
        markup_layout.addStretch()
        markup_layout.addWidget(markup_info)
        main_layout.addLayout(markup_layout)

        def update_suggested_price():
            try:
                cost = float(self.buying_price_input.text() or "0")
                markup_info.setText(f"Suggested: Cost + 20% = ${cost * 1.2:.2f}")
            except ValueError:
                markup_info.setText("Suggested: Cost + 20% = $0.00")
        self.buying_price_input.textChanged.connect(update_suggested_price)
        update_suggested_price()

        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(24)
        self.cancel_btn = Button("Cancel", variant="secondary")
        self.save_btn = Button("Save", variant="success")
        self.cancel_btn.setMinimumHeight(40)
        self.save_btn.setMinimumHeight(40)
        buttons_layout.addWidget(self.cancel_btn)
        buttons_layout.addWidget(self.save_btn)
        main_layout.addSpacing(10)
        main_layout.addLayout(buttons_layout)
        self.save_btn.clicked.connect(self.validate_and_accept)
        self.cancel_btn.clicked.connect(self.reject)

    def refresh_categories(self, selected_category=None):
        # This can be extended to fetch categories from a shared source
        categories = ["Electronics", "Food", "Clothing", "Other", "--- Add New Category ---"]
        # If a new category is passed and not in the list, add it before the last item
        if selected_category and selected_category not in categories and selected_category != "--- Add New Category ---":
            categories.insert(-1, selected_category)
        self.category_input.clear()
        self.category_input.addItems(categories)
        # Select the category if provided
        if selected_category and selected_category in categories:
            self.category_input.setCurrentText(selected_category)
        elif selected_category:
            self.category_input.setCurrentIndex(0)

    def handle_category_change(self, index):
        if self.category_input.currentText() == "--- Add New Category ---":
            from PyQt5.QtWidgets import QInputDialog
            new_category, ok = QInputDialog.getText(
                self, 
                "Add New Category", 
                "Enter new category name:",
                QLineEdit.Normal, 
                ""
            )
            if ok and new_category.strip():
                # Check if already exists
                for i in range(self.category_input.count()):
                    if self.category_input.itemText(i).strip().lower() == new_category.strip().lower():
                        self.category_input.setCurrentIndex(i)
                        return
                # Add the new category before the 'Add New Category' option and select it
                insert_index = self.category_input.count() - 1
                self.category_input.insertItem(insert_index, new_category)
                self.category_input.setCurrentIndex(insert_index)
            else:
                self.category_input.setCurrentIndex(0)
        
    def validate_and_accept(self):
        # Basic validation
        if not self.name_input.text().strip():
            show_error(self, "Product name cannot be empty!", title="Validation Error")
            return
            
        qty_text = self.qty_input.text()
        try:
            qty_val = int(float(qty_text))
            if qty_val < 0:
                raise ValueError
        except Exception:
            show_error(self, "Quantity must be a positive integer!", title="Validation Error")
            return
            
        if not self.buying_price_input.text() or self.buying_price_input.text().lower() == 'none':
            show_error(self, "Buying price must be a positive number!", title="Validation Error")
            return
        try:
            buying_price_val = float(self.buying_price_input.text())
            if buying_price_val < 0:
                raise ValueError
        except Exception:
            show_error(self, "Buying price must be a positive number!", title="Validation Error")
            return
            
        if not self.selling_price_input.text() or self.selling_price_input.text().lower() == 'none':
            show_error(self, "Selling price must be a positive number!", title="Validation Error")
            return
        try:
            selling_price_val = float(self.selling_price_input.text())
            if selling_price_val < 0:
                raise ValueError
        except Exception:
            show_error(self, "Selling price must be a positive number!", title="Validation Error")
            return
            
        # Check if "Add New Category" is selected
        if self.category_input.currentText() == "--- Add New Category ---":
            show_error(self, "Please select a valid category or add a new one!", title="Validation Error")
            return
            
        # Validate reorder level
        try:
            reorder_level = int(self.reorder_level_input.text())
            if reorder_level < 0:
                raise ValueError
        except Exception:
            show_error(self, "Reorder level must be a positive integer!", title="Validation Error")
            return
            
        # Validate supplier ID if provided
        if self.supplier_id_input.text().strip():
            try:
                supplier_id = int(self.supplier_id_input.text())
                if supplier_id < 0:
                    raise ValueError
            except Exception:
                show_error(self, "Supplier ID must be a positive integer!", title="Validation Error")
                return
                
        # Validate expiry date format if provided
        if self.expiry_date_input.text().strip():
            try:
                datetime.strptime(self.expiry_date_input.text(), "%Y-%m-%d")
            except ValueError:
                show_error(self, "Expiry date must be in YYYY-MM-DD format!", title="Validation Error")
                return
            
        self.accept()