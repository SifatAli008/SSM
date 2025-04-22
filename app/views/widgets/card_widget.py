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
        
        # Set background color if provided
        if color:
            palette = self.palette()
            palette.setColor(QPalette.Background, QColor(color))
            self.setAutoFillBackground(True)
            self.setPalette(palette)
        
        layout = QVBoxLayout(self)
        
        # Title layout with optional icon
        titleLayout = QHBoxLayout()
        if icon:
            iconLabel = QLabel()
            iconLabel.setPixmap(QIcon(icon).pixmap(QSize(20, 20)))
            titleLayout.addWidget(iconLabel)
        
        titleLabel = QLabel(title)
        titleLabel.setObjectName("cardTitle")
        titleLayout.addWidget(titleLabel)
        titleLayout.addStretch()
        layout.addLayout(titleLayout)
        
        # Main value
        valueLabel = QLabel(str(value))
        valueLabel.setObjectName("cardValue")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        valueLabel.setFont(font)
        layout.addWidget(valueLabel)
        
        # Optional subtitle
        if subtitle:
            subtitleLabel = QLabel(subtitle)
            subtitleLabel.setObjectName("cardSubtitle")
            font = QFont()
            font.setPointSize(9)
            subtitleLabel.setFont(font)
            layout.addWidget(subtitleLabel)
            
        layout.addStretch()