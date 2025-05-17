"""
Smart Shop Manager - UI Components
File: app/views/widgets/components.py

This module provides reusable UI components that ensure a consistent look and feel
across the entire application. Components include sidebar, navigation buttons, 
cards, tables, and forms.
"""

from PyQt5.QtWidgets import (
    QWidget, QFrame, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, 
    QScrollArea, QSizePolicy, QSpacerItem, QGraphicsDropShadowEffect, 
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox,
    QFormLayout, QGroupBox, QCheckBox, QRadioButton
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QPoint
from PyQt5.QtGui import QIcon, QFont, QPixmap, QColor, QPainter, QPen, QBrush

# Use absolute import for ThemeManager
from app.utils.theme_manager import ThemeManager

class NavButton(QPushButton):
    """Navigation button for the sidebar"""
    
    def __init__(self, text, icon=None, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setFlat(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(40)
        
        if icon:
            if isinstance(icon, str):
                self.setIcon(QIcon(icon))
            else:
                self.setIcon(icon)
            self.setIconSize(QSize(20, 20))
        
        # Apply light theme styling
        self.setStyleSheet(f"""
            QPushButton {{
                color: {ThemeManager.get_color('text_primary')};
                border: none;
                text-align: left;
                padding: 8px 16px;
                font-size: 14px;
                border-radius: {ThemeManager.BORDER_RADIUS['small']}px;
                margin: 2px 0px;
                background-color: transparent;
            }}
            
            QPushButton:hover {{
                background-color: {ThemeManager.get_color('hover')};
            }}
            
            QPushButton:checked {{
                background-color: {ThemeManager.get_color('primary')};
                color: white;
                font-weight: bold;
            }}
        """)

class Sidebar(QFrame):
    """Sidebar navigation component"""
    
    page_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setMaximumWidth(250)
        self.setMinimumWidth(250)
        
        # Apply sidebar background color
        self.setStyleSheet(f"""
            QFrame#sidebar {{
                background-color: {ThemeManager.get_color('sidebar')};
                border-right: 1px solid {ThemeManager.get_color('border')};
            }}
        """)
        
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 20, 15, 20)
        self.layout.setSpacing(5)
        
        # Logo/branding
        self.logo_layout = QHBoxLayout()
        self.logo_label = QLabel("Smart Shop")
        self.logo_label.setFont(QFont(ThemeManager.FONTS["family"], ThemeManager.FONTS["size_xlarge"], QFont.Bold))
        self.logo_label.setStyleSheet(f"color: {ThemeManager.get_color('text_primary')};")
        self.logo_layout.addWidget(self.logo_label)
        self.layout.addLayout(self.logo_layout)
        
        # Separator
        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.HLine)
        self.separator.setFrameShadow(QFrame.Sunken)
        self.separator.setStyleSheet(f"background-color: {ThemeManager.get_color('border')};")
        self.layout.addWidget(self.separator)
        self.layout.addSpacing(20)
        
        # Navigation container
        self.nav_container = QWidget()
        self.nav_container.setObjectName("nav-container")
        self.nav_layout = QVBoxLayout(self.nav_container)
        self.nav_layout.setContentsMargins(0, 0, 0, 0)
        self.nav_layout.setSpacing(8)
        
        # Navigation buttons (populated in setup_navigation)
        self.nav_buttons = {}
        
        self.layout.addWidget(self.nav_container)
        self.layout.addStretch()
        
        # Settings/profile area at bottom
        self.bottom_container = QWidget()
        self.bottom_layout = QVBoxLayout(self.bottom_container)
        self.bottom_layout.setContentsMargins(0, 0, 0, 0)
        self.bottom_layout.setSpacing(5)
        
        # Settings button
        self.settings_button = NavButton("Settings", "app/assets/icons/settings.png")
        self.bottom_layout.addWidget(self.settings_button)
        
        # Profile info
        self.profile_widget = QWidget()
        self.profile_layout = QHBoxLayout(self.profile_widget)
        self.profile_layout.setContentsMargins(10, 10, 10, 10)
        
        self.profile_icon = QLabel()
        self.profile_icon.setFixedSize(32, 32)
        self.profile_icon.setStyleSheet(f"""
            background-color: {ThemeManager.get_color('primary')};
            border-radius: 16px;
            color: white;
            font-weight: bold;
        """)
        self.profile_icon.setAlignment(Qt.AlignCenter)
        
        self.profile_info = QLabel("Admin User")
        self.profile_info.setStyleSheet(f"color: {ThemeManager.get_color('text_primary')};")
        
        self.profile_layout.addWidget(self.profile_icon)
        self.profile_layout.addWidget(self.profile_info)
        
        self.bottom_layout.addWidget(self.profile_widget)
        self.layout.addWidget(self.bottom_container)
    
    def setup_navigation(self, pages):
        """
        Set up navigation buttons
        
        Args:
            pages (dict): Dictionary with page IDs as keys and page info (title, icon) as values
        """
        # Clear existing buttons
        for button in self.nav_buttons.values():
            self.nav_layout.removeWidget(button)
            button.deleteLater()
        self.nav_buttons = {}
        
        # Add new buttons
        for page_id, page_info in pages.items():
            title = page_info.get("title", page_id.capitalize())
            icon = page_info.get("icon", None)
            
            button = NavButton(title, icon)
            button.clicked.connect(lambda checked, pid=page_id: self.page_changed.emit(pid))
            self.nav_buttons[page_id] = button
            self.nav_layout.addWidget(button)
        
        # Select the first page by default
        if pages:
            first_page = next(iter(pages))
            self.select_page(first_page)
    
    def select_page(self, page_id):
        """Select a page in the navigation"""
        for pid, button in self.nav_buttons.items():
            button.setChecked(pid == page_id)

class PageHeader(QWidget):
    """Header for each page with title and actions"""
    
    def __init__(self, title, subtitle=None, parent=None):
        super().__init__(parent)
        
        # Set responsive size policy
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 24)  # Increased bottom margin
        layout.setSpacing(8)  # Added spacing
        
        # Title row with actions
        title_row = QHBoxLayout()
        title_row.setSpacing(20)  # Add spacing between title and actions
        
        # Title
        self.title_label = QLabel(title)
        self.title_label.setObjectName("page-title")
        self.title_label.setFont(QFont(ThemeManager.FONTS["family"], ThemeManager.FONTS["size_xxlarge"], QFont.Bold))
        self.title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        title_row.addWidget(self.title_label)
        
        # Actions container (right-aligned)
        self.actions_container = QWidget()
        self.actions_container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.actions_layout = QHBoxLayout(self.actions_container)
        self.actions_layout.setContentsMargins(0, 0, 0, 0)
        self.actions_layout.setSpacing(12)  # Increased spacing between buttons
        title_row.addWidget(self.actions_container)
        
        layout.addLayout(title_row)
        
        # Subtitle
        if subtitle:
            self.subtitle_label = QLabel(subtitle)
            self.subtitle_label.setObjectName("page-subtitle")
            self.subtitle_label.setFont(QFont(ThemeManager.FONTS["family"], ThemeManager.FONTS["size_large"]))
            self.subtitle_label.setStyleSheet(f"color: {ThemeManager.get_color('text_secondary')}; margin-top: 4px;")
            self.subtitle_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            layout.addWidget(self.subtitle_label)
    
    def add_action(self, widget):
        """Add an action button to the header"""
        self.actions_layout.addWidget(widget)

class Card(QFrame):
    """
    Modern card component with consistent styling
    Enhanced version of the existing CardWidget with theme integration
    """
    
    def __init__(self, title=None, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        
        # Set responsive size policy
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumHeight(150)  # Increased minimum height
        
        # Apply styling
        self.setStyleSheet(f"""
            QFrame#card {{
                background-color: #f8f9fa;
                border-radius: {ThemeManager.BORDER_RADIUS['normal']}px;
                border: 1px solid {ThemeManager.get_color('border')};
            }}
            
            /* Ensure all child elements have transparent backgrounds */
            QFrame#card > * {{
                background-color: transparent;
            }}
            
            QFrame#card QLabel {{
                background-color: transparent;
                color: #333333;
            }}
            
            QFrame#card QWidget {{
                background-color: transparent;
            }}
            
            QFrame#card:hover {{
                border: 1px solid {ThemeManager.get_color('primary')};
            }}
        """)
        
        # Add a softer drop shadow effect for light theme
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(8)  # Increased blur
        shadow.setColor(QColor(0, 0, 0, 20))  # Adjusted shadow
        shadow.setOffset(0, 3)   # Increased offset
        self.setGraphicsEffect(shadow)
        
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)  # Consistent padding
        self.layout.setSpacing(12)  # Increased spacing
        
        # Card title (optional)
        if title:
            self.title_label = QLabel(title)
            self.title_label.setObjectName("card-title")
            self.title_label.setFont(QFont(ThemeManager.FONTS["family"], ThemeManager.FONTS["size_large"], QFont.Bold))
            self.title_label.setStyleSheet("background-color: transparent; color: #333333;")
            self.layout.addWidget(self.title_label)
            self.layout.addSpacing(12)  # Increased spacing after title

class Button(QPushButton):
    """Enhanced button with theme integration and variants"""
    
    def __init__(self, text, icon=None, variant="primary", parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(36)
        
        # Set responsive size policy
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        
        # Set font
        font = QFont(ThemeManager.FONTS["family"], ThemeManager.FONTS["size_normal"])
        font.setBold(True)
        self.setFont(font)
        
        # Set icon if provided
        if icon:
            if isinstance(icon, str):
                self.setIcon(QIcon(icon))
            else:
                self.setIcon(icon)
            self.setIconSize(QSize(18, 18))
        
        # Apply action-based styling if text matches common actions
        if text.lower() == 'add' or text.lower().startswith('add '):
            variant = "primary"
        elif text.lower() == 'edit' or text.lower().startswith('edit '):
            variant = "primary"
        elif text.lower() == 'delete' or text.lower().startswith('delete '):
            variant = "danger"
        elif text.lower() == 'view' or text.lower().startswith('view '):
            variant = "primary"
        
        # Apply variant styling
        self.set_variant(variant)
    
    def set_variant(self, variant):
        """Set the button variant (primary, secondary, success, warning, danger)"""
        if variant not in ["primary", "secondary", "success", "warning", "danger"]:
            variant = "primary"
        
        # Get colors based on variant
        if variant == "primary":
            bg_color = "#3B82F6"  # Bright blue as in sales dashboard
            hover_color = "#2563EB"
        elif variant == "secondary":
            bg_color = "#6B7280"  # Gray color for secondary actions
            hover_color = "#4B5563"
        elif variant == "success": 
            bg_color = "#10B981"
            hover_color = "#059669"
        elif variant == "warning":
            bg_color = "#F59E0B"
            hover_color = "#D97706"
        elif variant == "danger":
            bg_color = "#EF4444"  # Red color for delete actions
            hover_color = "#DC2626"
        
        # Apply custom stylesheet for the button
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                color: white;
                padding: 8px 16px;
                border-radius: {ThemeManager.BORDER_RADIUS['small']}px;
                font-weight: bold;
                border: none;
                text-align: center;
                min-width: 90px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {bg_color};
                padding-top: 9px;
                padding-left: 17px;
            }}
            QPushButton:disabled {{
                background-color: #D1D5DB;
                color: #6B7280;
            }}
        """)
        
        # Apply class for the stylesheet to pick up
        self.setProperty("class", variant)
        self.style().unpolish(self)
        self.style().polish(self)

class ComboBox(QComboBox):
    """Enhanced combobox with improved visibility for dropdown items"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMinimumHeight(36)
        
        # Force style with direct color values for maximum compatibility
        self.setStyleSheet("""
            QComboBox {
                padding: 5px 35px 5px 10px;
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                background-color: #FFFFFF;
                color: #000000;
                min-height: 36px;
            }
            
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 25px;
                border-left: 1px solid #D1D5DB;
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
                background: #FFFFFF;
            }
            
            QComboBox::down-arrow {
                width: 0px;
                height: 0px;
                image: none;
            }
        """)
        
        # Set view mode to be more compatible across platforms
        self.setView(self.createStandardView())
        
        # Fix popup appearance on Windows
        self.setMaxVisibleItems(10)
        self.view().window().setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.view().window().setAttribute(Qt.WA_TranslucentBackground)
    
    def createStandardView(self):
        """Create a standard list view with appropriate styling"""
        from PyQt5.QtWidgets import QListView
        view = QListView()
        view.setStyleSheet("""
            QListView {
                background-color: #FFFFFF;
                border: 1px solid #D1D5DB;
                color: #000000;
                outline: none;
                padding: 5px 0px;
            }
            
            QListView::item {
                background-color: #FFFFFF;
                color: #000000;
                min-height: 30px;
                padding: 5px 10px;
                border-bottom: 1px solid #F0F0F0;
            }
            
            QListView::item:selected {
                background-color: #3B82F6;
                color: #FFFFFF;
            }
            
            QListView::item:hover:!selected {
                background-color: #F3F4F6;
            }
        """)
        return view
    
    def paintEvent(self, event):
        """Custom paint event to draw a better dropdown arrow"""
        super().paintEvent(event)
        
        # Draw a custom dropdown arrow that will be visible
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Set the arrow color
        painter.setPen(QPen(QColor("#000000")))
        painter.setBrush(QBrush(QColor("#000000")))
        
        # Arrow size and position
        width = 10
        height = 6
        x = self.width() - width - 15
        y = (self.height() - height) // 2
        
        # Draw the arrow pointing down
        points = [
            QPoint(x, y),
            QPoint(x + width, y),
            QPoint(x + width // 2, y + height)
        ]
        painter.drawPolygon(points)

class TableComponent(QTableWidget):
    """Enhanced table with consistent styling and features"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Styling
        self.setShowGrid(True)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
        
        # Set responsive size policy
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumHeight(200)  # Ensure table has adequate height
        
        # Improve cell alignment and display
        self.setTextElideMode(Qt.ElideRight)
        self.setWordWrap(False)
        
        # Set font
        self.setFont(QFont(ThemeManager.FONTS["family"], ThemeManager.FONTS["size_normal"]))
        
        # Configure header
        header_font = QFont(ThemeManager.FONTS["family"], ThemeManager.FONTS["size_normal"])
        header_font.setBold(True)
        self.horizontalHeader().setFont(header_font)
        self.horizontalHeader().setMinimumHeight(40)  # Taller header for better clickability
        self.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        # We're using inline stylesheet to avoid inheritance issues when used within cards
        self.setStyleSheet(f"""
            QTableWidget {{
                background-color: {ThemeManager.get_color('card')};
                alternate-background-color: {ThemeManager.get_color('hover')};
                gridline-color: {ThemeManager.get_color('border')};
                border-radius: {ThemeManager.BORDER_RADIUS['small']}px;
                border: 1px solid {ThemeManager.get_color('border')};
                selection-background-color: {ThemeManager.get_color('primary')};
                selection-color: white;
                font-size: {ThemeManager.FONTS['size_normal']}px;
            }}
            
            QTableWidget::item {{
                border-bottom: 1px solid {ThemeManager.get_color('border')};
                padding: 8px;
                min-height: 36px;  /* Increased row height */
            }}
            
            QTableWidget::item:selected {{
                background-color: {ThemeManager.get_color('primary')};
                color: white;
            }}
            
            QHeaderView::section {{
                background-color: {ThemeManager.get_color('background')};
                padding: 10px 8px;  /* Increased padding */
                border: 1px solid {ThemeManager.get_color('border')};
                font-weight: bold;
                min-height: 20px;
                font-size: {ThemeManager.FONTS['size_normal']}px;
            }}
            
            QHeaderView::section:hover {{
                background-color: {ThemeManager.get_color('hover')};
            }}
            
            /* Fix for cell editing */
            QTableWidget QLineEdit {{
                background-color: white;
                color: black;
                border: 2px solid {ThemeManager.get_color('primary')};
                padding: 4px 8px;
                margin: 0px;
                selection-background-color: {ThemeManager.get_color('primary')};
                selection-color: white;
                font-family: "{ThemeManager.FONTS['family']}";
                font-size: {ThemeManager.FONTS['size_normal']}px;
            }}
            
            /* Scrollbar styling */
            QScrollBar:vertical {{
                background: {ThemeManager.get_color('background')};
                width: 14px;  /* Wider scrollbar */
                margin: 0px;
            }}
            
            QScrollBar::handle:vertical {{
                background: {ThemeManager.get_color('border')};
                min-height: 30px;
                border-radius: 7px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background: {ThemeManager.get_color('text_secondary')};
            }}
        """)
    
    def setup_columns(self, columns):
        """
        Set up table columns
        
        Args:
            columns (list): List of column names
        """
        self.setColumnCount(len(columns))
        self.setHorizontalHeaderLabels(columns)
        
        # Auto-adjust column widths based on content
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Set minimum section size
        self.horizontalHeader().setMinimumSectionSize(100)
    
    def add_row(self, data):
        """
        Add a row to the table
        
        Args:
            data (list): List of cell values
        """
        row_position = self.rowCount()
        self.insertRow(row_position)
        
        for col, value in enumerate(data):
            item = QTableWidgetItem(str(value))
            # Set font
            item.setFont(QFont(ThemeManager.FONTS["family"], ThemeManager.FONTS["size_normal"]))
            # Set alignment based on data type
            if isinstance(value, (int, float)):
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            else:
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.setItem(row_position, col, item)
        
        # Set row height
        self.setRowHeight(row_position, 36)  # Consistent row height

class Form(QWidget):
    """A standardized form with consistent styling"""
    
    def __init__(self, title=None, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: transparent;")
        
        # Set responsive size policy
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(16)  # Increased spacing
        
        # Title (optional)
        if title:
            self.title = QLabel(title)
            self.title.setFont(QFont(ThemeManager.FONTS["family"], ThemeManager.FONTS["size_large"], QFont.Bold))
            self.title.setStyleSheet("background-color: transparent; color: #333333;")
            self.layout.addWidget(self.title)
            self.layout.addSpacing(12)  # Increased spacing after title
        
        # Form layout
        self.form_widget = QWidget()
        self.form_widget.setStyleSheet("background-color: transparent;")
        self.form_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        self.form_layout = QFormLayout(self.form_widget)
        self.form_layout.setContentsMargins(0, 0, 0, 0)
        self.form_layout.setSpacing(20)  # Increased spacing between fields
        self.form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)  # Allow fields to grow horizontally
        self.form_layout.setRowWrapPolicy(QFormLayout.WrapLongRows)  # Wrap to new line on small screens
        self.form_layout.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # Left align labels
        
        self.layout.addWidget(self.form_widget)
        
        # Fields dictionary to keep track of form fields
        self.fields = {}
    
    def add_field(self, field_id, label, widget_type="text", options=None, default=None):
        """
        Add a field to the form
        
        Args:
            field_id (str): Unique identifier for the field
            label (str): Display label
            widget_type (str): Type of widget (text, number, decimal, select, checkbox)
            options (list): Options for select widget
            default: Default value for the field
        
        Returns:
            FormField: The created form field
        """
        # Create the appropriate widget
        if widget_type == "text":
            widget = QLineEdit()
            widget.setMinimumHeight(36)  # Standard input height
            widget.setFont(QFont(ThemeManager.FONTS["family"], ThemeManager.FONTS["size_normal"]))
            if default:
                widget.setText(str(default))
        elif widget_type == "number":
            widget = QSpinBox()
            widget.setMinimumHeight(36)  # Standard input height
            widget.setFont(QFont(ThemeManager.FONTS["family"], ThemeManager.FONTS["size_normal"]))
            widget.setMinimum(0)
            widget.setMaximum(9999)
            widget.setButtonSymbols(QSpinBox.UpDownArrows)  # Use arrows instead of +/- buttons
            if default is not None:
                widget.setValue(int(default))
        elif widget_type == "decimal":
            widget = QDoubleSpinBox()
            widget.setMinimumHeight(36)  # Standard input height
            widget.setFont(QFont(ThemeManager.FONTS["family"], ThemeManager.FONTS["size_normal"]))
            widget.setMinimum(0)
            widget.setMaximum(9999.99)
            widget.setDecimals(2)
            widget.setButtonSymbols(QDoubleSpinBox.UpDownArrows)
            if default is not None:
                widget.setValue(float(default))
        elif widget_type == "select":
            widget = QComboBox()
            widget.setMinimumHeight(36)  # Standard input height
            widget.setFont(QFont(ThemeManager.FONTS["family"], ThemeManager.FONTS["size_normal"]))
            # Apply combo box styling to ensure dropdown is visible
            widget.setStyleSheet(f"""
                QComboBox {{
                    padding: 8px 12px;
                    border: 1px solid {ThemeManager.get_color('border')};
                    border-radius: {ThemeManager.BORDER_RADIUS['small']}px;
                    background-color: {ThemeManager.get_color('card')};
                    color: {ThemeManager.get_color('text_primary')};
                    min-height: 36px;
                }}
                
                QComboBox::drop-down {{
                    subcontrol-origin: padding;
                    subcontrol-position: top right;
                    width: 30px;
                    border-left: 1px solid {ThemeManager.get_color('border')};
                }}
                
                QComboBox QAbstractItemView {{
                    background-color: {ThemeManager.get_color('card')};
                    border: 1px solid {ThemeManager.get_color('border')};
                    selection-background-color: {ThemeManager.get_color('primary')};
                    selection-color: white;
                    color: {ThemeManager.get_color('text_primary')};
                }}
                
                QComboBox QAbstractItemView::item {{
                    padding: 8px 12px;
                    min-height: 36px;
                }}
                
                QComboBox QAbstractItemView::item:selected {{
                    background-color: {ThemeManager.get_color('primary')};
                }}
            """)
            if options:
                widget.addItems(options)
            if default:
                index = widget.findText(str(default))
                if index >= 0:
                    widget.setCurrentIndex(index)
        elif widget_type == "checkbox":
            widget = QCheckBox()
            widget.setFont(QFont(ThemeManager.FONTS["family"], ThemeManager.FONTS["size_normal"]))
            widget.setMinimumHeight(24)  # Ensure good touch target
            widget.setStyleSheet(f"""
                QCheckBox {{
                    spacing: 10px;
                }}
                QCheckBox::indicator {{
                    width: 20px;
                    height: 20px;
                    border-radius: 4px;
                }}
            """)
            if default:
                widget.setChecked(bool(default))
        else:
            widget = QLineEdit()
            widget.setMinimumHeight(40)
        
        # Create form field
        field = FormField(label, widget)
        self.fields[field_id] = field
        
        # Add to layout
        self.form_layout.addRow(field)
        
        return field
    
    def get_values(self):
        """Get all form values as a dictionary"""
        values = {}
        for field_id, field in self.fields.items():
            values[field_id] = field.get_value()
        return values
    
    def set_values(self, values):
        """Set form values from a dictionary"""
        for field_id, value in values.items():
            if field_id in self.fields:
                self.fields[field_id].set_value(value)

class FormField(QWidget):
    """A standardized form field with label and input"""
    
    def __init__(self, label, widget, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: transparent;")
        
        # Set responsive size policy
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 8)  # Adjusted bottom margin
        self.layout.setSpacing(8)  # Increased spacing between label and input
        
        # Label
        self.label = QLabel(label)
        self.label.setFont(QFont(ThemeManager.FONTS["family"], ThemeManager.FONTS["size_normal"], QFont.Bold))
        self.label.setStyleSheet("background-color: transparent; color: #333333;")
        self.layout.addWidget(self.label)
        
        # Input widget
        self.widget = widget
        self.widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.layout.addWidget(self.widget)
    
    def get_value(self):
        """Get the current value of the form field"""
        if isinstance(self.widget, QLineEdit):
            return self.widget.text()
        elif isinstance(self.widget, QComboBox):
            return self.widget.currentText()
        elif isinstance(self.widget, (QSpinBox, QDoubleSpinBox)):
            return self.widget.value()
        elif isinstance(self.widget, QCheckBox):
            return self.widget.isChecked()
        else:
            return None
    
    def set_value(self, value):
        """Set the value of the form field"""
        if isinstance(self.widget, QLineEdit):
            self.widget.setText(str(value))
        elif isinstance(self.widget, QComboBox):
            index = self.widget.findText(str(value))
            if index >= 0:
                self.widget.setCurrentIndex(index)
        elif isinstance(self.widget, (QSpinBox, QDoubleSpinBox)):
            try:
                self.widget.setValue(float(value))
            except (ValueError, TypeError):
                pass
        elif isinstance(self.widget, QCheckBox):
            self.widget.setChecked(bool(value))

class Searchbar(QWidget):
    """A search input with icon"""
    
    search_triggered = pyqtSignal(str)
    
    def __init__(self, placeholder="Search...", parent=None):
        super().__init__(parent)
        
        # Set responsive size policy
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)  # No spacing for attached look
        
        # Create container for search with border radius
        container = QFrame()
        container.setObjectName("searchContainer")
        container.setStyleSheet(f"""
            #searchContainer {{
                background-color: {ThemeManager.get_color('card')};
                border: 1px solid {ThemeManager.get_color('border')};
                border-radius: {ThemeManager.BORDER_RADIUS['small']}px;
            }}
        """)
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(12, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # Search icon
        search_icon = QLabel()
        search_icon.setPixmap(QIcon("app/assets/icons/search.png").pixmap(QSize(18, 18)))
        search_icon.setFixedSize(24, 24)
        search_icon.setStyleSheet("background: transparent;")
        container_layout.addWidget(search_icon)
        container_layout.addSpacing(8)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(placeholder)
        self.search_input.setMinimumWidth(250)
        self.search_input.setMinimumHeight(36)  # Standard height
        self.search_input.setFont(QFont(ThemeManager.FONTS["family"], ThemeManager.FONTS["size_normal"]))
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: none;
                background-color: transparent;
                padding: 8px 12px 8px 0px;
            }
            QLineEdit:focus {
                border: none;
            }
        """)
        self.search_input.returnPressed.connect(self.on_search)
        container_layout.addWidget(self.search_input)
        
        # Search button
        self.search_button = QPushButton("Search")
        self.search_button.setCursor(Qt.PointingHandCursor)
        self.search_button.setMinimumHeight(36)  # Standard height
        self.search_button.setFont(QFont(ThemeManager.FONTS["family"], ThemeManager.FONTS["size_normal"]))
        self.search_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {ThemeManager.get_color('primary')};
                color: white;
                border: none;
                border-top-right-radius: {ThemeManager.BORDER_RADIUS['small'] - 1}px;
                border-bottom-right-radius: {ThemeManager.BORDER_RADIUS['small'] - 1}px;
                border-top-left-radius: 0px;
                border-bottom-left-radius: 0px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {ThemeManager.get_color('primary_dark')};
            }}
        """)
        self.search_button.clicked.connect(self.on_search)
        container_layout.addWidget(self.search_button)
        
        layout.addWidget(container)
    
    def on_search(self):
        """Emit search signal with current text"""
        self.search_triggered.emit(self.search_input.text())
    
    def text(self):
        """Get the current search text"""
        return self.search_input.text()
    
    def set_text(self, text):
        """Set the search text"""
        self.search_input.setText(text) 