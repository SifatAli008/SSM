"""
Smart Shop Manager - Graph Widget
File: views/widgets/graph_widget.py
"""
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class Graph(QFrame):
    def __init__(self, title, subtitle=None):
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setMinimumHeight(180)
        
        layout = QVBoxLayout(self)
        
        titleLabel = QLabel(title)
        titleLabel.setObjectName("graphTitle")
        font = QFont()
        font.setBold(True)
        titleLabel.setFont(font)
        layout.addWidget(titleLabel)
        
        # Placeholder for graph
        graphPlaceholder = QLabel("Graph")
        graphPlaceholder.setAlignment(Qt.AlignCenter)
        graphPlaceholder.setStyleSheet("background-color: #f5f5f5; border: 1px dashed #ccc;")
        layout.addWidget(graphPlaceholder)
        
        if subtitle:
            subtitleLayout = QHBoxLayout()
            subtitleLabel = QLabel(subtitle)
            subtitleLabel.setObjectName("graphSubtitle")
            subtitleLayout.addWidget(subtitleLabel)
            subtitleLayout.addStretch()
            
            if title == "Sales Trend":
                indicator = QLabel("●")
                indicator.setStyleSheet("color: #2ecc71;")
                valueLabel = QLabel("+15%")
                subtitleLayout.addWidget(indicator)
                subtitleLayout.addWidget(valueLabel)
            elif title == "Stock Levels":
                indicator = QLabel("●")
                indicator.setStyleSheet("color: #e74c3c;")
                valueLabel = QLabel("2 Stock out")
                subtitleLayout.addWidget(indicator)
                subtitleLayout.addWidget(valueLabel)
            elif title == "Profit & Loss":
                indicator = QLabel("●")
                indicator.setStyleSheet("color: #e74c3c;")
                valueLabel = QLabel("-$300")
                subtitleLayout.addWidget(indicator)
                subtitleLayout.addWidget(valueLabel)
                
            layout.addLayout(subtitleLayout)