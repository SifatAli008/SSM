"""
Smart Shop Manager - Action Button
File: views/widgets/action_button.py
"""
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

class ActionButton(QPushButton):
    def __init__(self, text, icon=None, color=None):
        super().__init__(text)
        if icon:
            self.setIcon(QIcon(icon))
        
        if color:
            self.setStyleSheet(f"background-color: {color}; color: white; border: none; padding: 8px;")
        
        self.setCursor(Qt.PointingHandCursor)