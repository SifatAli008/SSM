"""
Smart Shop Manager - Dashboard Widgets
File: views/widgets/card_widget.py
"""

from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette


class CardWidget(QFrame):
    def __init__(self, title, value, subtitle=None, icon=None, color=None):
        super().__init__()

        self.setObjectName("card")
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setMinimumSize(200, 120)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setStyleSheet(self.default_stylesheet())

        # Optional background color
        if color:
            palette = self.palette()
            palette.setColor(QPalette.Window, QColor(color))
            self.setAutoFillBackground(True)
            self.setPalette(palette)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)

        # Title Row
        title_layout = QHBoxLayout()
        title_layout.setSpacing(8)

        if icon:
            icon_label = QLabel()
            icon_label.setPixmap(QIcon(icon).pixmap(QSize(20, 20)))
            icon_label.setFixedSize(20, 20)
            title_layout.addWidget(icon_label)

        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")
        title_label.setFont(QFont("Arial", 10, QFont.Bold))
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        layout.addLayout(title_layout)

        # Value
        value_label = QLabel(str(value))
        value_label.setObjectName("cardValue")
        value_label.setFont(QFont("Arial", 20, QFont.Bold))
        layout.addWidget(value_label)

        # Subtitle
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setObjectName("cardSubtitle")
            subtitle_label.setFont(QFont("Arial", 9))
            subtitle_label.setStyleSheet("color: gray;")
            layout.addWidget(subtitle_label)

        layout.addStretch()

    def default_stylesheet(self):
        return """
        QFrame#card {
            background-color: #ffffff;
            border-radius: 12px;
            border: 1px solid #e0e0e0;
        }

        QFrame#card:hover {
            border: 1px solid #3498db;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        }

        QLabel#cardTitle {
            color: #2c3e50;
        }

        QLabel#cardValue {
            color: #2c3e50;
        }

        QLabel#cardSubtitle {
            color: #7f8c8d;
        }
        """
