from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon, QColor, QPalette

class AlertWidget(QFrame):
    def __init__(self, text, icon=None, color=None):
        super().__init__()
        self.setObjectName("alert")
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # Set background color (use QPalette.Window instead of deprecated Background)
        if color:
            palette = self.palette()
            palette.setColor(QPalette.Window, QColor(color))
            self.setAutoFillBackground(True)
            self.setPalette(palette)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

        if icon:
            iconLabel = QLabel()
            iconLabel.setPixmap(QIcon(icon).pixmap(QSize(16, 16)))
            layout.addWidget(iconLabel)

        label = QLabel(text)
        label.setObjectName("alertText")
        layout.addWidget(label)
