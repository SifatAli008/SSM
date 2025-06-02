from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QSizePolicy
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class Header(QWidget):
    def __init__(self, parent=None, user_name="Admin"):
        super().__init__(parent)
        self.setFixedHeight(60)
        self.setStyleSheet('''
            background-color: #fff;
            border-bottom: 1px solid #e0e0e0;
        ''')
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(10)
        title = QLabel("Smart Shop Manager")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #23272f;")
        layout.addWidget(title)
        layout.addStretch(1)
        user_label = QLabel(f"👤 {user_name}")
        user_label.setFont(QFont("Segoe UI", 14))
        layout.addWidget(user_label)
        self.settings_btn = QPushButton("⚙️")
        self.settings_btn.setFixedSize(36, 36)
        self.settings_btn.setStyleSheet('''
            QPushButton {
                background: #f5f6fa;
                border: none;
                border-radius: 18px;
                font-size: 18px;
            }
            QPushButton:hover {
                background: #e0e0e0;
            }
        ''')
        layout.addWidget(self.settings_btn)
        self.logout_btn = QPushButton("🚪")
        self.logout_btn.setFixedSize(36, 36)
        self.logout_btn.setStyleSheet('''
            QPushButton {
                background: #f5f6fa;
                border: none;
                border-radius: 18px;
                font-size: 18px;
            }
            QPushButton:hover {
                background: #e0e0e0;
            }
        ''')
        layout.addWidget(self.logout_btn) 