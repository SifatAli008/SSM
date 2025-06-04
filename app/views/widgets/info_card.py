from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette

class InfoCard(QFrame):
    clicked = pyqtSignal()

    def __init__(self, title, value, subtitle=None, icon=None, color="#3498db", clickable=True):
        super().__init__()
        self._clickable = clickable
        self._hover = False
        self._pressed = False

        self.setObjectName("infoCard")
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setMinimumSize(200, 120)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setStyleSheet(self.default_stylesheet(color))

        if clickable:
            self.setCursor(Qt.PointingHandCursor)

        if color:
            palette = self.palette()
            palette.setColor(QPalette.Window, QColor(color))
            self.setAutoFillBackground(True)
            self.setPalette(palette)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(8)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(8)

        # Title Row
        title_layout = QHBoxLayout()
        title_layout.setSpacing(8)
        if icon:
            icon_label = QLabel()
            if isinstance(icon, str) and len(icon) == 1:
                icon_label.setText(icon)
                icon_label.setFont(QFont("Segoe UI Emoji", 18))
            elif isinstance(icon, str):
                icon_label.setPixmap(QIcon(icon).pixmap(QSize(20, 20)))
                icon_label.setFixedSize(20, 20)
            else:
                icon_label.setText("")
            title_layout.addWidget(icon_label)

        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        self.layout.addLayout(title_layout)

        # Value
        self.value_label = QLabel(str(value))
        self.value_label.setObjectName("cardValue")
        self.value_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        self.value_label.setStyleSheet(f"color: {color};")
        self.layout.addWidget(self.value_label)

        # Subtitle
        self.subtitle_label = QLabel(subtitle or "")
        self.subtitle_label.setObjectName("cardSubtitle")
        self.subtitle_label.setFont(QFont("Segoe UI", 13))
        self.subtitle_label.setStyleSheet("color: #7f8c8d; background-color: transparent;")
        self.layout.addWidget(self.subtitle_label)

        self.layout.addStretch()

    def default_stylesheet(self, color):
        return f"""
        QFrame#infoCard {{
            background-color: #ffffff;
            border-radius: 12px;
            border: 1px solid #e0e0e0;
        }}
        QFrame#infoCard:hover {{
            border: 1px solid {color};
        }}
        QLabel#cardTitle {{
            color: #2c3e50;
            background-color: transparent;
        }}
        QLabel#cardValue {{
            background-color: transparent;
        }}
        QLabel#cardSubtitle {{
            color: #7f8c8d;
            background-color: transparent;
        }}
        """

    def update_values(self, value=None, subtitle=None, color=None):
        """
        Update the value, subtitle, and optionally the color of the InfoCard.
        """
        if value is not None:
            self.value_label.setText(str(value))
        if subtitle is not None:
            self.subtitle_label.setText(str(subtitle))
        if color is not None:
            self.value_label.setStyleSheet(f"color: {color};") 