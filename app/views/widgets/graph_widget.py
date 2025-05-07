from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QPalette


class Graph(QFrame):
    def __init__(self, title, subtitle=None, color="#3498db", icon=None):
        super().__init__()
        self.setObjectName("graphCard")
        self.setMinimumHeight(200)

        # Set background color if provided
        if color:
            palette = self.palette()
            palette.setColor(QPalette.Window, QColor(color))
            self.setAutoFillBackground(True)
            self.setPalette(palette)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Title row with icon
        title_layout = QHBoxLayout()
        if icon:
            icon_label = QLabel(icon)
            icon_label.setFont(QFont("Segoe UI", 16))
            title_layout.addWidget(icon_label)
        
        titleLabel = QLabel(title)
        titleLabel.setObjectName("graphTitle")
        font = QFont("Segoe UI", 12, QFont.Bold)
        titleLabel.setFont(font)
        title_layout.addWidget(titleLabel)
        title_layout.addStretch()
        layout.addLayout(title_layout)

        # Placeholder for the actual graph
        graphPlaceholder = QLabel("Graph Placeholder")
        graphPlaceholder.setAlignment(Qt.AlignCenter)
        graphPlaceholder.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.1);
            border: 1px dashed rgba(255, 255, 255, 0.3);
            padding: 20px;
            font-size: 14px;
            color: rgba(255, 255, 255, 0.7);
            border-radius: 8px;
        """)
        layout.addWidget(graphPlaceholder)

        # Subtitle and indicators (if applicable)
        if subtitle:
            subtitleLayout = QHBoxLayout()
            subtitleLabel = QLabel(subtitle)
            subtitleLabel.setObjectName("graphSubtitle")
            subtitleLabel.setStyleSheet("color: rgba(255, 255, 255, 0.7); font-size: 13px;")
            subtitleLayout.addWidget(subtitleLabel)
            subtitleLayout.addStretch()

            # Add dynamic indicators
            indicator = QLabel("●")
            valueLabel = QLabel()
            valueLabel.setFont(QFont("Segoe UI", 13))

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

        # Set the frame's style
        self.setStyleSheet("""
            QFrame#graphCard {
                background-color: #ffffff;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
            QFrame#graphCard:hover {
                border: 1px solid #3498db;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
            }
            QLabel#graphTitle {
                color: #2c3e50;
                font-size: 14px;
                font-weight: bold;
            }
            QLabel#graphSubtitle {
                color: #7f8c8d;
                font-size: 13px;
            }
        """)


