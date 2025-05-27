from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer

class Snackbar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.ToolTip)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedHeight(48)
        self.setStyleSheet("""
            background: #323232;
            color: white;
            border-radius: 8px;
            padding: 12px 24px;
            font-size: 15px;
        """)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(16, 0, 16, 0)
        self.label = QLabel()
        self.label.setStyleSheet("color: white;")
        self.layout.addWidget(self.label)
        self.action_btn = QPushButton()
        self.action_btn.setVisible(False)
        self.action_btn.setStyleSheet("background: transparent; color: #4FC3F7; font-weight: bold; border: none; margin-left: 16px;")
        self.layout.addWidget(self.action_btn)
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide)
        self.action_btn.clicked.connect(self.hide)

    def show_snackbar(self, message, duration=3000, action_text=None, action_callback=None):
        self.label.setText(message)
        if action_text and action_callback:
            self.action_btn.setText(action_text)
            self.action_btn.setVisible(True)
            self.action_btn.clicked.disconnect()
            self.action_btn.clicked.connect(lambda: (self.hide(), action_callback()))
        else:
            self.action_btn.setVisible(False)
        self.show()
        self.raise_()
        self.timer.start(duration)

    def hideEvent(self, event):
        self.action_btn.setVisible(False)
        super().hideEvent(event) 