from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class Graph(QFrame):
    def __init__(self, title, subtitle=None):
        super().__init__()
        self.setObjectName("graphCard")
        self.setMinimumHeight(200)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Title
        titleLabel = QLabel(title)
        titleLabel.setObjectName("graphTitle")
        font = QFont("Segoe UI", 10, QFont.Bold)
        titleLabel.setFont(font)
        layout.addWidget(titleLabel)

        # Placeholder for the actual graph
        graphPlaceholder = QLabel("Graph Placeholder")
        graphPlaceholder.setAlignment(Qt.AlignCenter)
        graphPlaceholder.setStyleSheet("""
            background-color: #f5f5f5;
            border: 1px dashed #ccc;
            padding: 20px;
            font-size: 12px;
            color: #888;
        """)
        layout.addWidget(graphPlaceholder)

        # Subtitle and indicators (if applicable)
        if subtitle:
            subtitleLayout = QHBoxLayout()
            subtitleLabel = QLabel(subtitle)
            subtitleLabel.setObjectName("graphSubtitle")
            subtitleLabel.setStyleSheet("color: #7f8c8d; font-size: 11px;")
            subtitleLayout.addWidget(subtitleLabel)
            subtitleLayout.addStretch()

            # Add dynamic indicators
            indicator = QLabel("●")
            valueLabel = QLabel()

            if title == "Sales Trend":
                indicator.setStyleSheet("color: #27ae60;")
                valueLabel.setText("+15%")
            elif title == "Stock Levels":
                indicator.setStyleSheet("color: #e67e22;")
                valueLabel.setText("2 Stock Out")
            elif title == "Profit & Loss":
                indicator.setStyleSheet("color: #e74c3c;")
                valueLabel.setText("-$300")

            subtitleLayout.addWidget(indicator)
            subtitleLayout.addWidget(valueLabel)

            layout.addLayout(subtitleLayout)