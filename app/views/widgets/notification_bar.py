from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt, pyqtSignal


class NotificationBar(QFrame):
    clicked = pyqtSignal()  # ✅ Custom signal

    def __init__(self, text, icon_text="✔", bg_color="#2ecc71", text_color="white", radius=8):
        super().__init__()

        self.setObjectName("notificationBar")
        self.setFixedHeight(40)
        self.setCursor(Qt.PointingHandCursor)  # ✅ Optional: shows clickable cursor
        self.setStyleSheet(f"""
            QFrame#notificationBar {{
                background-color: {bg_color};
                border-radius: {radius}px;
                padding: 0 12px;
            }}
            QLabel {{
                color: {text_color};
                font: bold 10pt "Segoe UI";
            }}
            QLabel#iconLabel {{
                font-size: 14pt;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(8)

        if icon_text:
            icon_label = QLabel(icon_text)
            icon_label.setObjectName("iconLabel")
            icon_label.setFixedWidth(20)
            icon_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(icon_label)

        text_label = QLabel(text)
        layout.addWidget(text_label)
        layout.addStretch()

    def mousePressEvent(self, event):
        """Emit custom signal on click."""
        self.clicked.emit()
        super().mousePressEvent(event)
        