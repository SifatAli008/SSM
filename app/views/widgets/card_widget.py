"""
Smart Shop Manager - Dashboard Widgets
File: views/widgets/card_widget.py
"""


from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy, QGraphicsDropShadowEffect
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
            
        # Add drop shadow effect instead of CSS box-shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(8)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)


        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)


        # Title Row
        title_layout = QHBoxLayout()
        title_layout.setSpacing(8)


        if icon:
            icon_label = QLabel()
            if isinstance(icon, str) and len(icon) == 1:
                # Emoji icon
                icon_label.setText(icon)
                icon_label.setFont(QFont("Segoe UI Emoji", 18))
            elif isinstance(icon, str):
                # Try to load as QIcon path
                icon_label.setPixmap(QIcon(icon).pixmap(QSize(20, 20)))
                icon_label.setFixedSize(20, 20)
            else:
                icon_label.setText("")
            title_layout.addWidget(icon_label)


        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")
        title_label.setFont(QFont("Segoe UI", 13, QFont.Bold))
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        layout.addLayout(title_layout)


        # Value
        value_label = QLabel(str(value))
        value_label.setObjectName("cardValue")
        value_label.setFont(QFont("Segoe UI", 22, QFont.Bold))
        value_label.setStyleSheet("color: #3498db;")
        layout.addWidget(value_label)


        # Subtitle
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setObjectName("cardSubtitle")
            subtitle_label.setFont(QFont("Segoe UI", 11))
            subtitle_label.setStyleSheet("color: #7f8c8d;")
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
        }


        QLabel#cardTitle {
            color: #2c3e50;
        }


        QLabel#cardValue {
            color: #3498db;
        }


        QLabel#cardSubtitle {
            color: #7f8c8d;
        }
        """