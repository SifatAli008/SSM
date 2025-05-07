from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont


class ActionButton(QPushButton):
    def __init__(self, text, icon=None, color="#2ecc71", radius=8):
        super().__init__(text)
        self.setCursor(Qt.PointingHandCursor)


        # Set icon if provided
        if icon:
            self.setIcon(QIcon(icon))


        # Set base styles
        self.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.setFixedHeight(36)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: {radius}px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: #27ae60;
            }}
            QPushButton:pressed {{
                background-color: #1e8449;
            }}
        """)



