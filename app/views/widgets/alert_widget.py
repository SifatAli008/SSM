from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon, QColor, QPalette, QFont




class AlertWidget(QFrame):
    def __init__(self, text, icon=None, color="#ffeaa7"):
        super().__init__()


        self.setObjectName("alert")
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        self.setMinimumHeight(30)
        self.setStyleSheet(self.default_stylesheet())


        # Set background color
        if color:
            palette = self.palette()
            palette.setColor(QPalette.Window, QColor(color))
            self.setAutoFillBackground(True)
            self.setPalette(palette)


        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 5, 12, 5)
        layout.setSpacing(8)


        # Optional icon
        if icon:
            icon_label = QLabel()
            icon_label.setPixmap(QIcon(icon).pixmap(QSize(16, 16)))
            icon_label.setFixedSize(18, 18)
            layout.addWidget(icon_label)


        # Alert text
        label = QLabel(text)
        label.setObjectName("alertText")
        label.setFont(QFont("Segoe UI", 9))
        label.setStyleSheet("color: #2d3436;")
        layout.addWidget(label)


        layout.addStretch()


    def default_stylesheet(self):
        return """
        QFrame#alert {
            border-radius: 8px;
            border: 1px solid #dfe6e9;
        }


        QLabel#alertText {
            color: #2d3436;
        }


        QFrame#alert:hover {
            border: 1px solid #74b9ff;
            background-color: #dfe6e9;
        }
        """



