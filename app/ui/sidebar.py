from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSizePolicy
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, pyqtSignal

class Sidebar(QWidget):
    page_changed = pyqtSignal(str)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(220)
        self.setStyleSheet('''
            background-color: #23272f;
            color: #fff;
            border-right: 1px solid #222;
        ''')
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        self.buttons = {}
        self.selected_key = None
        pages = [
            ("Dashboard", "dashboard", "🏠"),
            ("Inventory", "inventory", "📦"),
            ("Sales", "sales", "💰"),
            ("Customers", "customers", "👥"),
            ("Reports", "reports", "📊"),
            ("Settings", "settings", "⚙️"),
        ]
        for label, key, icon in pages:
            btn = QPushButton(f"{icon}  {label}")
            btn.setObjectName(key)
            btn.setStyleSheet('''
                QPushButton {
                    background: none;
                    color: #fff;
                    border: none;
                    text-align: left;
                    padding: 12px 24px;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background: #2c313c;
                }
                QPushButton[selected="true"] {
                    background: #1a1d23;
                    font-weight: bold;
                }
            ''')
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.clicked.connect(lambda checked, k=key: self.on_nav_clicked(k))
            layout.addWidget(btn)
            self.buttons[key] = btn
        layout.addStretch(1)

    def on_nav_clicked(self, key):
        self.select_page(key)
        self.page_changed.emit(key)

    def select_page(self, key):
        for k, btn in self.buttons.items():
            btn.setProperty("selected", k == key)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self.selected_key = key 