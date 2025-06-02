from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget
from app.ui.sidebar import Sidebar
from app.ui.header import Header

class MainLayout(QWidget):
    def __init__(self, parent=None, user_name="Admin"):
        super().__init__(parent)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.sidebar = Sidebar(self)
        main_layout.addWidget(self.sidebar)
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        self.header = Header(self, user_name)
        content_layout.addWidget(self.header)
        self.content_stack = QStackedWidget(self)
        content_layout.addWidget(self.content_stack, 1)
        main_layout.addLayout(content_layout, 1) 