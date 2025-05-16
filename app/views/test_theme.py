import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QCheckBox,
    QFrame, QTabWidget, QComboBox, QTableWidget,
    QTableWidgetItem, QSpinBox, QTextEdit, QGridLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from app.utils.theme_manager import ThemeManager, ThemeType
from app.views.widgets.components import Button, Card

class ThemeTestWindow(QWidget):
    def __init__(self):
        super().__init__()
        # Apply light theme explicitly
        ThemeManager.apply_theme(ThemeType.LIGHT)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Light Theme Test')
        self.setMinimumSize(800, 700)
        
        # Main layout
        main_layout = QHBoxLayout(self)
        
        # Sidebar
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(250)
        sidebar_layout = QVBoxLayout(sidebar)
        
        # Sidebar title
        sidebar_title = QLabel("Smart Shop Manager")
        sidebar_title.setFont(QFont(ThemeManager.FONTS["family"], 16, QFont.Bold))
        sidebar_title.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(sidebar_title)
        
        # Add some space
        sidebar_layout.addSpacing(20)
        
        # Navigation container
        nav_container = QWidget()
        nav_container.setObjectName("nav-container")
        nav_layout = QVBoxLayout(nav_container)
        
        # Navigation buttons
        nav_buttons = [
            "Dashboard", "Inventory", "Sales", "Customers", 
            "Reports", "Settings", "Help"
        ]
        
        for text in nav_buttons:
            btn = QPushButton(text)
            btn.setCheckable(True)
            nav_layout.addWidget(btn)
        
        # Set first button as checked
        nav_layout.itemAt(0).widget().setChecked(True)
        
        sidebar_layout.addWidget(nav_container)
        sidebar_layout.addStretch()
        
        # Main content
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Page title
        title = QLabel("Light Theme Demo")
        title.setObjectName("title")
        title.setFont(QFont(ThemeManager.FONTS["family"], 22, QFont.Bold))
        content_layout.addWidget(title)
        
        subtitle = QLabel("Test the new light theme components")
        subtitle.setObjectName("subtitle")
        subtitle.setStyleSheet(f"color: {ThemeManager.get_color('text_secondary')};")
        content_layout.addWidget(subtitle)
        
        content_layout.addSpacing(20)
        
        # Create a card for basic inputs
        inputs_card = Card("Basic UI Components")
        inputs_layout = QGridLayout()
        
        # Text input
        inputs_layout.addWidget(QLabel("Text Input:"), 0, 0)
        text_input = QLineEdit()
        text_input.setPlaceholderText("Enter some text")
        inputs_layout.addWidget(text_input, 0, 1)
        
        # Combo box
        inputs_layout.addWidget(QLabel("Dropdown:"), 1, 0)
        combo = QComboBox()
        combo.addItems(["Option 1", "Option 2", "Option 3"])
        combo.setStyleSheet(f"""
            QComboBox {{
                padding: 8px;
                border: 1px solid {ThemeManager.get_color('border')};
                border-radius: {ThemeManager.BORDER_RADIUS['small']}px;
                background-color: {ThemeManager.get_color('card')};
                color: {ThemeManager.get_color('text_primary')};
            }}
            
            QComboBox QAbstractItemView {{
                background-color: {ThemeManager.get_color('card')};
                border: 1px solid {ThemeManager.get_color('border')};
                selection-background-color: {ThemeManager.get_color('primary')};
                selection-color: white;
                color: {ThemeManager.get_color('text_primary')};
            }}
            
            QComboBox QAbstractItemView::item {{
                padding: 6px;
                min-height: 24px;
            }}
        """)
        inputs_layout.addWidget(combo, 1, 1)
        
        # Spin box
        inputs_layout.addWidget(QLabel("Spin Box:"), 2, 0)
        spin = QSpinBox()
        inputs_layout.addWidget(spin, 2, 1)
        
        # Checkbox
        inputs_layout.addWidget(QLabel("Checkbox:"), 3, 0)
        check = QCheckBox("Enable feature")
        inputs_layout.addWidget(check, 3, 1)
        
        # Add to card
        inputs_card.layout.addLayout(inputs_layout)
        content_layout.addWidget(inputs_card)
        
        # Buttons card
        buttons_card = Card("Button Styles")
        buttons_layout = QHBoxLayout()
        
        # Primary button
        primary_btn = Button("Primary", variant="primary")
        buttons_layout.addWidget(primary_btn)
        
        # Secondary button
        secondary_btn = QPushButton("Secondary")
        secondary_btn.setProperty("class", "secondary")
        secondary_btn.setStyleSheet("""
            QPushButton {
                background-color: """ + ThemeManager.get_color("accent") + """;
                color: white;
            }
            QPushButton:hover {
                background-color: #7C3AED;
            }
        """)
        buttons_layout.addWidget(secondary_btn)
        
        # Success button
        success_btn = QPushButton("Success")
        success_btn.setProperty("class", "success")
        success_btn.setStyleSheet("""
            QPushButton {
                background-color: """ + ThemeManager.get_color("success") + """;
                color: white;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        buttons_layout.addWidget(success_btn)
        
        # Warning button
        warning_btn = QPushButton("Warning")
        warning_btn.setProperty("class", "warning")
        warning_btn.setStyleSheet("""
            QPushButton {
                background-color: """ + ThemeManager.get_color("warning") + """;
                color: white;
            }
            QPushButton:hover {
                background-color: #D97706;
            }
        """)
        buttons_layout.addWidget(warning_btn)
        
        # Danger button
        danger_btn = QPushButton("Danger")
        danger_btn.setProperty("class", "danger")
        danger_btn.setStyleSheet("""
            QPushButton {
                background-color: """ + ThemeManager.get_color("danger") + """;
                color: white;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
        """)
        buttons_layout.addWidget(danger_btn)
        
        buttons_card.layout.addLayout(buttons_layout)
        content_layout.addWidget(buttons_card)
        
        # Table card
        table_card = Card("Table Example")
        table_layout = QVBoxLayout()
        
        table = QTableWidget(5, 3)
        table.setHorizontalHeaderLabels(["ID", "Product", "Price"])
        
        # Add some sample data
        for row in range(5):
            table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            table.setItem(row, 1, QTableWidgetItem(f"Product {row + 1}"))
            table.setItem(row, 2, QTableWidgetItem(f"${(row + 1) * 10.99:.2f}"))
        
        table_layout.addWidget(table)
        table_card.layout.addLayout(table_layout)
        content_layout.addWidget(table_card)
        
        content_layout.addStretch()
        
        # Add everything to main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(content)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ThemeTestWindow()
    window.show()
    sys.exit(app.exec_()) 